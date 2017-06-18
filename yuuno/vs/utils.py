from typing import AnyStr, Callable

from traitlets.utils.importstring import import_item


def get_proxy_or_core():
    """
    Returns the current core-proxy or a core instance for pre Vapoursynth R37 installations
    :return: A proxy or the actual core.
    """
    try:
        from vapoursynth import core
    except ImportError:
        from vapoursynth import get_core
        core = get_core()
    return core


def filter_or_import(name: AnyStr) -> Callable:
    """
    Loads the filter from the current core or tries to import the name.

    :param name: The name to load.
    :return:  A callable.
    """
    core = get_proxy_or_core()

    try:
        ns, func = name.split(".", 1)
        return getattr(getattr(core, ns), func)
    except (ValueError, AttributeError):
        return import_item(name)
