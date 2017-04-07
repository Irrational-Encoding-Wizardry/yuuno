from yuuno.features import install
from yuuno.widgets.applications import diff, compare, inspect, preview, dump, interact
from yuuno.settings import settings as _settings


def load_ipython_extension(ipython):
    install.initialize(ipython)


version = (0, 3, 4, 2)
__version__ = ".".join(str(n) for n in version)
__all__ = ["install", "diff", "compare", "inspect", "preview", "dump", "interact"]
