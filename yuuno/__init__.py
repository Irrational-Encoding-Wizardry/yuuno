# -*- coding: utf-8 -*-
import sys

__author__ = """stuxcrystal"""
__email__ = 'stuxcrystal@encode.moe'
__version__ = '0.5.0a0'


if sys.version_info < (3, 6):
    raise ImportError(
        "Yuuno now requires Python 3.6."
        "Please make sure you are using this version."
    )


from yuuno.yuuno import Yuuno

__all__ = ["Yuuno"]


try:
    import IPython
except ImportError:
    pass
else:
    from yuuno.ipython.environment import load_ipython_extension
    from yuuno.ipython.environment import unload_ipython_extension

    __all__ += [
        "load_ipython_extension",
        "unload_ipython_extension",
    ]
