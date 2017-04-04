"""
This file registers the formatters for the vapoursynth-types.
"""
from IPython import get_ipython

import vapoursynth as vs
from vapoursynth import VideoProps, VideoFrame, VideoNode, Core, Format

from yuuno.core.converter import converters, image_to_bytes


class _InlineManager(object):
    """
    Manager for Inline-Reprs.
    """

    def __init__(self):
        self.inlines = []

    def register(self, type, format="text/plain"):
        def _decorator(func):
            self.inlines.append((type, format, func))
            return func
        return _decorator

    def install(self):
        ipython = get_ipython()
        if ipython is None:
            return

        formatters = get_ipython().display_formatter.formatters
        for type, format, func in self.inlines:
            formatters[format].for_type(type, func)


inlines = _InlineManager()


@inlines.register(VideoNode, format="image/png")
@inlines.register(VideoFrame, format="image/png")
def video_converter(obj):
    img = converters.convert(obj, frame_no=0)
    return image_to_bytes(img), {
        'width': img.width,
        'height': img.height,
        'unconfined': True
    }


@inlines.register(Format, format="text/plain")
def format_format(f, p, cycle):
    p.text(str(f))


@inlines.register(VideoProps, format="text/plain")
def format_format(f, p, cycle):
    result = ["VideoProps:"]
    for k, v in f.items():
        result.append("\t%s: %r" % (k, repr(v)))
    p.text("\n".join(result))


@inlines.register(Core, format="image/png")
def format_core(core):
    try:
        return video_converter(vs.get_output(0))
    except KeyError:
        return b""


