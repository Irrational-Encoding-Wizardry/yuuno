############################
# Do not try this at home. #
############################
import builtins as __builtin__
import vapoursynth as vs
import sys


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


_patched_classes = {}
def _for_class(cls, inst=True):
    def _decorator(func):
        _patched_classes[cls] = func
        return func
    return _decorator

def _overridden_dict(obj):
    result = __dir__(obj)
    if type(obj) in _patched_classes:
        result += _patched_classes[type(obj)](obj)

    # Ensure that there are no duplicates
    return list(set(result))

__dir__ = dir
def install():
    import vapoursynth
    if not hasattr(vapoursynth, "construct_signature"):
        __builtin__.dir = _overridden_dict
        print("Vapoursynth Pre-R36 detected... Monkey-Patching autocompletion.", file=sys.stderr)


@_for_class(vs.Core)
@_for_class(vs.VideoNode)
def core_dir(core):
    return list(Plugin.get_namespaces())
