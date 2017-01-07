import builtins as __builtin__
from functools import wraps
import vapoursynth as vs


class Plugin(object):
    """
    Wrapper for namespaces to interact with it.
    """

    def __init__(self, raw_plugin):
        self.raw_plugin = raw_plugin

    @staticmethod
    def get_namespaces():
        """
        Retrieves all namespaces.
        """
        for plugin in vs.get_core().get_plugins().values():
            yield plugin['namespace']

    @classmethod
    def by_namespace(cls, namespace):
        """
        Retrieves the Plugin by namespace.
        """
        for plugin in vs.get_core().get_plugins().values():
            if plugin['namespace'] == namespace:
                return cls(plugin)
        return None


_patched_classes = ({}, {})
def _for_class(cls, inst=True):
    def _decorator(func):
        if inst:
            _patched_classes[0][cls] = func
        else:
            _patched_classes[1][cls] = func
        return func
    return _decorator

def _overridden_dict(obj):
    result = __dir__(obj)
    if type(obj) in _patched_classes[0]:
        result += _patched_classes[0][type(obj)](obj)
    if obj in _patched_classes[1]:
        result += _patched_classes[1][type(obj)](obj)
    return result

__dir__ = dir

def install():
    __builtin__.dir = _overridden_dict


@_for_class(vs.Core)
@_for_class(vs.VideoNode)
def core_dir(core):
    return list(Plugin.get_namespaces())
