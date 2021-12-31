# -*- encoding: utf-8 -*-

# Yuuno - IPython + VapourSynth
# Copyright (C) 2017 cid-chan (Sarah <cid+yuuno@cid-chan.moe>)
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
from typing import List

from traitlets.config import Configurable


class Environment(Configurable):
    """
    Defines the current environment used in Yuuno.
    """

    def additional_extensions(self) -> List[str]:
        """
        Defines additional extensions that should be
        loaded inside the environment
        """
        return []

    def post_extension_load(self) -> None:
        """
        Called directly after extensions have been loaded
        (but not enabled)
        """
        pass

    def initialize(self) -> None:
        """
        Called by yuuno to tell it that yuuno has
        initialized to the point that it can now initialize
        interoperability for the given environment.
        """

    def deinitialize(self) -> None:
        """
        Called by yuuno before it deconfigures itself.
        """
