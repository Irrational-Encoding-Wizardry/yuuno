﻿# -*- encoding: utf-8 -*-

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


from typing import Any as All

from traitlets.utils.importstring import import_item
from traitlets.config import SingletonConfigurable

from traitlets import Any, CInt
from traitlets import default, observe
from traitlets import DottedObjectName, List


class Settings(SingletonConfigurable):
    """
    Stores the settings for the registry
    """
    DEFAULT_EXTENSION_TYPES = [
        "yuuno.vs.extension.VapourSynth",
        "yuuno.ipy_vs.extension.IPythonVapoursynthExtension",
        "yuuno.comm.extension.YuunoKernelCommExtension",
    ]

    registry_type: str = DottedObjectName("yuuno.core.registry.Registry", config=True)
    registry = Any()

    extension_types = List(DottedObjectName(), DEFAULT_EXTENSION_TYPES, config=True)

    @observe('registry_type')
    def _reset_registry_on_reset(self, change: dict) -> None:
        self.registry = import_item(change['new'])()

    @default('registry')
    def _auto_registry(self) -> All:
        return import_item(self.registry_type)()
