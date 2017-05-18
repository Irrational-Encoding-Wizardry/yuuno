from yuuno.ipython.features import install

from yuuno.core.settings import settings as _settings
from yuuno.ipython.widgets.applications import diff, compare, inspect, preview, dump, interact



def load_ipython_extension(ipython):
    install.initialize(ipython)


version = (0, 4, 0)
__version__ = ".".join(str(n) for n in version)
__all__ = ["install", "diff", "compare", "inspect", "preview", "dump", "interact"]
