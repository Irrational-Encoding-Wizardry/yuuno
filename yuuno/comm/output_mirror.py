# -*- encoding: utf-8 -*-

# Yuuno - IPython + VapourSynth
# Copyright (C) 2017 StuxCrystal (Roland Netzsch <stuxcrystal@encode.moe>)
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
from weakref import ref
from typing import Optional, Dict, List
from collections import namedtuple

from yuuno.vs.utils import VapourSynthEnvironment, get_proxy_or_core


class ChangeSet(namedtuple("_ChangeSet", "changed deleted")):

    @property
    def persist(self) -> Dict[str, List[int]]:
        return {
            'created': self.changed,
            'deleted': self.deleted
        }


class OutputMirror(object):

    def __init__(self):
        self.last_seen_core: Optional[ref] = None
        self.current_output_ids: Dict[int, int] = {}
        self._recreate_mirror()

    def _recreate_mirror(self):
        current_ids = set(self.current_output_ids.keys())

        current_core = get_proxy_or_core(resolve_proxy=True)
        outputs = VapourSynthEnvironment.get_global_outputs()
        self.last_seen_core = ref(current_core)

        self.current_output_ids = {
            index: id(output)
            for index, output in outputs.keys()
        }

        return ChangeSet(list(outputs.keys()), current_ids-outputs.keys())

    def current_as_changeset(self):
        return ChangeSet(list(VapourSynthEnvironment.get_global_outputs().keys()), [])

    def update_mirror(self):
        current_core = get_proxy_or_core(resolve_proxy=True)
        core = self.last_seen_core()

        # Our core expired or we have a new core
        # expire the mirror and recreate it
        if core is None or core is not current_core:
            self._recreate_mirror()

        outputs = VapourSynthEnvironment.get_global_outputs()
        changes = []

        for index, output in outputs.items():
            val = self.current_output_ids.get(index)
            if id(output) != val:
                changes.append(index)
                self.current_output_ids[index] = id(output)

        deleted = list(self.current_output_ids.keys() - outputs.keys())
        for key in deleted:
            del self.current_output_ids[key]

        return ChangeSet(changes, deleted)

    def __getitem__(self, item):
        import vapoursynth
        item = vapoursynth.get_output(item)
        if id(item) != self.current_output_ids[item]:
            return None

        return item
