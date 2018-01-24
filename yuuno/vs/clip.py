# -*- encoding: utf-8 -*-

# Yuuno - IPython + VapourSynth
# Copyright (C) 2017 StuxCrystal (Roland Netzsch <stuxcrystal@encode.moe>)
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


import ctypes
from typing import Tuple

from PIL import Image
from traitlets import HasTraits, Instance, observe

import vapoursynth as vs
from vapoursynth import VideoNode, VideoFrame

from yuuno import Yuuno
from yuuno.clip import Clip, Frame
from yuuno.vs.extension import VapourSynth
from yuuno.vs.utils import get_proxy_or_core, is_version
from yuuno.vs.alpha import AlphaOutputClip


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


def extract_plane_r36compat(frame: VideoFrame, planeno: int, *, compat: bool=False) -> Image.Image:
    """
    Extracts the plane using the old VapourSynth API for reading a frame.

    Since we are doing raw memory operations using ctypes, this function has proven to be prone
    to SIGSEGV while developing.

    This code will subseqently be dropped from this codebase when VapourSynth r36 is officially dropped
    with the official release of R39.

    :param frame:   The frame
    :param planeno: The plane number
    :param compat:  Are we dealing with a compat format.
    :return: The extracted image.
    """
    width, height = calculate_size(frame, planeno)
    stride = frame.get_stride(planeno)
    s_plane = height * stride
    buf = (ctypes.c_byte*s_plane).from_address(frame.get_read_ptr(planeno).value)

    if not compat:
        return Image.frombuffer('L', (width, height), buf, "raw", "L", stride, -1)
    else:
        return Image.frombuffer('RGB', (width, height), buf, "raw", "BGRX", stride, -1)


def extract_plane_new(frame: VideoFrame, planeno: int, *, compat: bool=False) -> Image.Image:
    """
    Extracts the plane with the VapourSynth R37+ array-API.

    :param frame:   The frame
    :param planeno: The plane number
    :param compat:  Are we dealing with a compat format.
    :return: The extracted image.
    """
    arr = frame.get_read_array(planeno)
    height, width = arr.shape
    stride = frame.format.bytes_per_sample * width

    if not compat:
        return Image.frombuffer('L', (width, height), bytes(arr), "raw", "L", stride, -1)
    else:
        return Image.frombuffer('RGB', (width, height), bytes(arr), "raw", "BGRX", stride, -1)


def extract_plane(frame: VideoFrame, planeno: int, *, compat: bool=False) -> Image.Image:
    """
    Extracts the plane.

    Will use the new VapourSynth API for extracting the plane that has been added in R37 when available.
    On older systems it will use the more error-prone get_read_ptr-API.

    :param frame:   The frame
    :param planeno: The plane number
    :param compat:  Are we dealing with a compat format.
    :return: The extracted image.
    """
    if is_version(36):
        return extract_plane_new(frame, planeno, compat=compat)
    else:
        return extract_plane_r36compat(frame, planeno, compat=compat)


class VapourSynthFrameWrapper(HasTraits, Frame):

    pil_cache: Image.Image = Instance(Image.Image, allow_none=True)

    frame: VideoFrame = Instance(VideoFrame)
    compat_frame: VideoFrame = Instance(VideoFrame)

    def to_pil(self) -> Image.Image:
        if self.pil_cache is None:
            self.pil_cache = extract_plane(self.compat_frame, 0, compat=True)
        # noinspection PyTypeChecker
        return self.pil_cache


class VapourSynthClipMixin(HasTraits):

    @property
    def extension(self) -> VapourSynth:
        return Yuuno.instance().get_extension(VapourSynth)

    def _wrap_frame(self, frame: VideoFrame) -> VideoNode:
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

    def _to_compat_rgb32(self, clip: VideoNode):
        if clip.format.color_family == vs.YUV:
            clip = self.extension.resize_filter(clip, format=vs.RGB24, matrix_in_s=self.extension.yuv_matrix)

        if clip.format.color_family != vs.RGB or clip.format.bits_per_sample != 8:
            clip = self.extension.resize_filter(clip, format=vs.RGB24)

        return self.extension.resize_filter(clip, format=vs.COMPATBGR32)

    def to_compat_rgb32(self, frame: VideoFrame) -> VideoNode:
        clip = self._wrap_frame(frame)
        return self._to_compat_rgb32(clip)

    def __len__(self):
        return len(self.clip)

    def __getitem__(self, item) -> VapourSynthFrameWrapper:
        frame: VideoFrame = self.clip.get_frame(item)
        compat: VideoNode = self.to_compat_rgb32(frame)

        return VapourSynthFrameWrapper(frame=frame, compat_frame=compat.get_frame(0))


class VapourSynthClip(VapourSynthClipMixin, HasTraits):

    clip: VideoNode = Instance(VideoNode)

    def __init__(self, clip):
        super(VapourSynthClip, self).__init__(clip=clip)


class VapourSynthFrame(VapourSynthClipMixin, HasTraits):

    frame: VideoFrame = Instance(VideoFrame)
    clip: VideoNode = Instance(VideoNode, allow_none=True)

    def __init__(self, frame):
        HasTraits.__init__(self, frame=frame)

    @observe("frame")
    def _frame_observe(self, value):
        self.clip = self._wrap_frame(value['new'])


class VapourSynthAlphaFrameWrapper(HasTraits):
    clip: VapourSynthFrameWrapper = Instance(VapourSynthFrameWrapper)
    alpha: VapourSynthFrameWrapper = Instance(VapourSynthFrameWrapper)

    _cache: Image.Image = Instance(Image.Image, allow_none=True)

    @property
    def color(self):
        return clip[0]

    def to_pil(self):
        if self._cache is None:
            color = self.clip.to_pil()
            alpha = extract_plane(self.alpha.frame, 0)
            color.putalpha(alpha)
            self._cache = color
        return self._cache


class VapourSynthAlphaClip:

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

    def __getitem__(self, item):
        if self.alpha is None:
            return self.clip[item]
        return VapourSynthAlphaFrameWrapper(clip=self.clip[item], alpha=self.alpha[item])