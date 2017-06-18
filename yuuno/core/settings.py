from typing import Any as All

from traitlets.utils.importstring import import_item
from traitlets.config import SingletonConfigurable

from traitlets import Any
from traitlets import default, observe
from traitlets import DottedObjectName, List


class Settings(SingletonConfigurable):
    """
    Stores the settings for the registry
    """
    DEFAULT_EXTENSION_TYPES = [
        "yuuno.vs.extension.VapourSynth"
    ]

    registry_type: str = DottedObjectName("yuuno.core.registry.Registry", config=True)
    registry = Any()

    extension_types = List(DottedObjectName(), DEFAULT_EXTENSION_TYPES, config=True)

    @observe('registry_type')
    def _reset_registry_on_reset(self, change: dict) -> None:
        self.registry = import_item(change['new'])()

    @default('registry')
    def _auto_registry(self) -> All:
        return import_item(self.registry_type)()
