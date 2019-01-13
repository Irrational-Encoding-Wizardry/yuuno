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

from yuuno.clip import Clip, RawFormat
from yuuno.utils import future_yield_coro
from yuuno import Yuuno


EMPTY_IMAGE = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAACklEQVR4nGMAAQAABQABDQottAAAAABJRU5ErkJggg=="
)


class _Cache(object):

    def __init__(self, source, updater):
        self._cache_obj_id = None
        self._cache_inst = None

        self._cache_source = source
        self._cache_updater = updater

    def _update(self, obj):
        self._cache_obj_id = id(obj)
        self._cache_inst = self._cache_updater(obj)
        return self._cache_inst

    def get(self):
        obj = self._cache_source()
        if self._cache_obj_id != id(obj):
            return self._update(obj)
        return self._cache_inst


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
        super(Preview, self).__init__(**kwargs, clip=clip)

        self._clip_cache  = _Cache(lambda: self.clip, self._wrap_for)
        self._diff_cache = _Cache(lambda: self.diff, self._wrap_for)

        self._handlers = {
            'length': self._handle_request_length,
            'frame': self._handle_request_frame,
            'metadata': self._handle_request_metadata
        }

        self.on_msg(self._request_dispatch)

    def _request_dispatch(self, _, content, buffers):
        type = content.get('type')
        if type not in self._handlers:
            return
        self._handlers[type](_, content, buffers)

    @future_yield_coro
    def _handle_request_metadata(self, _, content, buffers):
        rqid = content.get('id', None)
        try:
            frame = yield self._get_frame_from_request(content)
            if frame is None:
                return

            meta = yield frame.get_metadata()
            format = frame.format()
            meta['$$$format'] = [
                {
                    RawFormat.ColorFamily.GREY: "GRAYSCALE",
                    RawFormat.ColorFamily.RGB:  "RGB",
                    RawFormat.ColorFamily.YUV:  "YUV"
                }[format.family],
                format.bits_per_sample,
                {
                    RawFormat.SampleType.INTEGER: "Integer",
                    RawFormat.SampleType.FLOAT:   "Float"
                }[format.sample_type],
                format.subsampling_w,
                format.subsampling_h
            ]
            self.send({
                'type': 'response',
                'id': rqid,
                'payload': meta
            })

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

    def _handle_request_length(self, _, content, buffers):
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
            target = self._diff_cache
        else:
            target = self._clip_cache
        return target.get()

    def _wrap_for(self, target):
        if target is None:
            return None

        elif not isinstance(target, Clip):
            target = Yuuno.instance().wrap(target)
        return target


    @future_yield_coro
    def _get_frame_from_request(self, content):
        rqid = content.get('id', None)
        wrapped = self._target_for(content)

        if wrapped is None:
            self.send({
                'type': 'response',
                'id': rqid,
                'payload': {
                    'size': [0, 0]
                }
            }, [EMPTY_IMAGE])
            return

        frameno = content.get('payload', {}).get('frame', self.frame)
        if frameno >= len(wrapped):
            frameno = len(wrapped) - 1

        frame = yield wrapped[frameno]
        return frame


    @future_yield_coro
    def _handle_request_frame(self, _, content, buffers):
        rqid = content.get('id', None)
        try:
            frame = yield self._get_frame_from_request(content)
            if frame is None:
                return
                
            data = Yuuno.instance().output.bytes_of(frame)

            self.send({
                'type': 'response',
                'id': rqid,
                'payload': {
                    'size': frame.get_size()
                }
            }, [data])

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