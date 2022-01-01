# -*- encoding: utf-8 -*-

# Yuuno - IPython + VapourSynth
# Copyright (C) 2017,2022 cid-chan (Sarah <cid+yuuno@cid-chan.moe>)
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


from typing import Type as TType
from typing import Dict as TDict

from traitlets import Dict, Type, Instance
from traitlets import default

from IPython.core.magic import Magics, magic_kinds

from yuuno_ipython.ipython.formatter import Feature


class MagicFeature(Feature):

    magics: TDict[TType[Magics], Magics] = Dict(key_traits=Type(Magics), value_traits=Instance(Magics))

    @default("magics")
    def _default_magics(self):
        return {}

    @property
    def magic_manager(self):
        return self.environment.ipython.magics_manager

    def register_magics(self, magic: TType[Magics]) -> None:
        """
        Registers a new magic into the IPython console.

        :param magic: The magics to use.
        """
        instance = magic(shell=self.environment.ipython)

        self.magics[magic] = instance
        self.environment.ipython.register_magics(instance)
        self.environment.parent.log.debug(f"Registered magics class: {magic.__class__}")

    def unregister_magics(self, magic: TType[Magics]) -> None:
        """
        Unregisters the magic-type from IPython.

        Rant: Why the fuck does IPython define it's own unregister function?

        :param magic: The magics-type you wish to deactivate.
        """
        actual_magics = self.magics[magic].magics

        for kind in magic_kinds:
            for key in actual_magics[kind]:
                self.magic_manager.magics[kind].pop(key, None)

        del self.magics[magic]
        self.environment.parent.log.debug(f"Unregistered magics class: {magic}")

    def deinitialize(self):
        for magic in tuple(self.magics.keys()):
            self.unregister_magics(magic)
