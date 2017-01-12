import ctypes
import functools
from io import BytesIO

# noinspection PyUnresolvedReferences
from PIL import Image
import vapoursynth as vs

from yuuno.vendor import mvsfunc


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


def get_plane_fast(frame: vs.VideoFrame, planeno: int) -> Image.Image:
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
    buf = (ctypes.c_byte*s_plane)()
    ctypes.memmove(buf, frame.get_read_ptr(planeno), s_plane)
    return Image.frombytes('L', (width, height), bytes(buf), "raw", "L", stride, 1)


def get_plane_slow(frame: vs.VideoFrame, planeno: int) -> Image.Image:
    """
    Returns a plane as an PIL image

    :param frame:    The frame.
    :param planeno:  The plane number.
    :return: A grayscale-image with the given plane.
    """
    width, height = retrieve_size(frame, planeno)

    array = frame.get_read_array(planeno)
    buffer = bytearray(len(array)*len(array[0]))
    assert len(array) > 0
    for stride_no, stride in enumerate(array):
        buffer[stride_no * len(stride):(stride_no + 1) * len(stride)] = stride
    return Image.frombytes('L', (width, height), bytes(buffer), "raw", "L", len(stride), 1)


def convert_frame(frame: vs.VideoFrame) -> Image.Image:
    """
    Converts all planes of a frame to an image.
    :param frame:
    :param frameno:
    :return:
    """
    return Image.merge("RGB", tuple(map(
        functools.partial(get_plane_fast, frame),
        range(frame.format.num_planes)
    )))


def ensure_rgb24(clip: vs.VideoNode, *, matrix="709") -> vs.VideoNode:
    """
    Converts the clip to a RGB24 colorspace
    :param clip:
    :param matrix:
    :return:
    """
    core = vs.get_core()

    if clip.format.color_family != vs.RGB:
        clip = mvsfunc.ToRGB(clip, matrix=matrix)

    if clip.format.bits_per_sample != 8:
        clip = core.fmtc.bitdepth(clip, bits=8)

    return clip


def convert_clip(clip: vs.VideoNode, *, frame_no=0, matrix="709") -> Image.Image:
    """
    Converts a clip to an image with the given frame with the given matrix.

    :param clip:
    :param frame_no:
    :param matrix:
    :return:
    """
    if clip.format.color_family == vs.YUV:
        return
    else:
        rgbclip = ensure_rgb24(clip, matrix=matrix)
        return convert_frame(rgbclip.get_frame(frame_no))


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
    im.save(f, format="png")
    return f.getvalue()


def image_to_clip(im: Image.Image, *args, **kwargs) -> vs.VideoNode:
    """
    Converts an Image to a VideoNode.

    This function will create a
    :param im:
    :param args: The args passed to the BlankClip-Operator
    :param args: The kwargs passed to the BlankClip-Operator
    :return:
    """