# Yuuno - IPython + VapourSynth
# Copyright (C) 2022 cid-chan (Sarah <cid+yuuno@cid-chan.moe>)
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
from ipywidgets import DOMWidget
from traitlets import Unicode, Any

from yuuno.utils import future_yield_coro
from yuuno.audio import Audio


class AudioWidget(DOMWidget):
    _view_name = Unicode('AudioPlaybackWidget').tag(sync=True)
    _view_module = Unicode('@yuuno/jupyter').tag(sync=True)
    _view_module_version = Unicode('1.2').tag(sync=True)

    clip: Audio = Any().tag(sync=True, to_json=(lambda v,w: id(v) if v is not None else None), from_json=(lambda v, w: w.clip))

    def __init__(self, clip, **kwargs):
        super(AudioWidget, self).__init__(**kwargs, clip=clip)
        self.on_msg(self._handle_request_meta)
        self.on_msg(self._handle_request_render)

    @future_yield_coro
    def _handle_request_render(self, _, content, buffers):
        if content.get("type", "") != "render": return
        rqid = content.get('id', None)
        if "payload" not in content: return
        payload = content["payload"]

        requested_frame = payload.get("frame", None)
        if requested_frame is None:
            self.send({
                "type": "failure",
                "id": rqid,
                "payload": {
                    "data": "Missing argument: Frame."
                }
            })
            return

        try:
            rendered = yield self.clip[int(requested_frame)]

            self.send({
                "type": "response",
                "id": rqid,
                "payload": {
                    "size": len(rendered[0]) // 4
                }
            }, rendered)
        except Exception as e:
            import traceback
            data = traceback.format_exception(type(e), e, e.__traceback__)
            self.send({
                "type": "failure",
                "id": rqid,
                "payload": {
                    "data": data
                }
            })
            return


    def _handle_request_meta(self, _, content, buffers):
        if content.get("type", "") != "meta": return
        rqid = content.get('id', None)

        format = self.clip.format()

        self.send({
            "type": "response",
            "id": rqid,
            "payload": {
                "channel_count": format.channel_count,
                "samples_per_second": format.samples_per_second,
                "frames": format.frames,
                "sample_count": format.sample_count
            }
        })
        
