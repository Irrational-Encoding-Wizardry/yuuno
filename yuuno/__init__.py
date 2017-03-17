from yuuno.glue import convert_clip
from yuuno.features import install
from yuuno.widgets.applications import diff, compare, inspect, preview, dump, interact


def load_ipython_extension(ipython):
    install.initialize(ipython)


version = (0, 3, "0a2", "dev1")
__version__ = ".".join(str(n) for n in version)
__all__ = ["install", "convert_clip",  "diff", "compare", "inspect", "preview", "dump", "interact"]
