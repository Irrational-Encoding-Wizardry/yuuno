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


class YuunoCommManager(object):
    """
    Manages comm connections
    """

    def __init__(self, extension):
        self.connections = {}
        self.extension = extension

    def register(self, comm):
        self.connections[comm.comm_id] = comm
        return YuunoCommConnection(self, comm)

    def unregister(self, comm: Comm):
        del self.connections[comm.comm_id]

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

    def _unregister_self(self):
        self.manager.unregister(self.comm)
        self.closed = True

    def _handle_message(self, msg):
        self.comm.send(msg['content']['data'])

    def _handle_close(self, msg):
        self._unregister_self()
