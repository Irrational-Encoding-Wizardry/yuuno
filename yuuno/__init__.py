from yuuno.inlinemgr import inlines as inlines
from yuuno.display import *
import yuuno.display
import yuuno.pil_inline

install = inlines.install

__all__ = ["install"] + yuuno.display.__all__
