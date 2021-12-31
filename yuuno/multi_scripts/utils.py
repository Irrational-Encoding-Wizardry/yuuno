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
from typing import Callable, Mapping, Generic, TypeVar, Iterator

from types import MappingProxyType

K = TypeVar("K")
S = TypeVar("S")
T = TypeVar("T")


class ConvertingMappingProxy(Mapping[K, T], Generic[K, S, T]):
    converter: Callable[[S], T]
    mapping: Mapping[K, S]

    __slots__ = ['converter', 'mapping']

    def __init__(self, mapping: Mapping[K, S], converter: Callable[[S], T]):
        self.mapping = MappingProxyType(mapping)
        self.converter = converter

    def __getitem__(self, item) -> T:
        return self.converter(self.mapping[item])

    def __len__(self):
        return len(self.mapping)

    def __iter__(self) -> Iterator[T]:
        return (self.converter(v) for v in self.mapping)

    def __contains__(self, item):
        return item in self.mapping
