from yuuno.formatters import inlines
from yuuno.glue import convert_clip
from yuuno import inspection
from yuuno import magic as cellmagic
from yuuno.widgets.applications import diff, compare, inspect, preview, dump, interact



def install(*, inspections=True, inline=True, magic=True):
    """
    Installs yuuno into the current notebook.

    :param inspections: Set to false if you want to skip the inspections. (pre R36)
    :param inline:      Set to false if you want to skip the inline preview generation.
    :param magic:       Set to false if you want to remove the cell-magic.
    """
    if inspections:
        inspection.install()
    if inline:
        inlines.install()
    if magic:
        cellmagic.install()
    

__all__ = ["install", "convert_clip",  "diff", "compare", "inspect", "preview", "dump", "interact"]
