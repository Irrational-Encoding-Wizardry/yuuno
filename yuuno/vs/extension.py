from typing import Callable as TCallable, Union as TUnion

from traitlets import Unicode, DottedObjectName
from traitlets import Instance, default
from traitlets import Union

from yuuno.trait_types import Callable

from yuuno.core.extension import Extension
from yuuno.core.registry import Registry

from yuuno.vs.utils import get_proxy_or_core


class VapourSynth(Extension):
    """
    Entry-Point for VapourSynth support of Yuuno
    """

    yuv_matrix: str = Unicode("709", help="The YUV-Matrix to use when converting to RGB", config=True)
    resizer: TUnion[str, TCallable] = Union([DottedObjectName(), Callable()],
        default_value="resize.Spline36",
        help="""Defines the resizer to use when converting from YUV to RGB.
It is essentially a function which takes the same arguments as a VapourSynth internal
resizer. The clip is passed as the first argument.

Yuuno will first try to match it to a VapourSynth-function defined by a plugin before
attempting to import it from a module and treat it as a normal function.

If the passed object is a callable, it will just use the callable.
        """,
        config=True
    )

    registry: Registry = Instance(Registry, read_only=True)

    @default("registry")
    def _init_registry(self):
        from vapoursynth import VideoNode, VideoFrame
        from yuuno.vs.clip import VapourSynthClip, VapourSynthFrame

        registry = Registry()
        registry.register(VapourSynthClip, VideoNode)
        registry.register(VapourSynthFrame, VideoFrame)
        return registry

    @classmethod
    def is_supported(cls):
        try:
            import vapoursynth
        except ImportError:
            return False

        core = vapoursynth.get_core()
        return core.version_number() > 35

    @property
    def resize_filter(self) -> TCallable:
        """
        Loads the resize-filter for any image operations.

        :return: The returned filter
        """
        from yuuno.vs.utils import filter_or_import
        if callable(self.resizer):
            return self.resizer
        return filter_or_import(self.resizer)

    def initialize(self):
        self.parent.registry.add_subregistry(self.registry)

        import vapoursynth
        core = get_proxy_or_core()

        self.parent.namespace['vs'] = vapoursynth
        self.parent.namespace['core'] = core

    def deinitialize(self):
        self.parent.registry.remove_subregistry(self.registry)

        del self.parent.namespace['vs']
        del self.parent.namespace['core']
