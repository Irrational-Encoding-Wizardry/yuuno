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
import functools
import subprocess
from threading import Thread, Lock, Event

from traitlets import Instance, default

from IPython.display import display
from IPython.core.magic import Magics, magics_class
from IPython.core.magic import line_cell_magic, line_magic

from yuuno import Yuuno
from yuuno.vs.utils import get_proxy_or_core, get_environment
from yuuno.multi_scripts.os import popen, interrupt_process

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
    _view_module_version = Unicode('1.1').tag(sync=True)

    current = Integer(0).tag(sync=True)
    length = Integer(1).tag(sync=True)
    terminated = Bool(False).tag(sync=True)

    start_time = Integer(0).tag(sync=True)
    end_time = Integer(0).tag(sync=True)

    _win32 = Bool(sys.platform=="win32").tag(sync=True)

    def __init__(self, *args, kill, process, commandline, **kwargs):
        super().__init__(*args, **kwargs)
        self._lock = Lock()
        self._kill = kill
        self._process = process
        self._commandline = commandline
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
        if content['type'] == "refresh":
            with self._lock:
                self.send({'type': 'write', 'data': ''.join(self._latest_writes), 'target': content['source']})
                self.send({'type': 'refresh_finish', 'data': None, 'target': content['source']})

        elif content['type'] == 'kill':
            self._process.terminate()
            self._kill.set()

        elif content['type'] == "interrupt":
            interrupt_process(self._process)


@magics_class
class EncodeMagic(Magics):
    """
    Encode magics.
    """

    environment: YuunoIPythonEnvironment = Instance(YuunoIPythonEnvironment)

    @default("environment")
    def _default_environment(self):
        return Yuuno.instance().environment

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

    def _state_updater(self, dead, encode, state):
        while not dead.is_set():
            encode.current, encode.length = state
            time.sleep(0.5)
        encode.current, encode.length = state

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
        process = popen(raw if shell else commandline, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=shell)
        encode = EncodeWidget(kill=kill, process=process, commandline=raw)
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
        if not line and not len(_running):
            print("There is no encode running.")
            return
        if not line and len(_running) > 1:
            print("You are running more than one encode. Use the following id to attach to a specific one.")
            print(r"Usage: %reattach [ID]")
            print()
            print("Running Encodes:")
            print("ID\t- Stats")
            for eid, edata in _running.items():
                print(f"{eid} \t- {edata.current}/{edata.length}\t- {edata._commandline[:40]}")
            return
        if not line and len(_running) == 1:
            return next(iter(_running.values()))
        if line not in _running:
            print("Encode was not found.")
            return
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
