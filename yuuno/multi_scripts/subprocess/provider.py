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
from typing import List, NamedTuple, Optional, TYPE_CHECKING, Dict

from yuuno import Yuuno
if TYPE_CHECKING:
    from yuuno.multi_scripts.script import ScriptManager, Script
    from yuuno.multi_scripts.subprocess.process import LocalSubprocessEnvironment


class ScriptProviderRegistration(NamedTuple):
    providercls: str
    extensions: List[str]

    def with_config(self, **kwargs: str) -> 'ScriptProviderInfo':
        return ScriptProviderInfo(*self, providerparams=kwargs)


class ScriptProviderInfo(NamedTuple):
    providercls: str
    extensions: List[str]
    providerparams: Dict[str, str]


class ScriptProvider(object):
    """
    Provider for single scripts.
    """
    yuuno: Yuuno

    def __init__(self, yuuno: Yuuno, **kwargs: Dict[str, str]):
        self.yuuno = yuuno

    def initialize(self, env: 'LocalSubprocessEnvironment') -> None:
        """
        Called after _all_ extensions have been loaded
        and the system is ready to be loaded.
        """
        pass

    def deinitialize(self) -> None:
        """
        Called when the environment is being disabled.
        """
        pass

    def get_script(self) -> 'Script':
        """
        Returns the script.
        """
        pass


class ManagedScriptProvider(ScriptProvider):

    manager_name: str
    manager: Optional['ScriptManager']

    script: Optional['Script']

    def __init__(self, yuuno: Yuuno, *, manager_name: str, **kwargs: Dict[str, str]):
        super(ManagedScriptProvider, self).__init__(yuuno, **kwargs)
        self.manager_name = manager_name
        self.manager = None
        self.script = None

    def initialize(self, env: 'LocalSubprocessEnvironment') -> None:
        mscr = self.yuuno.get_extension('MultiScript')
        self.manager = mscr.get_manager(self.manager_name)
        if self.manager is None:
            raise ValueError("Unknown Script Manager detected.")
        self.script = self.manager.create('subprocess', initialize=True)

    def get_script(self) -> 'Script':
        return self.script
