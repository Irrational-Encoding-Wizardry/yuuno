import ctypes
from typing import Tuple

from PIL import Image
from traitlets import HasTraits, Instance, observe

import vapoursynth as vs
from vapoursynth import VideoNode, VideoFrame

from yuuno import Yuuno
from yuuno.clip import Clip, Frame
from yuuno.vs.extension import VapourSynth
from yuuno.vs.utils import get_proxy_or_core


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
    if get_proxy_or_core().version_number() > 36:
        return extract_plane_new(frame, planeno, compat=compat)
    else:
        return extract_plane_r36compat(frame, planeno, compat=compat)


class VapourSynthFrameWrapper(HasTraits, Frame):

    frame: VideoFrame = Instance(VideoFrame)
    compat_frame: VideoFrame = Instance(VideoFrame)

    def to_pil(self) -> Image.Image:
        return extract_plane(self.compat_frame, 0, compat=True)


class VapourSynthClipMixin(HasTraits):

    @property
    def extension(self) -> VapourSynth:
        return Yuuno.instance().get_extension(VapourSynth)

    def _to_compat_rgb32(self):
        clip: VideoNode = self.clip

        if clip.format.color_family == vs.YUV:
            clip = self.extension.resize_filter(clip, format=vs.RGB24, matrix_in_s=self.extension.yuv_matrix)

        if clip.format.color_family != vs.RGB or clip.format.bits_per_sample != 8:
            clip = self.extension.resize_filter(clip, format=vs.RGB24)

        return self.extension.resize_filter(clip, format=vs.COMPATBGR32)

    def __len__(self):
        return len(self.clip)

    def __getitem__(self, item) -> VapourSynthFrameWrapper:
        frame: VideoNode = self.clip.get_frame(item)
        compat: VideoNode = self._to_compat_rgb32()

        return VapourSynthFrameWrapper(frame=frame, compat_frame=compat.get_frame(item))


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
    def _wrap_frame(self, value):
        val = value["new"]
        core = get_proxy_or_core()

        bc = core.std.BlankClip(
            width=val.width,
            height=val.height,
            length=1,
            fpsnum=1,
            fpsden=1,
            format=val.format.id
        )

        self.clip = bc.std.ModifyFrame([bc], lambda n, f: val.copy())
