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
from typing import Dict, Optional, Iterator, TYPE_CHECKING

from yuuno.core.extension import Extension
if TYPE_CHECKING:
    from yuuno.multi_scripts.script import ScriptManager
    from yuuno.multi_scripts.subprocess.provider import ScriptProviderRegistration


class MultiScriptExtension(Extension):

    _name = "MultiScript"
    managers: Dict[str, 'ScriptManager']
    providers: Dict[str, 'ScriptProviderRegistration']

    @classmethod
    def is_supported(self):
        return True

    def __init__(self, *args, **kwargs):
        super(MultiScriptExtension, self).__init__(*args, **kwargs)
        self.managers = {}
        self.providers = {}

    def initialize(self):
        pass

    def register_manager(self, name: str, manager: 'ScriptManager'):
        """
        Registers a new manager.

        :param name:     The name of the manager.
        :param manager:  The manager to register.
        :return: The registered manager.
        """
        if name in self.managers:
            raise ValueError("A manager with this name already exists.")
        self.managers[name] = manager

    def get_manager(self, name: str) -> Optional['ScriptManager']:
        """
        Returns the manager with the givern name.
        :param name:  The name of the manager.
        :return:      The manager that has been registered with this name.
        """
        return self.managers.get(name, None)

    def get_manager_names(self) -> Iterator[str]:
        """
        Returns all currently registered managers.

        :return: The currently registered manager.
        """
        yield from self.managers.keys()

    def register_provider(self, name: str, registration: 'ScriptProviderRegistration') -> None:
        """
        Register a new provider.

        :param name:          The name of the provider.
        :param registration:  The registration.
        """
        if name in self.providers:
            raise ValueError("A provider with this name has already been registered.")
        self.providers[name] = registration

    def get_provider(self, name: str) -> Optional['ScriptProviderRegistration']:
        """
        Get the provider with the given name.

        :param name: The name of the provider.
        :return: The registration-information.
        """
        return self.providers.get(name, None)

    def get_provider_names(self) -> Iterator[str]:
        """
        Returns the name of all provider.
        :return: The provider
        """
        yield from self.providers.keys()

    def deinitialize(self):
        for manager in self.managers.values():
            manager.dispose_all()
        self.managers = {}
        self.providers = {}
