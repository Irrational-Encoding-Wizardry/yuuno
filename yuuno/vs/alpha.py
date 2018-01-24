# -*- encoding: utf-8 -*-

# Yuuno - IPython + VapourSynth
# Copyright (C) 2018 StuxCrystal (Roland Netzsch <stuxcrystal@encode.moe>)
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
import abc
from collections.abc import Sequence

from yuuno.vs.utils import is_version

class AlphaOutputClipMeta(abc.ABCMeta):
    IS_VS43 = None

    VideoNode = None
    AlphaOutputTuple = None

    def __subclasscheck__(self, subclass):
        if self.IS_VS43 is None:
            import vapoursynth
            self.IS_VS43 = is_version(43)
            self.VideoNode = vapoursynth.VideoNode

            if self.IS_VS43:
                self.AlphaOutputTuple = vapoursynth.AlphaOutputTuple

        if self.IS_VS43:
            return issubclass(self.AlphaOutputTuple, subclass)

        return False

    @classmethod
    def __instancecheck__(self, obj):

        if self.__subclasscheck__(self, type(obj)):
            return True

        if not isinstance(obj, Sequence):
            return False

        if len(obj) != 2:
            return False

        return all(i is None or isinstance(i, self.VideoNode) for i in obj)


class AlphaOutputClip(metaclass=AlphaOutputClipMeta):
    pass

