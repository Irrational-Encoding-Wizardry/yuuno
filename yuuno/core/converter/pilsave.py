"""
Machinery to convert things from PIL-Images to
Bytes
"""
import os
from io import BytesIO

from PIL import Image

from yuuno.core.settings import settings
from yuuno.util import get_data_file


def open_icc(name=None):
    """
    Opens the ICC-Color profile to attach to the file.
    """
    if name is None:
        name = settings.csp

    path = get_data_file(name + '.icc')

    try:
        with open(path, "rb") as f:
            return f.read()
    except IOError as e:
        print(e)
        return b''

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
