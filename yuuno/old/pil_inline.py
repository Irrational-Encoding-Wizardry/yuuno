import vapoursynth as vs
from PIL.Image import Image, new
from vapoursynth import VideoNode, Core, Format
from yuuno.inlinemgr import inlines

from yuuno.old.vsimg import frame2image, image2bytes

inlines.register(Image, format="image/png")(image2bytes)


@inlines.register(VideoNode, format="image/png")
def format_video(video):
    return image2bytes(frame2image(video, frameno=0))

@inlines.register(Format, format="text/plain")
def format_format(f, p, cycle):
    p.text(str(f))

@inlines.register(Core, format="image/png")
def format_core(core):
    try:
        return format_video(vs.get_output(0))
    except KeyError:
        return b""
    
