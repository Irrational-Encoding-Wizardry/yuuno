"""
This file registers the formatters for the vapoursynth-types.
"""
from IPython import get_ipython
from PIL.Image import Image, new

import vapoursynth as vs
from vapoursynth import VideoProps, VideoNode, Core, Format

from yuuno.glue import convert_clip, image_to_bytes


class _InlineManager(object):
    """
    Manager for Inline-Reprs.
    """

    def __init__(self):
        self.inlines = []

    def register(self, type, format="text/plain"):
        def _wrapper(func):
            self.inlines.append((type, format, func))
            return func
        return _wrapper

    def install(self):
        ipython = get_ipython()
        if ipython is None:
            return

        formatters = get_ipython().display_formatter.formatters
        for type, format, func in self.inlines:
            formatters[format].for_type(type, func)


_converter = convert_clip
def set_converter(converter=lambda clip:convert_clip(clip, frame_no=0)):
    global _converter
    _converter = converter


inlines = _InlineManager()


@inlines.register(VideoNode, format="image/png")
def format_video(video):
    return image_to_bytes(_converter(video, frame_no=0)), {'width': video.width, 'height': video.height, 'unconfined': True}


@inlines.register(Format, format="text/plain")
def format_format(f, p, cycle):
    p.text(str(f))

@inlines.register(VideoProps, format="text/plain")
def format_format(f, p, cycle):
    result = ["VideoProps:"]
    for val in dir(f):
        if val.startswith("__") and val.endswith("__"):
            continue

        result.append("\t%s: %r" % (val, getattr(f, val)))
    p.text("\n".join(result))

@inlines.register(Core, format="image/png")
def format_core(core):
    try:
        return format_video(vs.get_output(0))
    except KeyError:
        return b""


