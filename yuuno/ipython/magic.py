from typing import Type as TType
from typing import Dict as TDict

from traitlets import Dict, Type, Instance
from traitlets import default

from IPython.core.magic import Magics, magic_kinds

from yuuno.ipython.formatter import Feature


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
                del self.magic_manager.magics[kind][key]

        del self.magics[magic]
        self.environment.parent.log.debug(f"Unregistered magics class: {magic}")

    def deinitialize(self):
        for magic in tuple(self.magics.keys()):
            self.unregister_magics(magic)
