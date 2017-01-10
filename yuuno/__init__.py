from yuuno.formatters import inlines
from yuuno.glue import convert_clip
from yuuno import inspection
from yuuno import magic as cellmagic
from yuuno.widgets.applications import diff, compare, inspect, preview, dump, interact


def install(*, inspections=True, inline=True, magic=True):
    if inspections:
        inspection.install()
    if inline:
        inlines.install()
    if magic:
        cellmagic.install()
    

__all__ = ["install", "convert_clip",  "diff", "compare", "inspect", "preview", "dump", "interact"]
