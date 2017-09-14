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


class YuunoLabKernelExtension(Extension):

    comm_manager: 'yuuno.lab.comms.YuunoCommManager' = Any()

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
    def ipython(self):
        return self.parent.environment.ipython

    @property
    def log(self):
        return self.parent.log

    @property
    def logger(self):
        return self.parent.logger

    def lab_connect(self, comm, msg):
        self.comm_manager.register(comm)

    def initialize(self):
        from yuuno.lab.comms import YuunoCommManager
        self.parent.log.info("Registering Comm-Target")
        self.ipython.kernel.comm_manager.register_target("yuuno.lab", self.lab_connect)

        self.comm_manager = YuunoCommManager(self)

    def deinitialize(self):
        self.comm_manager.close_all()

        self.ipython.kernel.comm_manager.unregister_target("yuuno.lab")
        self.parent.log.info("Unregistered Comm-Target")
