# -*- encoding: utf-8 -*-

# Yuuno - IPython + VapourSynth
# Copyright (C) 2017 StuxCrystal
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


from typing import AnyStr, Callable

from traitlets.utils.importstring import import_item


def get_proxy_or_core():
    """
    Returns the current core-proxy or a core instance for pre Vapoursynth R37 installations
    :return: A proxy or the actual core.
    """
    try:
        from vapoursynth import core
    except ImportError:
        from vapoursynth import get_core
        core = get_core()
    return core


def filter_or_import(name: AnyStr) -> Callable:
    """
    Loads the filter from the current core or tries to import the name.

    :param name: The name to load.
    :return:  A callable.
    """
    core = get_proxy_or_core()

    try:
        ns, func = name.split(".", 1)
        return getattr(getattr(core, ns), func)
    except (ValueError, AttributeError):
        return import_item(name)
