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
import base64
from typing import Any as TAny

from ipywidgets import DOMWidget

from traitlets import default, directional_link, observe
from traitlets import Any
from traitlets import Integer, Unicode, Float

from yuuno import Yuuno
from yuuno.clip import Clip, RawFormat
from yuuno.utils import future_yield_coro

from yuuno.net.base import Connection
from yuuno.net.handler import ClipHandler
from yuuno.net.multiplexer import ConnectionMultiplexer


EMPTY_IMAGE = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAACklEQVR4nGMAAQAABQABDQottAAAAABJRU5ErkJggg=="
)


class WidgetConnection(Connection):

    def __init__(self, widget: DOMWidget):
        super().__init__()
        self.widget = widget
        self.widget.on_msg(self._receive)

    def send(self, data, binaries):
        self.widget.send(data, binaries)

    def _receive(self, _, data, binaries):
        self.receive(data, binaries)


class Preview(DOMWidget):
    """
    Implements a preview widget

    .. automethod:: __init__
    """
    _view_name = Unicode('PreviewWindowWidget').tag(sync=True)
    _view_module = Unicode('@yuuno/jupyter').tag(sync=True)
    _view_module_version = Unicode('1.2').tag(sync=True)

    # Ignore the changes
    clip: Clip = Any().tag(sync=True, to_json=(lambda v,w: id(v) if v is not None else None), from_json=(lambda v, w: w.clip))
    diff: Clip = Any().tag(sync=True, to_json=(lambda v,w: id(v) if v is not None else None), from_json=(lambda v, w: w.diff))

    frame = Integer(0).tag(sync=True)
    zoom = Float(1.0).tag(sync=True)

    def __init__(self, clip, **kwargs):
        self._connection = ConnectionMultiplexer(WidgetConnection(self))
        self._c1 = self._connection.register("clip")
        self._c2 = self._connection.register("diff")

        super(Preview, self).__init__(**kwargs, clip=clip)

    @observe("clip")
    def _observe__clip(self, change):
        yuuno = Yuuno.instance()
        self._c1.receive = lambda a, b: None

        clip = change['new']
        if clip is None:
            return
            
        elif not isinstance(clip, Clip):
            clip = yuuno.wrap(clip)

        ClipHandler(self._c1, clip, yuuno)

    @observe("diff")
    def _observe__diff(self, change):
        yuuno = Yuuno.instance()
        self._c2.receive = lambda a, b: None

        clip = change['new']
        if clip is None:
            return
            
        elif not isinstance(clip, Clip):
            clip = yuuno.wrap(clip)

        ClipHandler(self._c2, clip, yuuno)

    def _wrap_for(self, target):
        if target is None:
            return None

        elif not isinstance(target, Clip):
            target = Yuuno.instance().wrap(target)
        return target
