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
from typing import TYPE_CHECKING
from typing import Optional, Tuple

from PIL.Image import Image, frombuffer, merge

from yuuno.clip import Clip, Frame, Size, RawFormat
from yuuno.utils import future_yield_coro, auto_join, inline_resolved, gather

if TYPE_CHECKING:
    from yuuno.multi_scripts.subprocess.process import Subprocess


class ProxyFrame(Frame):

    clip: str
    frameno: int
    script: 'Subprocess'

    _cached_img: Optional[Image]
    _cached_meta: Optional[Tuple[Size, RawFormat]]
    _cached_raw: Optional[bytes]

    def __init__(self, clip: str, frameno: int, script: 'Subprocess'):
        self.clip = clip
        self.frameno = frameno
        self.script = script

        self._cached_img = None
        self._cached_meta = None
        self._cached_raw = None

    @future_yield_coro
    def _meta(self):
        if self._cached_meta is None:
            self._cached_meta = yield self.script.requester.submit('script/subprocess/results/meta', {
                "id": self.clip,
                "frame": self.frameno
            })
        return self._cached_meta

    def size(self) -> Size:
        return self._meta().result()[0]

    def format(self) -> RawFormat:
        return self._meta().result()[1]

    @future_yield_coro
    def _raw_async(self) -> bytes:
        if self._cached_raw is None:
            with self.script.framebuffer() as buf:
                result = yield self.script.requester.submit('script/subprocess/results/raw', {
                    "id": self.clip,
                    "frame": self.frameno
                }, protect=True)
                if isinstance(result, int):
                    self._cached_raw = bytes(buf[:result])
                else:
                    # We got the actual object pickled.
                    # This means we are dealing with extremely huge frames
                    self._cached_raw = result
        return self._cached_raw

    def to_raw(self) -> bytes:
        return self._raw_async().result()

    @auto_join
    @future_yield_coro
    def to_pil(self):
        if self._cached_img is not None:
            return self._cached_img

        size, format, raw = yield self.get_raw_data_async()
        raw = memoryview(raw)

        index = 0
        planes = []
        for i in range(format.num_planes):
            plane = self.plane_size(i)
            planedata = raw[index:index+plane]
            planes.append(frombuffer('L', size, planedata, 'raw', "L", 0, 1))
            index += plane

        pil_format = "RGB"
        if format.num_planes == 4:
            pil_format += "A"
        return merge(pil_format, planes)

    @future_yield_coro
    def get_raw_data_async(self) -> Tuple[Size, RawFormat, bytes]:
        m, raw = yield gather([self._meta(), self._raw_async()])
        return m[0], m[1], raw


class ProxyClip(Clip):

    script: 'Subprocess'
    length: int

    def __init__(self, clip: str, length: int, script: 'Subprocess'):
        super(ProxyClip, self).__init__(clip)
        self.script = script
        self.length = length

    def __len__(self):
        return self.length

    @inline_resolved
    def __getitem__(self, item):
        if item >= len(self):
            raise IndexError("The clip does not have as many frames.")
        return ProxyFrame(clip=self.clip, frameno=item, script=self.script)
