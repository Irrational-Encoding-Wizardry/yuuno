from typing import List as TList, Callable as TCallable, Dict as TDict
from typing import Any as TAny, AnyStr
from typing import Iterator, Tuple as TTuple

from traitlets import HasTraits, default
from traitlets import List, Dict
from traitlets import Unicode, Any

from yuuno.trait_types import Callable


class Namespace(HasTraits):
    """
    Essentially a view of the current variables
    pushed to the user namespace.
    """

    watchers: TList[TCallable[[AnyStr, TAny, TAny], None]] = List(Callable())

    namespace: TDict[AnyStr, TAny] = Dict(key_trait=Unicode(), value_trait= Any())

    # Sentinel object
    Undefined: object = object()

    @default("watchers")
    def _watchers_default(self):
        return []

    @default("namespace")
    def _namespace_default(self):
        return {}

    def watch(self, callback: TCallable[[AnyStr, TAny, TAny], None]) -> None:
        """
        Register a new callback that pushes or undefines the object
        from the actual environmental namespace.

        :param callback:   The callback to run
        """
        self.watchers.append(callback)

    def unwatch(self, callback: TCallable[[AnyStr, TAny, TAny], None]) -> None:
        """
        Unregister a given callback

        :param callback: The callback to unregister
        """
        self.watchers.remove(callback)

    def _notify(self, key: AnyStr, value: TAny, old: TAny):
        for watcher in self.watchers:
            watcher(key, value, old)

    def as_dict(self) -> TDict[AnyStr, TAny]:
        return self.namespace.copy()

    def items(self) -> Iterator[TTuple[AnyStr, TAny]]:
        return self.namespace.items()

    def __iter__(self):
        return iter(self.namespace)

    def __getitem__(self, item: AnyStr) -> TAny:
        return self.namespace[item]

    def __setitem__(self, key: AnyStr, value: TAny):
        old = self.namespace.get(key, self.Undefined)
        self.namespace[key] = value
        self._notify(key, value, old)

    def __delitem__(self, key: AnyStr):
        old = self.namespace.pop(key)
        self._notify(key, self.Undefined, old)
