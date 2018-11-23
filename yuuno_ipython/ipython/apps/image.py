# -*- encoding: utf-8 -*-

# Yuuno - IPython + VapourSynth
# Copyright (C) 2017 StuxCrystal (Roland Netzsch <stuxcrystal@encode.moe>)
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


import math
import base64

from typing import Optional
from typing import Dict as TDict, List as TList

from ipywidgets import Widget as IPyWidget
from ipywidgets import Layout
from ipywidgets import Box
from ipywidgets import Image as IPyWImage, HTML as IPyWHTML

from traitlets import observe, default
from traitlets import Instance
from traitlets import Bool, Dict, List
from traitlets import CaselessStrEnum

from PIL.Image import Image as PILImage

from yuuno import Yuuno
from yuuno_ipython.ipython.utils import fake_dict
from yuuno_ipython.ipython.apps.mixins import Jinja2Mixin
from yuuno_ipython.ipython.environment import YuunoIPythonEnvironment


class Image(Box, Jinja2Mixin):
    """
    An empty hull of an once mighty class.
    """
    @staticmethod
    def get_bytelink(image: PILImage) -> str:
        return f"data:image/png;base64,{base64.b64encode(Yuuno.instance().output.bytes_of(image)).decode()}"