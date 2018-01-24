# -*- encoding: utf-8 -*-

# Yuuno - IPython + VapourSynth
# Copyright (C) 2017,2018 StuxCrystal (Roland Netzsch <stuxcrystal@encode.moe>)
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
from typing import Callable as TCallable, Union as TUnion

from traitlets import observe
from traitlets import Unicode, DottedObjectName
from traitlets import Instance, default
from traitlets import CInt, CBool
from traitlets import Union

from yuuno.trait_types import Callable

from yuuno.core.extension import Extension
from yuuno.core.registry import Registry

from yuuno.vs.utils import get_proxy_or_core, is_version
from yuuno.vs.alpha import AlphaOutputClip


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

    push_values: bool = CBool(True, help="""Push vs and the current core instance onto the current environment.""", config=True)

    core_num_threads: int = CInt(-1, help="""The number of concurrent threads used by the core. Can be set the change the number.
Settings to a value less than one makes it default to the number of hardware threads.
    """, config=True)
    core_add_cache: bool = CBool(True, help="For debugging purposes only. When set to `False` no caches will be automatically inserted between filters.", config=True)
    core_accept_lowercase: bool = CBool(False, help="When set to `True` function name lookups in the core are case insensitive. Don't distribute scripts that need it to be set.", config=True)
    core_max_cache_size: int = CBool(None, allow_none=True, help="Set the upper framebuffer cache size after which memory is aggressively freed. The value is in mediabytes.", config=True)

    def _update_core_values(name=None):
        def _func(self, change=None):
            core = get_proxy_or_core()

            if name is None:
                core.num_threads = self.core_num_threads
                core.add_cache = self.core_add_cache
                core.accept_lowercase = self.core_accept_lowercase

                # There is no obvious default for max_cache_size
                if self.core_max_cache_size is not None:
                    core.max_cache_size = self.core_max_cache_size

            else:
                setattr(core, name, change.new)
        return _func

    update_core_values = _update_core_values()

    _observe_num_threads      = observe("core_num_threads")(_update_core_values("num_threads"))
    _observe_add_cache        = observe("core_add_cache")(_update_core_values("add_cache"))
    _observe_accept_lowercase = observe("core_accept_lowercase")(_update_core_values("accept_lowercase"))
    _observe_max_cache_size   = observe("core_max_cache_size")(_update_core_values("max_cache_size"))

    @default("registry")
    def _init_registry(self):
        from vapoursynth import VideoNode, VideoFrame
        from yuuno.vs.clip import VapourSynthClip, VapourSynthFrame
        from yuuno.vs.clip import VapourSynthAlphaClip

        registry = Registry()
        registry.register(VapourSynthClip, VideoNode)
        registry.register(VapourSynthFrame, VideoFrame)
        registry.register(VapourSynthAlphaClip, AlphaOutputClip)
        if is_version(43):
            # Required so that IPython automatically supports alpha outputs
            from vapoursynth import AlphaOutputTuple
            registry.register(VapourSynthAlphaClip, AlphaOutputTuple)

        return registry

    @classmethod
    def is_supported(cls):
        try:
            import vapoursynth
        except ImportError:
            return False

        core = vapoursynth.get_core()
        return is_version(36)

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

        self.update_core_values()

    def deinitialize(self):
        self.parent.registry.remove_subregistry(self.registry)

        del self.parent.namespace['vs']
        del self.parent.namespace['core']
