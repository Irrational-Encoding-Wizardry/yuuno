import os
import ctypes
import functools
from io import BytesIO

from PIL import Image
import vapoursynth as vs

from yuuno.settings import settings


def retrieve_size(frame: vs.VideoFrame, planeno: int) -> (int, int):
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


def get_plane_fast(frame: vs.VideoFrame, planeno: int, *, compat=False) -> Image.Image:
    """
    Faster implementation of get_plane.

    Experimental.

    :param frame:    The frame
    :param planeno:  The planeno
    :return: The returned frame.
    """
    width, height = retrieve_size(frame, planeno)
    stride = frame.get_stride(planeno)
    s_plane = height*stride
    buf = (ctypes.c_byte*s_plane).from_address(frame.get_read_ptr(planeno).value)
    
    if not compat:
        return Image.frombuffer('L', (width, height), buf, "raw", "L", stride, 1)
    else:
        return Image.frombuffer('RGB', (width, height), buf, "raw", "BGRX", stride, -1)


def convert_frame(frame: vs.VideoFrame, *, compat=False) -> Image.Image:
    """
    Converts all planes of a frame to an image.
    :param frame:
    :param frameno:
    :return:
    """
    if compat:
        return get_plane_fast(frame, 0, compat=True)
    
    return Image.merge("RGB", tuple(map(
        functools.partial(get_plane_fast, frame),
        range(frame.format.num_planes)
    )))


def ensure_rgb24(clip: vs.VideoNode, *, matrix=None, compat=False) -> vs.VideoNode:
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


def convert_clip(clip: vs.VideoNode, *, frame_no=0, matrix=None, compat=True) -> Image.Image:
    """
    Converts a clip to an image with the given frame with the given matrix.

    :param clip:
    :param frame_no:
    :param matrix:
    :return:
    """
    rgbclip = ensure_rgb24(clip, matrix=matrix, compat=compat)
    return convert_frame(rgbclip.get_frame(frame_no), compat=compat)


def open_icc(name=None):
    """
    Opens the ICC-Color profile to attach to the file.
    """
    if name is None:
        name = settings.csp
    
    this_dir, this_filename = os.path.split(__file__)
    path = os.path.join(this_dir, "data", name+".icc")
    with open(path, "rb") as f:
        return f.read()

def image_to_bytes(im: Image.Image) -> bytes:
    """
    Saves the image as PNG into a bytes object.
    :param im:
    :return:
    """
    if im is None:
        return b""

    f = BytesIO()
    if im.mode not in ("RGB", "1", "L", "P"):
        im = im.convert("RGB")
    im.save(f, format="png", icc_profile=open_icc())
    return f.getvalue()
