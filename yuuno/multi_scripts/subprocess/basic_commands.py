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
from pathlib import Path
from typing import TYPE_CHECKING

from yuuno.utils import future_yield_coro
from yuuno.multi_scripts.script import Script

if TYPE_CHECKING:
    from yuuno.multi_scripts.subprocess.process import LocalSubprocessEnvironment


class BasicCommands(object):

    script: Script
    env: 'LocalSubprocessEnvironment'

    def __init__(self, script: Script, env: 'LocalSubprocessEnvironment'):
        self.script = script
        self.env = env

    @property
    def commands(self):
        return {
            'script/subprocess/execute': self.execute,
            'script/subprocess/results': self.results,
            'script/subprocess/results/raw': self.frame_data,
            'script/subprocess/results/meta': self.frame_meta
        }

    @future_yield_coro
    def execute(self, type: str, code: str):
        if type == 'path':
            code = Path(code)
        return (yield self.script.execute(code))

    @future_yield_coro
    def results(self):
        outputs = yield self.script.get_results()
        return {
            str(k): len(v)
            for k, v in outputs.items()
        }

    @future_yield_coro
    def frame_meta(self, id: str, frame: int):
        outputs = yield self.script.get_results()
        clip = outputs.get(id, None)
        if clip is None:
            return None
        try:
            frame = yield clip[frame]
        except IndexError:
            return None
        return frame.size(), frame.format()

    @future_yield_coro
    def frame_data(self, id: str, frame: int):
        outputs = yield self.script.get_results()
        clip = outputs.get(id, None)
        if clip is None:
            return None
        try:
            frame = yield clip[frame]
        except IndexError:
            return None
        frame = frame.to_raw()

        from yuuno.multi_scripts.subprocess.process import FRAME_BUFFER_SIZE
        if len(frame) > FRAME_BUFFER_SIZE:
            return frame

        with self.env.framebuffer() as f:
            f[:len(frame)] = frame

        return len(frame)
