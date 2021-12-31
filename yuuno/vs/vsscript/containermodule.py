# -*- encoding: utf-8 -*-

# Yuuno - IPython + VapourSynth
# Copyright (C) 2018 cid-chan (Sarah <cid+yuuno@cid-chan.moe>)
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
from types import ModuleType
from typing import Callable, Type, MutableMapping, Any, Dict
from collections import ChainMap
from importlib.machinery import ModuleSpec, BuiltinImporter
from sys import modules


def create_module(manager: Callable[[], Dict[str, Any]]) -> Type[ModuleType]:
    def get_dict() -> MutableMapping[str, Any]:
        d = manager()
        return ChainMap(d, {
            '__name__': '__vapoursynth__',
            '__spec__': ModuleSpec(name='__vapoursynth__', loader=BuiltinImporter, origin='yuuno'),
            '__package__': None,
            '__doc__': None
        })

    class _EnvLocalModule(ModuleType):
        """
        The __vapoursynth__-Module has to be backed by a environment backed
        dictionary.
        """

        def __getattribute__(self, item):
            try:
                get_dict()[item]
            except KeyError as e:
                raise AttributeError(item) from e

        def __setattr__(self, key, value):
            nonlocal manager
            get_dict()[key] = value

        def __delattr__(self, item):
            d = get_dict()
            del d[item]

        def __dir__(self):
            nonlocal manager
            return [
                "__dir__",
                "__getattribute__",
                "__setattr__",
                "__delattr__",
                "__repr__"
            ] + list(manager.keys())

        def __repr__(self):
            return "<module '__vapoursynth__' (provided)>"

    modules['__vapoursynth__'] = _EnvLocalModule("__vapoursynth__")
