# -*- coding: utf-8 -*-
from typing import Sequence, Type, TypeVar, Optional

from traitlets.utils.importstring import import_item
from traitlets import Instance, List
from traitlets import default

from yuuno.core.environment import Environment
from yuuno.core.extension import Extension
from yuuno.core.namespace import Namespace
from yuuno.core.settings import Settings

from yuuno.pngoutput import PNGOutput

T = TypeVar("T")


class Yuuno(Settings):
    """
    Main-instance of Yuuno.
    """

    environment: Environment = Instance(Environment)
    extensions: Sequence[Type[Extension]] = List(Instance(Extension))

    output: PNGOutput = Instance(PNGOutput)
    namespace: Namespace = Instance(Namespace)

    @default("output")
    def _default_output(self):
        return PNGOutput(yuuno=self)

    @default("namespace")
    def _default_namespace(self):
        return Namespace()

    def _load_extensions(self) -> Sequence[Extension]:
        exts = []
        for extension in self.extension_types:
            ext_cls = import_item(extension)
            if not ext_cls.is_supported():
                self.log.info(f"Yuuno-Extension {ext_cls.__name__} reported that it is not supported on this system.")
                continue

            exts.append(ext_cls(parent=self))
        return exts

    def _initialize_extensions(self) -> None:
        self.extensions = self._load_extensions()
        for extension in self.extensions:
            extension.initialize()

    def _deinitialize_extensions(self) -> None:
        for extension in reversed(self.extensions):
            extension.deinitialize()

    def get_extension(self, cls: Type[T]) -> Optional[T]:
        """
        Returns the loaded extension given by type.
        :param cls:  The class of the object.
        :return: The given extension or None
        """
        for extension in self.extensions:
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
