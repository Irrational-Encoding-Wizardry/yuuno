import functools
from io import BytesIO

# noinspection PyUnresolvedReferences
from PIL import Image
import vapoursynth as vs

from yuuno.vendor import mvsfunc


def get_plane(frame: vs.VideoFrame, planeno: int) -> Image.Image:
    """
    Returns a plane as an PIL image

    :param frame:    The frame.
    :param planeno:  The plane number.
    :return: A grayscale-image with the given plane.
    """

    width, height = frame.width, frame.height
    array = frame.get_read_array(planeno)
    buffer = bytearray(len(array)*len(array[0]))
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
        functools.partial(get_plane, frame),
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
        # Disable Dithering made by fmtc.bitdepth to make the images comparable.
        clip = core.fmtc.bitdepth(clip, bits=8, dmode=1)

    return clip


def convert_clip(clip: vs.VideoNode, *, frame_no=0, matrix="709") -> Image.Image:
    """
    Converts a clip to an image with the given frame with the given matrix.

    :param clip:
    :param frame_no:
    :param matrix:
    :return:
    """
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
