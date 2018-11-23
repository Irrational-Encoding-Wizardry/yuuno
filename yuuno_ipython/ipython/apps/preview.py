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


from typing import Any as TAny

from ipywidgets import DOMWidget

from traitlets import default, directional_link, observe
from traitlets import Any
from traitlets import Integer, Unicode, Float

from yuuno.clip import Clip
from yuuno.utils import future_yield_coro
from yuuno import Yuuno


class Preview(DOMWidget):
    """
    Implements a preview widget

    .. automethod:: __init__
    """
    _view_name = Unicode('PreviewWindowWidget').tag(sync=True)
    _view_module = Unicode('@yuuno/jupyter').tag(sync=True)
    _view_module_version = Unicode('1.1').tag(sync=True)

    # Ignore the changes
    clip = Any(Clip).tag(sync=True, to_json=(lambda v,w: id(v)), from_json=(lambda v, w: w.clip))

    frame = Integer(0).tag(sync=True)
    zoom = Float(1.0).tag(sync=True)

    def __init__(self, clip, **kwargs):
        super(Preview, self).__init__(**kwargs, clip=clip)
        self._cache = [0, None]
        self.on_msg(self._handle_request_length)
        self.on_msg(self._handle_request_frame)

    def _handle_request_length(self, _, content, buffers):
        if content.get('type', '') != 'length':
            return

        rqid = content.get('id', None)

        self.send({
            'type': 'response',
            'id': rqid,
            'payload': len(self.clip),
        })

    @property
    def _wrapped_clip(self):
        if self._cache[0] != id(self.clip):
            self._cache = [id(self.clip), Yuuno.instance().wrap(self.clip)]
        return self._cache[1]

    @future_yield_coro
    def _handle_request_frame(self, _, content, buffers):
        if content.get('type', '') != 'frame':
            return

        rqid = content.get('id', None)

        try:
            frame = yield self._wrapped_clip[content.get("payload", None) or self.frame]
        except Exception as e:
            import traceback
            self.send({
                'type': 'failure',
                'id': rqid,
                'payload': traceback.format_exception(type(e), e, e.__traceback__)
            })
            raise
        data = Yuuno.instance().output.bytes_of(frame.to_pil())
        self.send({
            'type': 'response',
            'id': rqid,
            'payload': {
                'size': frame.size()
            }
        }, [data])