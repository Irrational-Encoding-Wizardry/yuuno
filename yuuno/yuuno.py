# -*- coding: utf-8 -*-

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

from typing import Union, Sequence, Type, TypeVar, Optional

from traitlets.utils.importstring import import_item
from traitlets import Instance, List
from traitlets import default

from yuuno.core.environment import Environment
from yuuno.core.extension import Extension
from yuuno.core.namespace import Namespace
from yuuno.core.settings import Settings

from yuuno.output import YuunoImageOutput

T = TypeVar("T")


class Yuuno(Settings):
    """
    Main-instance of Yuuno.
    """

    environment: Environment = Instance(Environment)
    extensions: Sequence[Extension] = List(Instance(Extension))

    output: YuunoImageOutput = Instance(YuunoImageOutput)
    namespace: Namespace = Instance(Namespace)

    @default("output")
    def _default_output(self):
        return YuunoImageOutput(yuuno=self)

    @default("namespace")
    def _default_namespace(self):
        return Namespace()

    def _actual_extensions(self):
        return self.extension_types + self.environment.additional_extensions()

    def _load_extensions(self) -> Sequence[Extension]:
        exts = []
        for extension in self._actual_extensions():
            if callable(extension):
                ext_cls = extension
            else:
                ext_cls = import_item(extension)
            if not ext_cls.is_supported():
                self.log.info(f"Yuuno-Extension {ext_cls.get_name()} reported that it is not supported on this system.")
                continue
            else:
                self.log.debug(f"Yuuno-Extension {ext_cls.get_name()} loaded.")

            exts.append(ext_cls(parent=self))
        return exts

    def _initialize_extensions(self) -> None:
        self.extensions = self._load_extensions()
        self.environment.post_extension_load()

        failed_extensions = []
        for extension in self.extensions:
            try:
                extension.initialize()
            except Exception as e:
                failed_extensions.append(extension)
                import traceback
                traceback.print_exception(type(e), e, e.__traceback__)

            else:
                self.log.debug(f"Yuuno-Extension {extension.get_name()} initialized.")

        for extension in failed_extensions:
            self.extensions.remove(extension)

    def _deinitialize_extensions(self) -> None:
        for extension in reversed(self.extensions):
            extension.deinitialize()

    def get_extension(self, cls: Union[Type[T], str]) -> Optional[T]:
        """
        Returns the loaded extension given by type.
        :param cls:  The class of the object.
        :return: The given extension or None
        """
        for extension in self.extensions:
            if isinstance(cls, str):
                if extension.get_name() == cls:
                    return extension
                continue

            if isinstance(extension, cls):
                return extension
        return None

    def start(self) -> None:
        """
        Initializes essential stuff about Yuuno.
        """
        self._initialize_extensions()
        self.environment.initialize()

    def stop(self) -> None:
        """
        Clears up stuff about yuuno.
        """
        self.environment.deinitialize()
        self._deinitialize_extensions()
        self.clear_instance()

    def wrap(self, obj: object) -> object:
        """
        Create the clip-wrapper for a specific object.
        """
        return self.registry.wrap(obj)
