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
from typing import Sequence, Type, ClassVar, Optional

from traitlets.config import Configurable


class Extension(Configurable):
    """
    This is an entrypoint for extensions to Yuuno.

    This can be used to add support for new frameservers
    to Yuuno.
    """
    _name: ClassVar[Optional[str]] = None
    
    @classmethod
    def get_name(cls) -> str:
        if cls._name is None:
            return cls.__name__
        return cls._name

    @classmethod
    def is_supported(cls) -> bool:
        """
        Called to check if the extension is supported at all.
        :return: The result of this check.
        """
        return False

    def initialize(self) -> None:
        """
        Called by the Yuuno-singleton so that the extension
        can register its observers.
        """

    def deinitialize(self) -> None:
        """
        Called by the Yuuno-singleton so that the extension
        can clear the environment.
        """
