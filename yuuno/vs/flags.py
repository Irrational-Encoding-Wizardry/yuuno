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
import enum
import platform
from operator import or_
from functools import reduce
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import vapoursynth


class classproperty(object):
    __slots__ = ('func',)

    def __init__(self, func):
        self.func = func

    def __get__(self, instance, owner):
        return self.func(owner)


class flag(int):

    def __new__(cls, val, func=None):
        f = super(flag, cls).__new__(cls, val)
        f.func = None
        f(func)
        return f

    def __and__(self, other):
        if not isinstance(other, flag):
            return NotImplemented

        return flag(int(self) & other, lambda *a, **kwa: (self(*a, **kwa) and other(*a, **kwa)))

    def __or__(self, other):
        if not isinstance(other, flag):
            return NotImplemented

        return flag(int(self) | other, lambda *a, **kwa: (self(*a, **kwa) or other(*a, **kwa)))

    def __xor__(self, other):
        if not isinstance(other, flag):
            return NotImplemented

        return flag(int(self) ^ other, lambda *a, **kwa: (self(*a, **kwa) == other(*a, **kwa)))

    def __call__(self, *args, **kwargs):
        if self.func is None:
            self.func = args[0]
            return self
        return self.func.__get__(None, Features)(*args, **kwargs)


class Features(enum.Flag):
    NOT_SUPPORTED = flag(1, lambda vs: False)

    @flag(2)
    @staticmethod
    def FUNCTIONS_INTROSPECTABLE(vs: 'vapoursynth'):
        # AT R36
        return hasattr(vs, 'construct_signature')

    @flag(4)
    @staticmethod
    def SUPPORT_CORE_PROXY(vs: 'vapoursynth'):
        # AT R37
        return hasattr(vs, 'core')

    @flag(8)
    @staticmethod
    def EXTRACT_VIA_ARRAY(vs: 'vapoursynth'):
        # AT R37
        return hasattr(vs.VideoNode, 'get_read_array')

    @flag(16)
    @staticmethod
    def EXPORT_OUTPUT_DICT(vs: 'vapoursynth'):
        # AT R39
        return hasattr(vs, 'get_outputs')

    @flag(32)
    @staticmethod
    def SUPPORT_ALPHA_OUTPUT_TUPLE(vs: 'vapoursynth'):
        # AT R43
        return hasattr(vs, 'AlphaOutputTuple')

    @flag(64)
    @staticmethod
    def COMPATBGR_IS_XRGB(vs):
        # AT <=R43 AND DARWIN
        return platform.system() == 'Darwin' and not hasattr(vs, 'Environment')

    @flag(128)
    @staticmethod
    def EXPORT_VSSCRIPT_ENV(vs):
        # AT R44
        return hasattr(vs, 'Environment')

    @flag(256)
    @staticmethod
    def ENVIRONMENT_POLICIES(vs):
        # AT R51
        return hasattr(vs, 'EnvironmentPolicy')

    def __bool__(self):
        return self.value and self in self.current

    @classproperty
    def current(cls):
        try:
            import vapoursynth
        except ImportError:
            return cls.NOT_SUPPORTED

        cur = reduce(or_, (m for m in cls.__members__.values() if m.value(vapoursynth)))

        # Don't always calculate the current environments.
        cls.current = cur
        return cur
