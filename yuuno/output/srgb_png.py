import struct
from PIL.Image import register_save
from PIL.PngImagePlugin import PngInfo, putchunk, _save


FORMAT_NAME = "png+srgb.yuuno"

# These values are taken from the official PNG specification.
# These values allow older browsers to have sRGB-like color-settings.
GAMA_SRGB = struct.pack('!I', 45455)
CHRM_SRGB = struct.pack("!8I", 31270, 32900, 64000, 33000, 30000, 60000, 15000, 6000)


SRGB_PNGINFO = PngInfo()
SRGB_PNGINFO.add(b"gAMA", GAMA_SRGB)
SRGB_PNGINFO.add(b"cHRM", CHRM_SRGB)


def putchunk_srgb(fp, cid, *data):
    if cid == b"iCCP":
        return putchunk(fp, b'sRGB', b'\3')

    return putchunk(fp, cid, *data)


def save_srgb_png(im, fp, filename, chunk=putchunk_srgb, check=0):
    return _save(im, fp, filename, chunk, check)


register_save(FORMAT_NAME, save_srgb_png)


def srgb() -> dict:
    return {
        "format": FORMAT_NAME,
        "icc_profile": b"\0",
        "pnginfo": SRGB_PNGINFO
    }
