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
from ipykernel.comm import Comm


from yuuno.comm.commands import Command


class YuunoCommManager(object):
    """
    Manages comm connections
    """

    def __init__(self, extension):
        self.connections = {}
        self.extension = extension
        self.callbacks = []

    def register(self, comm):
        conn = YuunoCommConnection(self, comm)
        self.connections[comm.comm_id] = conn
        return conn

    def unregister(self, comm: Comm):
        del self.connections[comm.comm_id]

    def broadcast(self, msg):
        for conn in self.connections.values():
            conn.send(msg)

    def receive(self, comm, command):
        for callback in self.callbacks:
            callback(comm, command)

    def on_message(self, callback):
        self.callbacks.append(callback)

    def remove_callback(self, callback):
        self.callbacks.remove(callback)

    def close_all(self):
        for conn in tuple(self.connections.values()):
            conn.close()


class YuunoCommConnection(object):
    """
    Handles a signle comm-connection
    """

    def __init__(self, manager: YuunoCommManager, comm: Comm):
        self.manager = manager
        self.comm = comm
        self.comm.on_msg(self._handle_message)
        self.comm.on_close(self._handle_close)
        self.closed = False

    def close(self):
        try:
            self.comm.close()
        finally:
            self._unregister_self()

    def send(self, message: Command):
        raw = message.to_message()
        buffers = raw.pop('_buffers', [])
        self.comm.send({'command': message.command_name, 'data': raw}, buffers=buffers)

    def _unregister_self(self):
        self.manager.unregister(self.comm)
        self.closed = True

    def _handle_message(self, msg):
        content = msg["content"]
        data = content["data"].copy()
        data['_buffers'] = msg['buffers']

        command = Command.parse_msg(data)
        self.manager.receive(self, command)

    def _handle_close(self, msg):
        self._unregister_self()
