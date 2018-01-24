# -*- encoding: utf-8 -*-

# Yuuno - IPython + VapourSynth
# Copyright (C) 2017,2018 StuxCrystal (Roland Netzsch <stuxcrystal@encode.moe>)
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
import types
from typing import AnyStr, Callable

from traitlets.utils.importstring import import_item


def get_proxy_or_core(*, resolve_proxy=False):
    """
    Returns the current core-proxy or a core instance for pre Vapoursynth R37 installations
    :param resolve_proxy: If you have R37 or later, force resolving the proxy object
    :return: A proxy or the actual core.
    """
    try:
        from vapoursynth import core
        if resolve_proxy:
            core = core.core
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


def is_version(version_number):
    core = get_proxy_or_core(resolve_proxy=True)
    return core.version_number() >= version_number


class VapourSynthEnvironment(object):

    def __init__(self):
        self.previous_outputs = {}
        self.old_outputs = None

    @staticmethod
    def get_global_outputs():
        import vapoursynth
        if hasattr(vapoursynth, "get_outputs"):
            return vapoursynth.get_outputs()
        return types.MappingProxyType(vapoursynth._get_output_dict("OutputManager.get_outputs"))

    def _set_outputs(self, output_dict):
        import vapoursynth
        vapoursynth.clear_outputs()
        for k, v in output_dict.items():
            v.set_output(k)

    @property
    def outputs(self):
        if self.old_outputs is None:
            return self.previous_outputs
        return self.get_global_outputs()

    def __enter__(self):
        self.old_outputs = self.get_global_outputs().copy()
        self._set_outputs(self.previous_outputs)

    def __exit__(self, exc, val, tb):
        self.previous_outputs = self.get_global_outputs().copy()
        self._set_outputs(self.old_outputs)
        self.old_outputs = None


