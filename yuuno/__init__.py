from yuuno.formatters import inlines
from yuuno.glue import convert_clip
import yuuno.inspection as inspection
from yuuno.widgets.applications import diff, compare, inspect, preview, dump


def install(*, inspections=True, inline=True):
    if inspections:
        inspection.install()
    if inline:
        inlines.install()
    

__all__ = ["install", "convert_clip",  "diff", "compare", "inspect", "preview", "dump"]
