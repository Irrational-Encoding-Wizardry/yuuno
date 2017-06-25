# -*- coding: utf-8 -*-

# Yuuno - IPython + VapourSynth
# Copyright (C) 2017 StuxCrystal
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import sys

__author__ = """stuxcrystal"""
__email__ = 'stuxcrystal@encode.moe'
__version__ = '0.5.0'


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
