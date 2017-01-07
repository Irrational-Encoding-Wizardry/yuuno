from yuuno.inlinemgr import inlines as inlines
from yuuno import vsinspect
from yuuno.display import *
import yuuno.display
import yuuno.pil_inline

def install():
    inlines.install()
    vsinspect.install()
    

__all__ = ["install"] + yuuno.display.__all__
