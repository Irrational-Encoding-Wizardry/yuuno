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
from yuuno import Yuuno
from yuuno.vs.utils import get_proxy_or_core, VapourSynthEnvironment

from yuuno.comm.comms import YuunoCommConnection, YuunoCommManager
from yuuno.comm.commands import Command, UpdateCommand
from yuuno.comm.commands import FrameRequestCommand, FrameResponseCommand
from yuuno.comm.commands import OutputRequestCommand, OutputResponseCommand


class CommProtocolHandler(object):

    def __init__(self, extension, comm_manager: YuunoCommManager):
        self.comm_manager = comm_manager
        self.extension = extension

    @property
    def yuuno(self) -> Yuuno:
        return Yuuno.instance()

    def dispatch(self, comm: YuunoCommConnection, command: Command):
        name = command.command_name
        func = getattr(self, "on_%s"%name, lambda _, __:None)
        return func(comm, command)

    def on_update(self, comm: YuunoCommConnection, command: UpdateCommand):
        comm.send(UpdateCommand(self.extension.output_mirror.current_as_changeset(), id=command.id))

    def on_request_output(self, comm: YuunoCommConnection, command: OutputRequestCommand):
        clip = VapourSynthEnvironment.get_global_outputs()[command.output]
        wrapper = self.yuuno.wrap(clip)
        comm.send(OutputResponseCommand.from_clip(command.id, wrapper))

    def on_request_frame(self, comm: YuunoCommConnection, command: FrameRequestCommand):
        clip = VapourSynthEnvironment.get_global_outputs()[command.output]
        wrapper = self.yuuno.wrap(clip)[command.frame]
        comm.send(FrameResponseCommand(command.id, wrapper.to_pil()))
