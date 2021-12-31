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
import ctypes

PyCapsule_GetName = ctypes.pythonapi.PyCapsule_GetName
PyCapsule_GetName.argtypes = [ctypes.py_object]
PyCapsule_GetName.restype = ctypes.c_char_p

PyCapsule_GetPointer = ctypes.pythonapi.PyCapsule_GetPointer
PyCapsule_GetPointer.argtypes = [ctypes.py_object, ctypes.c_char_p]
PyCapsule_GetPointer.restype = ctypes.c_void_p

_CData = ctypes.c_int.mro()[-2]


class CapsulesMeta(type):
    def __new__(cls, name, bases, dict):
        types = {}

        for k in tuple(dict):
            if hasattr(dict[k], "mro") and _CData in dict[k].mro():
                types[k] = dict[k]
                del dict[k]
        dict['_types_'] = types

        return type.__new__(cls, name, bases, dict)


class Capsules(metaclass=CapsulesMeta):
    _module_ = None

    def __init__(self):
        if not hasattr(self._module_, '__pyx_capi__'):
            raise ValueError("Not a cython module.")

        self.module = self._module_
        self.capsules = self._module_.__pyx_capi__
        self._cache = {}

    def _convert(self, name, capsule_ptr):
        return self._types_[name](capsule_ptr)

    def _extract(self, item):
        try:
            capsule = self.capsules[item]
        except KeyError as e:
            raise AttributeError(item) from e

        name = PyCapsule_GetName(capsule)
        return self._convert(item, PyCapsule_GetPointer(capsule, name))

    def __getattr__(self, item):
        if item not in self._cache:
            self._cache[item] = self._extract(item)

        return self._cache[item]