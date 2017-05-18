import ctypes
import functools

import vapoursynth as vs
from PIL import Image

from yuuno.core.converter.manager import converters
from yuuno.core.settings import settings


@converters.register(vs.VideoNode)
class VideoNodeConverter(object):

    def __init__(self, frame):
        self.frame = frame

    def extract(self, **kwargs):
        return self.convert_clip(self.frame, **kwargs)

    @classmethod
    def retrieve_size(cls, frame: vs.VideoFrame, planeno: int) -> (int, int):
        """
        Calculates the size of the plane.
        :param frame:   The frame
        :param planeno: The plane.
        :return: The size of the returned plane.
        """

        width, height = frame.width, frame.height
        if planeno != 0:
            width >>= frame.format.subsampling_w
            height >>= frame.format.subsampling_h
        return width, height

    @classmethod
    def get_plane_fast(cls, frame: vs.VideoFrame, planeno: int, *, compat=False) -> Image.Image:
        """
        Faster implementation of get_plane.

        Experimental.

        :param frame:    The frame
        :param planeno:  The planeno
        :return: The returned frame.
        """
        width, height = cls.retrieve_size(frame, planeno)
        stride = frame.get_stride(planeno)
        s_plane = height*stride
        buf = (ctypes.c_byte*s_plane).from_address(frame.get_read_ptr(planeno).value)
        
        if not compat:
            return Image.frombuffer('L', (width, height), buf, "raw", "L", stride, 1)
        else:
            return Image.frombuffer('RGB', (width, height), buf, "raw", "BGRX", stride, -1)

    @classmethod
    def convert_frame(cls, frame: vs.VideoFrame, *, compat=False) -> Image.Image:
        """
        Converts all planes of a frame to an image.
        :param frame:
        :param frameno:
        :return:
        """
        if compat:
            return cls.get_plane_fast(frame, 0, compat=True)
        
        return Image.merge("RGB", tuple(map(
            functools.partial(cls.get_plane_fast, frame),
            range(frame.format.num_planes)
        )))

    @classmethod
    def ensure_rgb24(cls, clip: vs.VideoNode, *, matrix=None, compat=False) -> vs.VideoNode:
        """
        Converts the clip to a RGB24 colorspace
        :param clip:    The clip to convert
        :param matrix:  The matrix to use when converting from YUV to RGB
        :return: An RGB24-Clip
        """

        if matrix is None:
            matrix = settings.yuv_matrix

        if clip.format.color_family == vs.YUV:           # Matrix on YUV
            clip = clip.resize.Spline36(
                format=vs.RGB24,
                matrix_in_s=matrix
            )
            
        if clip.format.color_family != vs.RGB or clip.format.bits_per_sample != 8:
            clip = clip.resize.Spline36(
                format=vs.RGB24
            )
            
        if compat:
            clip = clip.resize.Spline36(
                format=vs.COMPATBGR32
            )

        return clip

    @classmethod
    def convert_clip(cls, clip: vs.VideoNode, *, frame_no=0, matrix=None, compat=True) -> Image.Image:
        """
        Converts a clip to an image with the given frame with the given matrix.

        :param clip:
        :param frame_no:
        :param matrix:
        :return:
        """
        rgbclip = cls.ensure_rgb24(clip, matrix=matrix, compat=compat)
        return cls.convert_frame(rgbclip.get_frame(frame_no), compat=compat)


@converters.register(vs.VideoFrame)
class VideoFrameConverter(VideoNodeConverter):

    @classmethod
    def get_core(cls):
        if hasattr(vs, "core"):
            return vs.core
        return vs.get_core()

    @classmethod
    def _frame2clip(cls, frame):
        bc = cls.get_core().std.BlankClip(
            width=frame.width,
            height=frame.height,
            length=1,
            fpsnum=1,
            fpsden=1,
            format=frame.format.id
        )

        return bc.std.ModifyFrame([bc], lambda n,f: frame.copy())

    def __init__(self, frame):
        self.frame = self._frame2clip(frame)

    def extract(self, **kwargs):
        # Enforce first frame (since there is only one frame, duh)
        kwargs['frame_no'] = 0
        return super(VideoFrameConverter, self).extract(**kwargs)
