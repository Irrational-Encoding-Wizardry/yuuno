import base64
import ctypes
import functools
import itertools

import vapoursynth
from io import BytesIO
from PIL import Image
from yuuno.vendor import mvsfunc


def get_bytelink(data, format="image/png"):
    return "data:%s;base64,%s"%(format, base64.b64encode(data).decode())


def get_plane(frame, planeno):
    width, height = frame.width, frame.height
    ary = frame.get_read_array(planeno)
    buffer = bytearray(len(ary)*len(ary[0]))
    for stride_no, stride in enumerate(ary):
        buffer[stride_no*len(stride):(stride_no+1)*len(stride)] = stride
    return Image.frombuffer('L', (width, height), buffer, "raw", "L", len(stride), 1)

def frame2image(clip, frameno=0):
    """
    Converts a frame to an image.
    """
    core = vapoursynth.get_core()

    if clip.format.color_family != vapoursynth.RGB:
        clip = mvsfunc.ToRGB(clip)
    clip = mvsfunc.Depth(clip, 8)
    
    # Extract metadata from the clip.
    width, height = clip.width, clip.height
    colorformat = clip.format

    # Extract the frame.
    frame = clip.get_frame(frameno)

    planes = tuple(map(
        functools.partial(get_plane, frame),
        range(colorformat.num_planes)
    ))

    return Image.merge("RGB", planes)


def image2bytes(im):
    f = BytesIO()
    if im.mode not in ("RGB", "1", "L", "P"):
        im = im.convert("RGB")
    im.save(f, format="png")
    return f.getvalue()
