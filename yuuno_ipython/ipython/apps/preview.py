# -*- encoding: utf-8 -*-

# Yuuno - IPython + VapourSynth
# Copyright (C) 2017, 2022 cid-chan (Sarah <cid+yuuno@cid-chan.moe>)
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
import typing as t
from typing import Any as TAny

from ipywidgets import DOMWidget

from traitlets import default, directional_link, observe
from traitlets import Any
from traitlets import Integer, Unicode, Float, Dict

from yuuno.clip import Clip
from yuuno.utils import future_yield_coro
from yuuno import Yuuno


EMPTY_IMAGE = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAACklEQVR4nGMAAQAABQABDQottAAAAABJRU5ErkJggg=="
)


# class _Cache(object):
# 
#     def __init__(self, source, updater):
#         self._cache_obj_id = None
#         self._cache_inst = None
# 
#         self._cache_source = source
#         self._cache_updater = updater
# 
#     def _update(self, obj):
#         self._cache_obj_id = id(obj)
#         self._cache_inst = self._cache_updater(obj)
#         return self._cache_inst
# 
#     def get(self):
#         obj = self._cache_source()
#         if self._cache_obj_id != id(obj):
#             return self._update(obj)
#         return self._cache_inst


class Preview(DOMWidget):
    """
    Implements a preview widget

    .. automethod:: __init__
    """
    _view_name = Unicode('PreviewWindowWidget').tag(sync=True)
    _view_module = Unicode('yuuno-platform').tag(sync=True)
    _view_module_version = Unicode('1.2').tag(sync=True)

    # Ignore the changes
    clips: t.Dict[str, Clip] = Dict(Any()).tag(
        sync=True,
        to_json=lambda d, _: {k: id(v) for k, v in d.items()},
        from_json=lambda _, w: w.clips
    )

    clip: str = Unicode("0", allow_none=True).tag(sync=True)
    diff: str = Unicode(None, allow_none=True).tag(sync=True)

    frame = Integer(0).tag(sync=True)
    zoom = Float(1.0).tag(sync=True)

    def __init__(self, clip, **kwargs):
        super(Preview, self).__init__(**kwargs, clip=clip)

        # self.on_msg(self._handle_request_length)
        # self.on_msg(self._handle_request_frame)
        self.on_msg(self._handle_any_msg)

    def _handle_any_msg(self, _, content, buffers):
        if 'type' not in content:
            return

        op = content['type']
        if op == 'length':
            func = self._handle_request_length
        else:
            func = self._handle_request_frame

    def _handle_request_length(self, _, content, buffers):
        if content.get('type', '') != 'length':
            return

        rqid = content.get('id', None)
        target = self._target_for(content)
        if target is None:
            self.send({
                'type': 'response',
                'id': rqid,
                'payload': {
                    'length': 0
                }
            })
            return

        self.send({
            'type': 'response',
            'id': rqid,
            'payload': {
                'length': len(target)
            },
        })

    def _target_for(self, content):
        if content.get('payload', {}).get('image', 'clip') == "diff":
            target = self.clips.get(self.diff, None)
        else:
            target = self.clips.get(self.clip, None)

        return self._wrap_for(target)

    def _wrap_for(self, target):
        if target is None:
            return None

        elif not isinstance(target, Clip):
            target = Yuuno.instance().wrap(target)
        return target

    @future_yield_coro
    def _handle_request_frame(self, _, content, buffers):
        if content.get('type', '') != 'frame':
            return

        rqid = content.get('id', None)
        wrapped = self._target_for(content)

        if wrapped is None:
            self.send({
                'type': 'response',
                'id': rqid,
                'payload': {
                    'size': [0, 0],
                    'props': {}
                }
            }, [EMPTY_IMAGE])
            return

        frameno = content.get('payload', {}).get('frame', self.frame)
        if frameno >= len(wrapped):
            frameno = len(wrapped) - 1

        try:
            frame = yield wrapped[frameno]
        except Exception as e:
            import traceback
            self.send({
                'type': 'failure',
                'id': rqid,
                'payload': {
                    'message': ''.join(traceback.format_exception(type(e), e, e.__traceback__))
                }
            })
            raise
        data = Yuuno.instance().output.bytes_of(frame.to_pil())
        self.send({
            'type': 'response',
            'id': rqid,
            'payload': {
                'size': frame.size(),
                'props': frame.properties()
            }
        }, [data])

