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
from yuuno.output import YuunoImageOutput
from yuuno.comm.output_mirror import ChangeSet


class UnknownCommandException(KeyError): pass


class Command(object):
    COMMAND_CLASSES = {}
    command_name = None

    @classmethod
    def register(cls, name, clazz=None):
        def _decorator(new_cls):
            new_cls.command_name = name
            cls.COMMAND_CLASSES[name] = new_cls
            return new_cls

        if clazz is not None:
            return _decorator(clazz)

        return _decorator

    @classmethod
    def from_message(cls, data):
        return cls(**data)

    @classmethod
    def parse_msg(cls, message):
        type_name = message["command"]
        data = message["data"]

        type = cls.COMMAND_CLASSES.get(type_name)
        if type is None:
            raise UnknownCommandException("Unknown command %s" % type_name)

        return type.from_message(data)

    def to_message(self):
        return {}

    def __repr__(self):
        return "<%s %r>"%(self.__class__.__name__, self.to_message())


@Command.register("update")
class UpdateCommand(Command):

    def __init__(self, change: ChangeSet=None, id=None):
        self.change: ChangeSet = change
        self.id = id

    def to_message(self):
        data = self.change.persist
        data['id'] = self.id
        return data

    @classmethod
    def from_message(cls, data):
        return cls(
            id = data.get('id', None),
            change=ChangeSet(
                changed=data.get('changed', []),
                deleted=data.get('deleted', [])
            )
        )


@Command.register("request_output")
class OutputRequestCommand(Command):

    def __init__(self, id, output):
        self.id = id
        self.output = output

    def to_message(self):
        return {
            'id': self.id,
            'output': self.output
        }


@Command.register("response_output")
class OutputResponseCommand(Command):

    def __init__(self, id, width, height, length):
        self.id = id
        self.width = width
        self.height = height
        self.length = length

    def to_message(self):
        return {
            'id': self.id,
            'size': {
                'width': self.width,
                'height': self.height,
            },
            'length': self.length
        }

    @classmethod
    def from_message(cls, data):
        return OutputResponseCommand(
            data['id'],
            data['size']['width'],
            data['size']['height'],
            data['length']
        )

    @classmethod
    def from_clip(cls, id, clip):
        length = len(clip)
        p = clip[0].to_pil()
        width = p.width
        height = p.height
        return cls(id, width, height, length)


@Command.register("request_frame")
class FrameRequestCommand(Command):

    def __init__(self, id, output, frame):
        self.id = id
        self.output = output
        self.frame = frame

    def to_message(self):
        return {
            'id': self.id,
            'output': self.output,
            'frame': self.frame
        }


@Command.register("response_frame")
class FrameResponseCommand(Command):

    def __init__(self, id, pil_image):
        self.id = id
        self.pil_image = pil_image

    @property
    def output(self) -> YuunoImageOutput:
        return Yuuno.instance().output

    def to_message(self):
        return {
            'id': self.id,
            '_buffers': [
                self.output.bytes_of(self.pil_image)
            ]
        }

    @classmethod
    def from_message(cls, data):
        raise NotImplementedError
