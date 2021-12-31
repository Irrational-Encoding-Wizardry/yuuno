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
from typing import Dict, Optional, Union
from pathlib import Path
from concurrent.futures import Future

from yuuno.clip import Clip


class Script(object):
    """
    Represents a script.
    """

    @property
    def alive(self) -> bool:
        """
        Checks if the environment is still alive.
        """
        return False

    def initialize(self) -> None:
        """
        Called when the script is going to be
        initialized.

        We need this to find out if script-creation
        is actually costly.
        """

    def dispose(self) -> None:
        """
        Disposes the script.
        """
        raise NotImplementedError

    def get_results(self) -> Future:
        """
        Returns a dictionary with clips
        that represent the results of the script.
        """
        raise NotImplementedError

    def execute(self, code: Union[str, Path]) -> Future:
        """
        Executes the code inside the environment
        """
        raise NotImplementedError


class ScriptManager(object):
    """
    Manages and creates script-environments.
    """

    def create(self, name: str, *, initialize=False) -> Script:
        """
        Creates a new script environment.
        """
        raise NotImplementedError

    def get(self, name: str) -> Optional[Script]:
        """
        Returns the script with the given name.
        """
        raise NotImplementedError

    def dispose_all(self) -> None:
        """
        Disposes all scripts
        """
        raise NotImplementedError

    def disable(self) -> None:
        """
        Disposes all scripts and tries to clean up.
        """
        raise NotImplementedError
