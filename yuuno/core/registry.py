from traitlets import Type as Class, Dict, List, HasTraits
from traitlets import This
from traitlets import default

from typing import Dict as Dictionary
from typing import List as Listing
from typing import Type, Optional, Callable, Iterator

from yuuno.clip import Clip, T


class Registry(HasTraits):
    """
    Stores which Clip-Type is responsible for wrapping
    specific applications.
    """

    clip_types: Dictionary = Dict(value_trait=Class(klass=Clip), key_trait=Class())
    sub_registries: Listing['Registry'] = List(This())

    @default("clip_types")
    def _init_cliptypes(self) -> Dictionary[Type[Clip], Type[T]]:
        return {}

    @default("sub_registries")
    def _init_subregistries(self) -> Listing['Registry']:
        return []

    def all_types(self) -> Iterator[Type]:
        """
        A generator that returns all supported types.
        """
        yield from self.clip_types.keys()
        for registry in self.sub_registries:
            yield from registry.all_types()

    def add_subregistry(self, registry: 'Registry') -> None:
        """
        Adds a subregistry to the registry.

        These registries can be removed at any time.

        :param registry:  The registry to add
        """
        self.sub_registries.append(registry)

    def remove_subregistry(self, registry: 'Registry') -> None:
        """
        Removes a subregistry from the registry.

        :param registry: The registry to remove.
        """
        self.sub_registries.remove(registry)

    def register(self, base: Type[Clip], type: Type[T]=None) -> Optional[Callable[[Type[Clip]], Type[Clip]]]:
        """
        Registers a new clip type for the given clip.

        :param base:  The clip-type
        :param type:  The type the clip is wrapping. (If omitted it will represent a decorator)
        :return: A decorator or none.
        """

        # Decorator Syntax
        if type is None:
            def _decorator(type: Type[T]) -> Type[T]:
                self.register(type, base)
                return type
            return _decorator

        # Normal handling
        self.clip_types[type] = base

    def get_clip_type_for(self, item: T) -> Optional[Type[Clip]]:
        """
        Returns the clip type for the given object.

        :param item:  The clip to convert.
        :return:  Type clip-type responsible for wrapping the object
        """
        # Find in own first
        for cls in type(item).mro():
            if cls in self.clip_types:
                return self.clip_types[cls]

        # Then find in foreign
        for registry in self.sub_registries:
            result = registry.get_clip_type_for(item)
            if result is not None:
                return result

        return None

    def wrap(self, item: T) -> Clip:
        """
        Returns a wrapper for the clip type.

        :param item: The item to convert.
        :return: The clip wrapping the item.
        """
        clip_type = self.get_clip_type_for(item)
        if clip_type is None:
            raise ValueError(f"Unsupported type {type(item)!r}")
        return clip_type(item)

