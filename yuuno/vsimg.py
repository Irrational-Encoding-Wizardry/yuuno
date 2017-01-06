import ctypes
import functools
import itertools

import vapoursynth
from io import BytesIO
from PIL import Image
from yuuno.vendor import mvsfunc


def get_plane(frame, planeno):
    width, height = frame.width, frame.height
    buffer = (ctypes.c_char*(width*height))()
    ctypes.memmove(buffer, frame.get_read_ptr(planeno), width*height)
    return Image.frombuffer('L', (width, height), buffer, "raw", "L", width, 1)


def frame2image(clip, frameno=0):
    """
    Converts a frame to an image.
    """
    core = vapoursynth.get_core()

    # Convert clip to RGB
    if clip.format.color_family != vapoursynth.RGB:
        clip = mvsfunc.ToRGB(clip, compat=1)
    
    # Extract metadata from the clip.
    width, height = clip.width, clip.height
    colorformat = clip.format

    # Extract the frame.
    frame = clip.get_frame(frameno)

    planesize = width*height*colorformat.bytes_per_sample
    buffer = (ctypes.c_char*planesize)()
    ctypes.memmove(buffer, frame.get_read_ptr(0), planesize)

    # Parse the PIL image
    return Image.frombuffer('RGB', (width, height), buffer, "raw", "BGRX", frame.get_stride(0), -1)

def image2bytes(im):
    f = BytesIO()
    im.save(f, format="png")
    return f.getvalue()
