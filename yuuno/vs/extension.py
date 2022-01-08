# -*- encoding: utf-8 -*-

# Yuuno - IPython + VapourSynth
# Copyright (C) 2017,2018,2022 cid-chan (Sarah <cid+yuuno@cid-chan.moe>)
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
import sys
from typing import TYPE_CHECKING
from typing import Callable as TCallable, Union as TUnion
from typing import List as TList, Optional

from traitlets import observe
from traitlets import Unicode, DottedObjectName
from traitlets import default
from traitlets import CInt, CBool
from traitlets import Union
from traitlets import List
from traitlets.config import import_item

from yuuno.trait_types import Callable

from yuuno.core.extension import Extension
from yuuno.core.registry import Registry

from yuuno.vs.utils import get_proxy_or_core
from yuuno.vs.utils import MessageLevel, is_single
from yuuno.vs.flags import Features
from yuuno.vs.alpha import AlphaOutputClip

from yuuno.multi_scripts.subprocess.provider import ScriptProviderRegistration


if TYPE_CHECKING:
    import vapoursynth as vs
    from yuuno.multi_scripts.extension import MultiScriptExtension


class VapourSynth(Extension):
    """
    Entry-Point for VapourSynth support of Yuuno
    """
    _name = "VapourSynth"

    hook_messages: bool = CBool(True, help="""Redirect the message handler to this extension so other parts of Yuuno can handle it.
    
Note that this feature is disabled on vsscript-environments (vsedit, vspipe, etc.)""", config=True)
    yuv_matrix: str = Unicode("709", help="The YUV-Matrix to use when converting to RGB", config=True)
    prefer_props: bool = CBool(True, help="If set, the data of the video node will be preferred.", config=True)
    merge_bands: bool = CBool(False, help="Manually extract the planes and merge them using PIL. Defaults to automatically detecting the correct choice.", config=True)

    post_processor = Union(
        [DottedObjectName(), Callable()], allow_none=True,
        default_value=None,
        help="Define a post-processor function. It gets an RGB24 clip and returns an RGB24 clip.",
        config=True
    )
    resizer: TUnion[str, TCallable] = Union(
        [DottedObjectName(), Callable()],
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

    push_values: bool = CBool(True, help="""Push vs and the current core instance onto the current environment.""", config=True)

    core_num_threads: int = CInt(-1, help="""The number of concurrent threads used by the core. Can be set the change the number.
Settings to a value less than one makes it default to the number of hardware threads.
    """, config=True)
    core_add_cache: bool = CBool(True, help="For debugging purposes only. When set to `False` no caches will be automatically inserted between filters.", config=True)
    core_accept_lowercase: bool = CBool(False, help="When set to `True` function name lookups in the core are case insensitive. Don't distribute scripts that need it to be set.", config=True)
    core_max_cache_size: int = CBool(None, allow_none=True, help="Set the upper framebuffer cache size after which memory is aggressively freed. The value is in mediabytes.", config=True)

    vsscript_environment_wrap: bool = CBool(True, help="Allow Yuuno to automatically wrap the internal frame-extractor into the current environment. Do not disable while running multiple cores at once.", config=True)
    raw_force_compat: bool = CBool(True, "In raw image exports, force Planar RGB output", config=True)

    log_handlers: TList[TCallable[[int, str], None]] = List(Callable())

    @default("log_handlers")
    def _default_log_handlers(self):
        return []

    def _update_core_values(name: Optional[str]=None):
        def _func(self, change=None):
            core = get_proxy_or_core()
            if core is None:
                return

            if name is None:
                core.num_threads = self.core_num_threads

                # Not supported in
                if hasattr(core, "add_cache"):
                    core.add_cache = self.core_add_cache

                if hasattr(core, 'accept_lowercase'):
                    core.accept_lowercase = self.core_accept_lowercase

                # There is no obvious default for max_cache_size
                if self.core_max_cache_size is not None:
                    core.max_cache_size = self.core_max_cache_size

            elif hasattr(core, name):
                setattr(core, name, change.new)
        return _func

    update_core_values = _update_core_values()

    _observe_num_threads      = observe("core_num_threads")(_update_core_values("num_threads"))
    _observe_add_cache        = observe("core_add_cache")(_update_core_values("add_cache"))
    _observe_accept_lowercase = observe("core_accept_lowercase")(_update_core_values("accept_lowercase"))
    _observe_max_cache_size   = observe("core_max_cache_size")(_update_core_values("max_cache_size"))

    @staticmethod
    def instance() -> 'VapourSynth':
        from yuuno import Yuuno
        return Yuuno.instance().get_extension(VapourSynth)

    @classmethod
    def is_supported(cls):
        return not Features.NOT_SUPPORTED

    @property
    def resize_filter(self) -> TCallable[['vs.VideoNode', 'int'], 'vs.VideoNode']:
        """
        Loads the resize-filter for any image operations.

        :return: The returned filter
        """
        from yuuno.vs.utils import filter_or_import
        if callable(self.resizer):
            return self.resizer
        return filter_or_import(self.resizer)

    @property
    def processor(self):
        if self.post_processor is None:
            return
        func = self.post_processor
        if not callable(func):
            func = import_item(func)
        return func

    def _on_vs_log(self, level: MessageLevel, message: str):
        try:
            for cb in self.log_handlers:
                cb(level, message)
        except Exception as e:
            import traceback
            print("During logging of a vapoursynth-message, this exception occured:", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)

    @property
    def can_hook_log(self):
        if not self.hook_messages:
            return False

        if Features.ENVIRONMENT_POLICIES:
            from yuuno.vs.policy.environment import YuunoPolicy
            if YuunoPolicy.IS_OWNED_BY_US:
                return True

        return is_single()

    def initialize_hook(self, vapoursynth):
        if self.can_hook_log:
            if not Features.API4:
                vapoursynth.set_message_handler(self._on_vs_log)
        elif self.hook_messages:
            self.parent.log.debug("vsscript-Environment detected. Skipping hook on message-handler.")

    def initialize_namespace(self, vapoursynth):
        core = get_proxy_or_core()
        self.parent.namespace['vs'] = vapoursynth
        self.parent.namespace['core'] = core

    def initialize_registry(self):
        self.parent.log.debug("Registering wrappers.")
        from vapoursynth import VideoNode, VideoFrame
        from yuuno.vs.clip import VapourSynthClip, VapourSynthFrame
        from yuuno.vs.clip import VapourSynthAlphaClip, VapourSynthAudio

        # Detected VSScript.
        wrapperfunc = lambda cls, wrapper=None: cls
        if self.script_manager is not None and self.vsscript_environment_wrap:
            wrapperfunc = self.script_manager.env_wrapper_for

        self.registry = Registry()
        self.registry.register(wrapperfunc(VapourSynthClip), VideoNode)
        self.registry.register(wrapperfunc(VapourSynthFrame), VideoFrame)
        self.registry.register(wrapperfunc(VapourSynthAlphaClip), AlphaOutputClip)
        if Features.SUPPORT_ALPHA_OUTPUT_TUPLE:
            # Required so that IPython automatically supports alpha outputs
            from vapoursynth import AlphaOutputTuple
            self.registry.register(wrapperfunc(VapourSynthAlphaClip), AlphaOutputTuple)

        if Features.API4:
            from vapoursynth import VideoOutputTuple, AudioNode
            from yuuno.vs.policy.clip import WrappedAudio
            self.registry.register(wrapperfunc(VapourSynthAlphaClip), VideoOutputTuple)
            self.registry.register(wrapperfunc(VapourSynthAudio, wrapper=WrappedAudio), AudioNode)

        self.parent.registry.add_subregistry(self.registry)

    def initialize_multi_script(self):
        self.script_manager = None
        managers: Optional['MultiScriptExtension'] = self.parent.get_extension('MultiScript')
        if managers is None:
            self.parent.log.debug("MultiScript not found. Skipping VSScript.")
            return

        managers.register_provider('vapoursynth', ScriptProviderRegistration(
            providercls="yuuno.vs.provider.VSScriptProvider",
            extensions=[]
        ))

        # Check support for vapoursynth/#389 at R44
        if not Features.EXPORT_VSSCRIPT_ENV:
            self.parent.log.info("Yuuno doesn't support VSScript for VS<R44")
            return

        self.parent.log.debug("Enabling VSScript.")
        if Features.API4:
            from yuuno.vs.policy.environment import VSScriptManager
        else:
            from yuuno.vs.vsscript.script import VSScriptManager
            from yuuno.vs.vsscript.vs_capi import enable_vsscript
            enable_vsscript()

        self.script_manager = VSScriptManager()
        managers.register_manager('VSScript', self.script_manager)
        self.parent.log.debug("VSScript enabled.")

    def initialize(self):
        import vapoursynth

        self.initialize_hook(vapoursynth)
        self.initialize_namespace(vapoursynth)
        self.initialize_multi_script()
        self.initialize_registry()

        if self.script_manager is None:
            self.update_core_values()

    def deinitialize(self):
        self.parent.registry.remove_subregistry(self.registry)
        del self.parent.namespace['vs']
        del self.parent.namespace['core']

        if self.can_hook_log:
            import vapoursynth
            vapoursynth.set_message_handler(None)

        if Features.EXPORT_VSSCRIPT_ENV and self.script_manager is not None:
            self.script_manager.disable()
