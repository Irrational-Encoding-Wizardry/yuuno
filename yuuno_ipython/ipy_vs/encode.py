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


import io
import sys
import time
import shlex
import queue
import codecs
import signal
import subprocess
from threading import Thread, Lock, Event

from traitlets import Instance, default

from IPython.display import display
from IPython.core.magic import Magics, magics_class
from IPython.core.magic import line_cell_magic

from yuuno import Yuuno
from yuuno.multi_scripts.os import popen, interrupt_process

from yuuno_ipython.ipython.utils import execute_code
from yuuno_ipython.ipython.magic import MagicFeature
from yuuno_ipython.ipython.environment import YuunoIPythonEnvironment

from yuuno_ipython.ipy_vs.vs_feature import VSFeature

from collections import deque

from ipywidgets import DOMWidget
from traitlets import Unicode, Tuple, Integer, Bool


class EncodeWidget(DOMWidget):
    _view_name = Unicode('EncodeWindowWidget').tag(sync=True)
    _view_module = Unicode('@yuuno/jupyter').tag(sync=True)
    _view_module_version = Unicode('1.1').tag(sync=True)

    current = Integer(0).tag(sync=True)
    length = Integer(1).tag(sync=True)
    terminated = Bool(False).tag(sync=True)
    _win32 = Bool(sys.platform=="win32").tag(sync=True)

    def __init__(self, *args, kill, process, **kwargs):
        super().__init__(*args, **kwargs)
        self._lock = Lock()
        self._kill = kill
        self._process = process
        self._latest_writes = deque(maxlen=10000)
        self.on_msg(self._rcv_message)

    def write(self, string):
        string = string.replace("\n", "\r\n")
        if not string:
            return

        with self._lock:
            self._latest_writes.append(string)
        self.send({'type': 'write', 'data': string, 'target': 'broadcast'})

    def _rcv_message(self, _, content, buffer):
        if content['type'] == "refresh":
            with self._lock:
                self.send({'type': 'write', 'data': ''.join(self._latest_writes), 'target': content['source']})
                self.send({'type': 'refresh_finish', 'data': None, 'target': content['source']})

        elif content['type'] == 'kill':
            self._kill.set()

        elif content['type'] == "interrupt":
            self._process.send_signal(signal.CTRL_C_EVENT)


@magics_class
class EncodeMagic(Magics):
    """
    Encode magics.
    """

    environment: YuunoIPythonEnvironment = Instance(YuunoIPythonEnvironment)

    @default("environment")
    def _default_environment(self):
        return Yuuno.instance().environment

    def _reader(self, dead: Event, process: subprocess.Popen, pipe_r, term_q, encode):

        while process.poll() is None and not dead.is_set():
            d = pipe_r.read(1)
            if d:
                term_q.put(d)

        if process.poll() is None:
            process.terminate()

        process.stdin.close()
        if not dead.is_set():
            dead.set()

        encode.terminated = True

        d = pipe_r.read()
        if d:
            term_q.put(d)
        term_q.put(b"\n\n[Process Terminated]")
        term_q.put(None)

    def _terminal_writer(self, term_q, encode: EncodeWidget):
        decoder = codecs.getincrementaldecoder(sys.getdefaultencoding())('replace')

        killed = False
        while not killed:
            data = []
            while not term_q.empty():
                raw = term_q.get_nowait()
                if raw is None:
                    killed = True
                    break
                data.append(raw)
            data = b''.join(data)
            if not data:
                time.sleep(0.1)
            encode.write(decoder.decode(data))
        encode.write(decoder.decode(b'', final=True))

    def _state_updater(self, dead, encode, state):
        while not dead.is_set():
            encode.current, encode.length = state
            time.sleep(0.5)
        encode.current, encode.length = state

    def _clip_output(self, clip, dead, encode, stdin, state, y4m):
        def _progress(current, length):
            state[0], state[1] = current, length
        try:
            clip.output(stdin, y4m=y4m, progress_update=_progress)
        except Exception as e:
            if dead.is_set():
                return
            raise e
        stdin.close()

    def begin_encode(self, clip, commandline, stdout=None, **kwargs):
        """
        Implements the actual encoding process

        :param clip:        The clip to encode.
        :param commandline: The command to execute
        :param stdout:      Where to send the stdout.
        :return:            The return code.
        """
        kill = Event()
        state = [0, len(clip)]
        process = popen(commandline, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1)
        encode = EncodeWidget(kill=kill, process=process)
        commandline = shlex.split(commandline)

        q = queue.Queue()
        Thread(target=self._reader, args=(kill, process, process.stdout, q, encode), daemon=True).start()
        Thread(target=self._terminal_writer, args=(q, encode), daemon=True).start()
        Thread(target=self._clip_output, args=(clip, kill, encode, process.stdin, state, kwargs.get("y4m", False))).start()
        Thread(target=self._state_updater, args=(kill, encode, state), daemon=True).start()

        return encode

    def prepare_encode(self, line, cell, stdout=None):
        if cell is None:
            cell, line = line.split(" ", 1)

        y4m = False
        progress = True

        # Switch to Argparse if this gets more complicated
        while True:
            if line.startswith("--y4m"):
                y4m = True
                line = line[6:]
            elif line.startswith("--no-progress"):
                progress = False
                line = line[14:]
            else:
                break

        commandline = self.environment.ipython.var_expand(line)
        clip = execute_code(cell, '<yuuno:encode>')
        return self.begin_encode(clip, commandline, stdout=stdout, y4m=y4m, with_progress=progress)

    @line_cell_magic
    def encode(self, line, cell=None):
        """
        Encodes the video directly displaying the output.
        :param line:  The line
        :param cell:  The cell
        :return: The result-code
        """
        return self.prepare_encode(line, cell)

    @line_cell_magic
    def render(self, line, cell=None):
        """
        Renders the video into a bytes-io buffer.
        :param line: The line
        :param cell: The cell
        :return: The IO.
        """
        res = io.BytesIO()
        self.prepare_encode(line, cell, stdout=res)
        return res


class Encode(VSFeature, MagicFeature):

    def initialize(self):
        self.register_magics(EncodeMagic)
