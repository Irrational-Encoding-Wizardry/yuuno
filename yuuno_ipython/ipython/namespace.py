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


from typing import Callable as TCallable
from typing import AnyStr, Any

from traitlets import default

from yuuno.trait_types import Callable
from yuuno.core.namespace import Namespace as YuunoNamespace

from yuuno_ipython.ipython.feature import Feature


class Namespace(Feature):
    """
    Represents the namespace synchronization feature.
    """

    cb: TCallable[[AnyStr, Any], None] = Callable()

    @default("cb")
    def _set_cb_unique(self) -> TCallable[[AnyStr, Any], None]:
        return self.push_value

    def push_value(self, key: AnyStr, value: Any, old: Any) -> None:
        if value is YuunoNamespace.Undefined:
            self.environment.parent.log.debug(f"Popping from user namespace: {key}")
            self.environment.ipython.drop_by_id({key: old})
        else:
            self.environment.parent.log.debug(f"Pushing to user namespace: {key}: {value!r}")
            self.environment.ipython.push({key: value})

    def initialize(self):
        namespace = self.environment.parent.namespace
        namespace.watch(self.cb)
        for key, value in namespace.items():
            self.push_value(key, value, YuunoNamespace.Undefined)

    def deinitialize(self):
        namespace = self.environment.parent.namespace

        for key, value in namespace.items():
            self.push_value(key, YuunoNamespace.Undefined, value)

        namespace.unwatch(self.cb)
