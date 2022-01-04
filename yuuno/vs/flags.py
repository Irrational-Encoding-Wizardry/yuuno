# -*- encoding: utf-8 -*-

# Yuuno - IPython + VapourSynth
# Copyright (C) 2018,2022 cid-chan (Sarah <cid+yuuno@cid-chan.moe>)
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


class _flag(int):

    def __new__(cls, val, func=None):
        f = super(_flag, cls).__new__(cls, val)
        f.func = None
        f(func)
        return f

    def __and__(self, other):
        if not isinstance(other, _flag):
            return NotImplemented

        return _flag(int(self) & other, lambda *a, **kwa: (self(*a, **kwa) and other(*a, **kwa)))

    def __or__(self, other):
        if not isinstance(other, _flag):
            return NotImplemented

        return _flag(int(self) | other, lambda *a, **kwa: (self(*a, **kwa) or other(*a, **kwa)))

    def __xor__(self, other):
        if not isinstance(other, _flag):
            return NotImplemented

        return _flag(int(self) ^ other, lambda *a, **kwa: (self(*a, **kwa) == other(*a, **kwa)))

    def __call__(self, *args, **kwargs):
        if self.func is None:
            self.func = args[0]
            return self
        return self.func.__get__(None, Features)(*args, **kwargs)

    def __str__(self):
        return bin(self)

    def __repr__(self):
        return f"<FlagValue: {bin(self)}>"


def flag(idx: int) -> _flag:
    return _flag(1 << idx)


class Features(enum.Flag):
    NOT_SUPPORTED = _flag(0, lambda vs: False)

    @flag(1)
    @staticmethod
    def FUNCTIONS_INTROSPECTABLE(vs: 'vapoursynth'):
        # AT R36
        return hasattr(vs, 'construct_signature')

    @flag(2)
    @staticmethod
    def SUPPORT_CORE_PROXY(vs: 'vapoursynth'):
        # AT R37
        return hasattr(vs, 'core')

    @flag(3)
    @staticmethod
    def EXTRACT_VIA_ARRAY(vs: 'vapoursynth'):
        # AT R37
        return hasattr(vs.VideoNode, 'get_read_array')

    @flag(4)
    @staticmethod
    def EXPORT_OUTPUT_DICT(vs: 'vapoursynth'):
        # AT R39
        return hasattr(vs, 'get_outputs')

    @flag(5)
    @staticmethod
    def SUPPORT_ALPHA_OUTPUT_TUPLE(vs: 'vapoursynth'):
        # AT R43
        return hasattr(vs, 'AlphaOutputTuple')

    @flag(6)
    @staticmethod
    def COMPATBGR_IS_XRGB(vs):
        # AT <=R43 AND DARWIN
        return platform.system() == 'Darwin' and not hasattr(vs, 'Environment')

    @flag(7)
    @staticmethod
    def EXPORT_VSSCRIPT_ENV(vs):
        # AT R44
        return hasattr(vs, 'Environment')

    @flag(8)
    @staticmethod
    def ENVIRONMENT_POLICIES(vs):
        # AT R51
        return hasattr(vs, 'EnvironmentPolicy')

    @flag(9)
    @staticmethod
    def API4(vs):
        # AT R55
        return hasattr(vs, 'AudioNode')

    @flag(10)
    @staticmethod
    def CLOSE_FRAMES(vs):
        return hasattr(vs.VideoFrame, "close")

    def __bool__(self):
        return bool(self.value and self in self.current)

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
