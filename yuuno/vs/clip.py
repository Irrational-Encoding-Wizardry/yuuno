# -*- encoding: utf-8 -*-

# Yuuno - IPython + VapourSynth
# Copyright (C) 2017,2018 cid-chan (Sarah <cid+yuuno@cid-chan.moe>)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import math
import ctypes
from typing import Tuple, overload
from concurrent.futures import Future

from PIL import Image
from traitlets import HasTraits, Instance, observe

import vapoursynth as vs
from vapoursynth import VideoNode, VideoFrame

from yuuno import Yuuno
from yuuno.utils import future_yield_coro, gather

from yuuno.clip import Clip, Frame, Size, RawFormat
from yuuno.audio import Audio, Format as AudioFormat

from yuuno.vs.extension import VapourSynth
from yuuno.vs.utils import get_proxy_or_core, is_single
from yuuno.vs.flags import Features
from yuuno.vs.alpha import AlphaOutputClip


# On MAC OSX VapourSynth<=R43 is actually returned as XRGB instead of RGBX
COMPAT_PIXEL_FORMAT = "XRGB" if Features.COMPATBGR_IS_XRGB else "BGRX"


def calculate_size(frame: VideoFrame, planeno: int) -> Tuple[int, int]:
    """
    Calculates the size of the plane

    :param frame:    The frame
    :param planeno:  The plane
    :return: (width, height)
    """
    width, height = frame.width, frame.height
    if planeno != 0:
        width >>= frame.format.subsampling_w
        height >>= frame.format.subsampling_h
    return width, height

@overload
def extract_plane_r36compat(frame: VideoFrame, planeno: int, *, compat: bool=False , direction: int = -1, raw=True) -> bytes: pass
@overload
def extract_plane_r36compat(frame: VideoFrame, planeno: int, *, compat: bool=False, direction: int = -1, raw=False) -> Image.Image: pass
def extract_plane_r36compat(frame, planeno, *, compat=False, direction=-1, raw=False):
    """
    Extracts the plane using the old VapourSynth API for reading a frame.

    Since we are doing raw memory operations using ctypes, this function has proven to be prone
    to SIGSEGV while developing.

    This code will subseqently be dropped from this codebase when VapourSynth r36 is officially dropped
    with the official release of R39.

    :param frame:     The frame
    :param planeno:   The plane number
    :param compat:    Are we dealing with a compat format.
    :param direction: -1 bottom to top, 1 top to bottom
    :param raw:       Return bytes instead of an image.
    :return: The extracted image.
    """
    width, height = calculate_size(frame, planeno)
    stride = frame.get_stride(planeno)
    s_plane = height * stride
    buf = (ctypes.c_byte*s_plane).from_address(frame.get_read_ptr(planeno).value)

    if raw:
        return bytes(buf)
    else:
        if not compat:
            return Image.frombuffer('L', (width, height), buf, "raw", "L", stride, direction)
        else:
            return Image.frombuffer('RGB', (width, height), buf, "raw", COMPAT_PIXEL_FORMAT, stride, direction)

@overload
def extract_plane_new(frame: VideoFrame, planeno: int, *, compat: bool=False , direction: int = -1, raw=True) -> bytes: pass
@overload
def extract_plane_new(frame: VideoFrame, planeno: int, *, compat: bool=False, direction: int = -1, raw=False) -> Image.Image: pass
def extract_plane_new(frame, planeno, *, compat=False, direction=-1, raw=False):
    """
    Extracts the plane with the VapourSynth R37+ array-API.

    :param frame:     The frame
    :param planeno:   The plane number
    :param compat:    Are we dealing with a compat format.
    :param direction: -1 bottom to top, 1 top to bottom
    :param raw:       Return bytes instead of an image.
    :return: The extracted image.
    """
    arr = frame.get_read_array(planeno)
    height, width = arr.shape
    stride = frame.format.bytes_per_sample * width

    if raw:
        return bytes(arr)
    else:
        if not compat:
            return Image.frombuffer('L', (width, height), bytes(arr), "raw", "L", stride, direction)
        else:
            return Image.frombuffer('RGB', (width, height), bytes(arr), "raw", COMPAT_PIXEL_FORMAT, stride, direction)


if Features.EXTRACT_VIA_ARRAY:
    extract_plane = extract_plane_new
else:
    extract_plane = extract_plane_r36compat


class VapourSynthFrameWrapper(HasTraits, Frame):

    pil_cache: Image.Image = Instance(Image.Image, allow_none=True)

    frame: VideoFrame = Instance(VideoFrame)
    rgb_frame: VideoFrame = Instance(VideoFrame)
    compat_frame: VideoFrame = Instance(VideoFrame)

    @property
    def extension(self) -> VapourSynth:
        return Yuuno.instance().get_extension(VapourSynth)

    def _extract(self):
        # APIv4 requires manually plane based extraction.
        if self.extension.merge_bands or Features.API4:
            r = extract_plane(self.rgb_frame, 0, compat=False, direction=1)
            g = extract_plane(self.rgb_frame, 1, compat=False, direction=1)
            b = extract_plane(self.rgb_frame, 2, compat=False, direction=1)
            self.pil_cache = Image.merge('RGB', (r, g, b))
        else:
            self.pil_cache = extract_plane(self.compat_frame, 0, compat=True)

    def to_pil(self) -> Image.Image:
        if self.pil_cache is None:
            self._extract()
        # noinspection PyTypeChecker
        return self.pil_cache

    def size(self) -> Size:
        return Size(self.frame.width, self.frame.height)

    def format(self) -> RawFormat:
        if self.extension.raw_force_compat:
            frame = self.rgb_frame
        else:
            frame = self.frame

        ff: vs.Format = frame.format
        samples = RawFormat.SampleType.INTEGER if ff.sample_type==vs.INTEGER else RawFormat.SampleType.FLOAT
        fam = {
            vs.RGB: RawFormat.ColorFamily.RGB,
            vs.GRAY: RawFormat.ColorFamily.GREY,
            vs.YUV: RawFormat.ColorFamily.YUV,
            vs.YCOCG: RawFormat.ColorFamily.YUV
        }[ff.color_family]

        return RawFormat(
            sample_type=samples,
            family=fam,
            num_planes=ff.num_planes,
            subsampling_w=ff.subsampling_w,
            subsampling_h=ff.subsampling_h,
            bits_per_sample=ff.bits_per_sample
        )

    def to_raw(self):
        if self.extension.raw_force_compat:
            frame = self.rgb_frame
        else:
            frame = self.frame

        return b"".join(
            extract_plane(frame, i, compat=False, raw=True)
            for i in range(frame.format.num_planes)
        )


class VapourSynthClipMixin(HasTraits, Clip):

    clip: VideoNode

    @property
    def extension(self) -> VapourSynth:
        return Yuuno.instance().get_extension(VapourSynth)

    @staticmethod
    def _wrap_frame(frame: VideoFrame) -> VideoNode:
        core = get_proxy_or_core()

        bc = core.std.BlankClip(
            width=frame.width,
            height=frame.height,
            length=1,
            fpsnum=1,
            fpsden=1,
            format=frame.format.id
        )

        return bc.std.ModifyFrame([bc], lambda n, f: frame.copy())

    def _to_rgb32(self, clip: VideoNode) -> VideoNode:
        if clip.format.color_family == vs.YUV:
            clip = self.extension.resize_filter(
                clip,
                format=vs.RGB24,
                matrix_in_s=self.extension.yuv_matrix,
                prefer_props=self.extension.prefer_props
            )

        if clip.format.color_family != vs.RGB or clip.format.bits_per_sample != 8:
            clip = self.extension.resize_filter(clip, format=vs.RGB24)

        processor = self.extension.processor
        if processor is not None:
            clip = processor(clip)

        return clip

    def to_rgb32(self, frame: VideoNode) -> VideoNode:
        return self._to_rgb32(frame)

    def to_compat_rgb32(self, frame: VideoNode) -> VideoNode:
        # Skip resizing on APIv4 as COMPATBGR32 does not exist anymore.
        if Features.API4:
            return frame
        return self.extension.resize_filter(frame, format=vs.COMPATBGR32)

    def __len__(self):
        return len(self.clip)

    @future_yield_coro
    def __getitem__(self, item) -> VapourSynthFrameWrapper:
        if not is_single():
            try:
                get_proxy_or_core().std.BlankClip()
            except vs.Error:
                raise RuntimeError("Tried to access clip of a dead core.") from None

        frame = yield self.clip.get_frame_async(item)
        wrapped = self._wrap_frame(frame)
        _rgb24: VideoNode = self.to_rgb32(wrapped)
        rgb24: Future = _rgb24.get_frame_async(0)
        compat: Future = self.to_compat_rgb32(_rgb24).get_frame_async(0)

        (yield gather([rgb24, compat]))
        rgb24_frame, compat_frame = rgb24.result(), compat.result()

        return VapourSynthFrameWrapper(
            frame=frame,
            compat_frame=compat_frame,
            rgb_frame=rgb24_frame
        )


class VapourSynthClip(VapourSynthClipMixin, HasTraits):

    clip: VideoNode = Instance(VideoNode)

    def __init__(self, clip):
        super(VapourSynthClip, self).__init__(clip)


class VapourSynthFrame(VapourSynthClipMixin, HasTraits):

    frame: VideoFrame = Instance(VideoFrame)
    clip: VideoNode = Instance(VideoNode, allow_none=True)

    def __init__(self, frame):
        super(VapourSynthFrame, self).__init__(None)
        self.frame = frame

    @observe("frame")
    def _frame_observe(self, value):
        self.clip = self._wrap_frame(value['new'])


class VapourSynthAlphaFrameWrapper(HasTraits):
    clip: VapourSynthFrameWrapper = Instance(VapourSynthFrameWrapper)
    alpha: VapourSynthFrameWrapper = Instance(VapourSynthFrameWrapper)

    _cache: Image.Image = Instance(Image.Image, allow_none=True)

    @property
    def color(self):
        return self.clip

    def to_pil(self):
        if self._cache is None:
            color = self.clip.to_pil()
            alpha = extract_plane(self.alpha.frame, 0, direction=1)
            color.putalpha(alpha)
            self._cache = color
        return self._cache

    def size(self) -> Size:
        return self.clip.size()

    def format(self) -> RawFormat:
        f = self.clip.format()
        return RawFormat(
            bits_per_sample=f.bits_per_sample,
            family=f.family,
            num_planes=f.num_planes+1,
            subsampling_h=f.subsampling_h,
            subsampling_w=f.subsampling_w,
            sample_type=f.sample_type
        )

    def to_raw(self):
        return b"".join([self.clip.to_raw(), self.alpha.to_raw()])


class VapourSynthAlphaClip(Clip):

    def __init__(self, clip):
        if not isinstance(clip, AlphaOutputClip):
            raise ValueError("Passed non Alpha-Clip into the wrapper")

        self.clip = VapourSynthClip(clip[0])
        if clip[1] is None:
            self.alpha = None
        else:
            self.alpha = VapourSynthClip(clip[1])

    def __len__(self):
        if self.alpha is None:
            return len(self.clip)
        return min(map(len, (self.clip, self.alpha)))

    @future_yield_coro
    def __getitem__(self, item):
        if self.alpha is None:
            return (yield self.clip[item])

        f1 = yield self.clip[item]
        f2 = yield self.alpha[item]
        return VapourSynthAlphaFrameWrapper(clip=f1, alpha=f2)


if Features.API4:
    from yuuno.audio import Audio
    from yuuno.vs.audioop import byteswap, to_float32_le


    COMBINE_FRAME_COUNT = 24


    class VapourSynthAudio(Audio):

        def __init__(self, clip: vs.AudioNode):
            self.clip = clip

        def format(self) -> AudioFormat:
            return AudioFormat(
                channel_count = self.clip.num_channels,
                samples_per_second = self.clip.sample_rate,
                frames = math.ceil(self.clip.num_frames / COMBINE_FRAME_COUNT),
                sample_count = self.clip.num_samples
            )

        def __len__(self):
            return len(self.clip.num_frames)

        @future_yield_coro
        def _single_frame(self, frame: int) -> Future:
            if frame >= self.clip.num_frames:
                return (b"",) * self.clip.num_channels

            rendered = yield self.clip.get_frame_async(frame)
            with rendered:
                if rendered.sample_type == vs.FLOAT:
                    result = []
                    floats = len(rendered[0])

                    data = bytearray(floats * 4)
                    for channel in rendered:
                        memoryview(data).cast("f")[:] = channel
                        result.append(byteswap(data))

                    return tuple(result)

                else:
                    return tuple(
                        to_float32_le(bytes(channel), bits_per_sample=self.clip.bits_per_sample)
                        for channel in rendered
                    )

        @future_yield_coro
        def __getitem__(self, frame: int) -> Future:
            if frame * COMBINE_FRAME_COUNT > self.clip.num_frames:
                raise IndexError("Frame index out of range.")

            many_frames = yield gather([self._single_frame(frame*COMBINE_FRAME_COUNT + i) for i in range(COMBINE_FRAME_COUNT)])
            return tuple(
                b"".join(channel)
                for channel in zip(*many_frames)
            )
