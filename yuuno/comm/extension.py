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
from traitlets import Any

from yuuno.yuuno import Yuuno
from yuuno.core.extension import Extension


class YuunoKernelCommExtension(Extension):

    comm_manager: 'yuuno.comm.comms.YuunoCommManager' = Any()
    output_mirror: 'yuuno.comm.output_mirror.OutputMirror' = Any()
    handler: 'yuuno.comm.handlers.CommProtocolHandler' = Any()

    @classmethod
    def is_supported(cls):
        try:
            import IPython
        except ImportError:
            return False

        from yuuno.ipython.environment import YuunoIPythonEnvironment
        if not isinstance(Yuuno.instance().environment, YuunoIPythonEnvironment):
            return False

        if not hasattr(IPython.get_ipython(), 'kernel'):
            return False

        return True

    @property
    def ipython(self) -> 'IPython.core.shellapp.InteractiveShellApp':
        return self.parent.environment.ipython

    @property
    def log(self):
        return self.parent.log

    @property
    def logger(self):
        return self.parent.logger

    def lab_connect(self, comm, msg):
        from yuuno.comm.commands import UpdateCommand
        conn = self.comm_manager.register(comm)

    def update_outputs(self):
        from yuuno.comm.commands import UpdateCommand
        change = self.output_mirror.update_mirror()
        self.comm_manager.broadcast(UpdateCommand(change))

    def initialize(self):
        from yuuno.comm.comms import YuunoCommManager
        from yuuno.comm.output_mirror import OutputMirror
        from yuuno.comm.handlers import CommProtocolHandler

        self.parent.log.info("Initializing YuunoLab")
        self.comm_manager = YuunoCommManager(self)
        self.output_mirror = OutputMirror()
        self.handler = CommProtocolHandler(self, self.comm_manager)
        self.comm_manager.on_message(self.handler.dispatch)

        self.parent.log.info("Registering Comm-Target")
        self.ipython.kernel.comm_manager.register_target("yuuno.comm", self.lab_connect)

        self.parent.log.info("Registering cell events")
        self.ipython.events.register('post_run_cell', self.update_outputs)

    def deinitialize(self):
        self.comm_manager.remove_callback(self.handler.dispatch)
        self.comm_manager.close_all()

        self.ipython.events.unregister('post_run_cell', self.update_outputs)
        self.parent.log.info("Unregistering cell events")

        self.ipython.kernel.comm_manager.unregister_target("yuuno.comm")
        self.parent.log.info("Unregistered Comm-Target")
