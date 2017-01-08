from yuuno.formatters import inlines
from yuuno.glue import convert_clip
import yuuno.inspection as inspection


def install(*, inspections=True, inline=True):
    if inspections:
        inspection.install()
    if inline:
        inlines.install()
    

__all__ = ["install", "convert_clip"]
