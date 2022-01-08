# -*- encoding: utf-8 -*-

# Yuuno - IPython + VapourSynth
# Copyright (C) 2017 cid-chan (Sarah <cid+yuuno@cid-chan.moe>)
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
from typing import NamedTuple

import sys
import time
import shlex
import queue
import codecs
import random
import subprocess
from threading import Thread, Lock, Event

import jinja2
from traitlets import Instance, default

from IPython.display import display
from IPython.core.magic import Magics, magics_class
from IPython.core.magic import line_cell_magic, line_magic

from yuuno import Yuuno
from yuuno.vs.utils import get_proxy_or_core, get_environment

from yuuno.multi_scripts.os import popen, interrupt_process, kill_process

from yuuno_ipython.utils import get_data_file, log_errors

from yuuno_ipython.ipython.utils import execute_code
from yuuno_ipython.ipython.magic import MagicFeature
from yuuno_ipython.ipython.environment import YuunoIPythonEnvironment

from yuuno_ipython.ipy_vs.vs_feature import VSFeature

from collections import deque

from ipywidgets import DOMWidget
from traitlets import Unicode, Tuple, Integer, Bool


_running = {}


class EncodeWidget(DOMWidget):
    _view_name = Unicode('EncodeWindowWidget').tag(sync=True)
    _view_module = Unicode('@yuuno/jupyter').tag(sync=True)
    _view_module_version = Unicode('1.2').tag(sync=True)

    current = Integer(0).tag(sync=True)
    length = Integer(1).tag(sync=True)
    terminated = Bool(False).tag(sync=True)
    commandline = Unicode("").tag(sync=True)

    start_time = Integer(0).tag(sync=True)
    end_time = Integer(0).tag(sync=True)

    _win32 = Bool(sys.platform=="win32").tag(sync=True)

    def __init__(self, *args, kill, process, commandline, **kwargs):
        super().__init__(*args, **kwargs)
        self._lock = Lock()
        self._kill = kill
        self._process = process
        self._commandline = commandline
        self.commandline = self._commandline
        self._latest_writes = deque(maxlen=10000)
        self.start_time = int(time.time())
        self.on_msg(self._rcv_message)

    def write(self, string):
        string = string.replace("\n", "\r\n")
        if not string:
            return

        with self._lock:
            self._latest_writes.append(string)
        self.send({'type': 'write', 'data': string, 'target': 'broadcast'})

    def join(self, timeout=None):
        self._kill.wait(timeout=timeout)

    def _rcv_message(self, _, content, buffer):
        cid = content.get("id", None)
        if content['type'] == "refresh":
            data = content
            if "payload" in data:
                data = data["payload"]

            with self._lock:
                writes = ''.join(self._latest_writes)
                if cid is not None:
                    self.send({'type': 'response', 'id': cid, 'payload': {"data": writes}})
                self.send({'type': 'write', 'data': writes, 'target': data['source']})
                self.send({'type': 'refresh_finish', 'data': None, 'target': data['source']})

        elif content['type'] == 'kill':
            kill_process(self._process)
            self._kill.set()
            with self._lock:
                self.send({'type': 'response', 'id': cid, 'payload': {}})

        elif content['type'] == "interrupt":
            interrupt_process(self._process)
            with self._lock:
                self.send({'type': 'response', 'id': cid, 'payload': {}})


class _EData(NamedTuple):
    id: str
    command: str
    current: int
    length: int


class EncodeData(object):
    _template_txt = None
    _template_html = None

    @classmethod
    def template_txt(cls):
        if cls._template_txt is None:
            path = get_data_file("txt") / "encodes.txt"
            with open(path, "r") as f:
                cls._template_txt = jinja2.Template(f.read())
        return cls._template_txt

    @classmethod
    def template_html(cls):
        if cls._template_html is None:
            path = get_data_file("html") / "encodes.html"
            with open(path, "r") as f:
                cls._template_html = jinja2.Template(f.read())
        return cls._template_html
        

    @staticmethod
    def _map_value(eid, encoder):
        return _EData(
            str(eid),
            encoder._commandline,
            encoder.current,
            encoder.length
        )

    def __init__(self, current_encodes):
        self.current_encodes = current_encodes.copy()

    def _repr_pretty_(self, p, cycle):
        p.text(self.template_txt().render({
            "encodes": [self._map_value(*i) for i in self.current_encodes.items()]
        }))

    def _repr_html_(self):
        return self.template_html().render({
            "random_id": hex(random.randint(0, 2**32))[2:],
            "encodes": [self._map_value(*i) for i in self.current_encodes.items()]
        })
        


@magics_class
class EncodeMagic(Magics):
    """
    Encode magics.
    """

    environment: YuunoIPythonEnvironment = Instance(YuunoIPythonEnvironment)

    @default("environment")
    def _default_environment(self):
        return Yuuno.instance().environment

    @log_errors
    def _reader(self, dead: Event, process: subprocess.Popen, pipe_r, term_q, encode, after_exit):
        while process.poll() is None and not dead.is_set():
            d = pipe_r.read(1)
            if d:
                term_q.put(d)

        if process.poll() is None:
            process.terminate()

        try:
            process.stdin.close()
        except OSError:
            pass

        if not dead.is_set():
            dead.set()

        encode.end_time = int(time.time())
        encode.terminated = True
        del _running[str(process.pid)]

        d = pipe_r.read()
        if d:
            term_q.put(d)

        if after_exit is not None:
            after_exit()

        term_q.put(b"\n\n[Process Terminated]")
        term_q.put(None)

    @log_errors
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
            if data:
                encode.write(decoder.decode(data))
            time.sleep(0.1)
        encode.write(decoder.decode(b'', final=True))

    @log_errors
    def _state_updater(self, dead, encode, state):
        while not dead.is_set():
            encode.current, encode.length = state
            time.sleep(0.5)
        encode.current, encode.length = state

    @log_errors
    def _clip_output(self, env, clip, dead, encode, stdin, state, y4m):
        def _progress(current, length):
            state[0], state[1] = current, length
        try:
            from yuuno_ipython.ipy_vs.outputter import encode as raw_encode
            with env():
                raw_encode(clip, stdin, y4m=y4m, progress=_progress)

        except Exception as e:
            if dead.is_set():
                return
            encode._process.terminate()
            raise e
        try:
            stdin.close()
        except OSError:
            pass

    def begin_encode(self, clip, commandline, stdout=None, after_exit=None, **kwargs):
        """
        Implements the actual encoding process

        :param clip:        The clip to encode.
        :param commandline: The command to execute
        :param stdout:      Where to send the stdout.
        :return:            The return code.
        """
        raw = commandline
        commandline = shlex.split(commandline)
        shell = kwargs.pop('shell', False)

        kill = Event()
        state = [0, len(clip)]
        process = popen(
            raw if shell else commandline,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,

            shell=shell,
            bufsize=0
        )
        encode = EncodeWidget(kill=kill, process=process, commandline=raw)
        encode.length = len(clip)
        _running[str(process.pid)] = encode

        q = queue.Queue()
        Thread(target=self._reader, args=(kill, process, process.stdout, q, encode, after_exit), daemon=True).start()
        Thread(target=self._terminal_writer, args=(q, encode), daemon=True).start()
        if clip is not None:
            Thread(target=self._clip_output, args=(get_environment(), clip, kill, encode, process.stdin, state, kwargs.get("y4m", False))).start()
        Thread(target=self._state_updater, args=(kill, encode, state), daemon=True).start()

        return encode

    def prepare_encode(self, line, cell, stdout=None):
        if cell is None:
            cell, line = line.split(" ", 1)

        y4m = False
        multi = False

        # Switch to Argparse if this gets more complicated
        while True:
            if line.startswith("--y4m"):
                y4m = True
                line = line[6:]
            elif line.startswith("--no-progress"):
                print("--no-progress has no use anymore and is ignored.")
            elif line.startswith("--multi"):
                multi = True
                line = line[8:]
            else:
                break

        if not multi and len(_running):
            print(r"You are already running an encode. Use %reattach to view the latest encode or use --multi to run multiple instances")
            return

        commandline = self.environment.ipython.var_expand(line)
        clip = execute_code(cell, '<yuuno:encode>')
        encode = self.begin_encode(clip, commandline, stdout=stdout, y4m=y4m)
        return encode

    @line_magic
    def reattach(self, line):
        if not line:
            if len(_running) != 1:
                display(EncodeData(_running))
            else:
                return next(iter(_running.values()))
        elif line not in _running:
            print("Encode was not found.")
        else:
            return _running[line]

    @line_cell_magic
    def encode(self, line, cell=None):
        """
        Encodes the video directly displaying the output.
        :param line:  The line
        :param cell:  The cell
        :return: The result-code
        """
        return self.prepare_encode(line, cell)


class Encode(VSFeature, MagicFeature):

    def initialize(self):
        self.register_magics(EncodeMagic)
