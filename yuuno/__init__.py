# -*- coding: utf-8 -*-

# Yuuno - IPython + VapourSynth
# Copyright (C) 2017,2018 cid-chan (Sarah <cid+yuuno@cid-chan.moe>)
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

__author__ = """cid-chan"""
__email__ = 'cid+yuuno@cid-chan.moe'
__version__ = '1.4'


if sys.version_info < (3, 8):
    raise ImportError(
        "Yuuno requires Python 3.8 or newer"
        "Please make sure you are using this version."
    )

from yuuno.yuuno import Yuuno
from yuuno.autodiscover import discover_environments
from yuuno.standalone import init_standalone

__all__ = ["Yuuno", 'init_standalone'] + discover_environments(vars())
