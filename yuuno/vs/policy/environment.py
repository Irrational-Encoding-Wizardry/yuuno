# -*- encoding: utf-8 -*-

# Yuuno - IPython + VapourSynth
# Copyright (C) 2022 cid-chan (Sarah <cid+yuuno@cid-chan.moe>)
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
import typing as t

import sys
import types
import weakref
import threading
from pathlib import Path

import vapoursynth as vs

from yuuno.clip import Clip
from yuuno.utils import inline_resolved
from yuuno.multi_scripts.script import Script, ScriptManager

from yuuno.vs.extension import VapourSynth
from yuuno.vs.policy.clip import WrappedClip, WrappedAudio
from yuuno.vs.flags import Features


class YuunoPolicy(vs.EnvironmentPolicy):
    IS_OWNED_BY_US = False

    __slots__ = (
        "api", "global_policy", "policy_attachments"
    )

    api: vs.EnvironmentPolicyAPI
    current_policy: t.Any

    policy_attachments: t.MutableMapping[vs.EnvironmentData, types.ModuleType]

    def __init__(self):
        self.api = None

    def on_policy_registered(self, special_api: vs.EnvironmentPolicyAPI):
        YuunoPolicy.IS_OWNED_BY_US = True

        self.api = special_api
        self.current_policy = threading.local()
        self.policy_attachments = weakref.WeakKeyDictionary()

    def on_policy_cleared(self):
        self.policy_attachments.clear()
        YuunoPolicy.IS_OWNED_BY_US = False

    def get_current_environment(self) -> t.Optional[vs.EnvironmentData]:
        return getattr(self.current_policy, "current", None)

    def set_environment(self, environment: t.Optional[vs.EnvironmentData]):
        if "__vapoursynth__" in sys.modules:
            del sys.modules["__vapoursynth__"]

        old_environment = self.get_current_environment()
        self.current_policy.current = environment
        if environment is not None:
            if environment not in self.policy_attachments:
                self.policy_attachments[environment] = types.ModuleType("__vapoursynth__")
            sys.modules["__vapoursynth__"] = self.policy_attachments[environment]

        return old_environment


class VSScript(Script):
    __slots__ = ("main", "environment", "policy", "_exec_counter", "_dispose_hook")

    environment: t.Optional[vs.EnvironmentData]
    policy: YuunoPolicy

    def __init__(self, policy: YuunoPolicy):
        self.main = types.ModuleType("__vapoursynth__")
        self.policy = policy
        self.environment = None
        self._exec_counter = 0

        self._dispose_hook = lambda self: None

    @property
    def env(self) -> vs.Environment:
        if self.environment is None:
            raise RuntimeError("The environment has not been established yet.")
        return self.policy.api.wrap_environment(self.environment)

    @property
    def alive(self) -> bool:
        """
        Checks if the environment is still alive.
        """
        if self.environment is None:
            return False
        return self.alive

    def initialize(self) -> None:
        """
        Called when the script is going to be
        initialized.

        We need this to find out if script-creation
        is actually costly.
        """
        self.environment = self.policy.api.create_environment()
        if VapourSynth.instance().can_hook_log:
            self.policy.api.set_logger(self.environment, VapourSynth.instance()._on_vs_log)

    def dispose(self) -> None:
        """
        Disposes the script.
        """
        if self.environment is None:
            return

        self._dispose_hook(self)
        self.policy.api.destroy_environment(self.environment)
        self.environment = None

    @inline_resolved
    def get_results(self) -> t.Dict[str, Clip]:
        """
        Returns a dictionary with clips
        that represent the results of the script.
        """
        with self.use():
            return {
                str(k): WrappedClip(self.env, v)
                for k, v in vs.get_outputs().items()
            }

    @inline_resolved
    def execute(self, code: t.Union[bytes, str, Path]) -> None:
        """
        Executes the code inside the environment
        """
        current_counter = self._exec_counter
        self._exec_counter += 1

        filename = "<yuuno %d:%d>" % (self.env.id, current_counter)
        if isinstance(code, Path):
            filename = str(code)
            with open(code, "rb") as f:
                code = f.read()

        script = compile(code, filename, 'exec', dont_inherit=True)
        module_env = vars(self.main)

        exec(script, module_env, module_env)

    @inline_resolved
    def perform(self, cb: t.Callable[[], t.Any]) -> t.Any:
        with self.use():
            return cb()

    @property
    def use(self):
        return self.env.use



class VSScriptManager(ScriptManager):
    __slots__ = (
        "policy",
        "environments"
    )
    environments: t.Dict[str, VSScript]

    def __init__(self):
        self.policy = YuunoPolicy()
        self.environments = {}

    def env_wrapper_for(self, cls, *, wrapper=WrappedClip):
        def _wrapper(*args, **kwargs):
            return wrapper(vs.get_current_environment(), cls(*args, **kwargs))
        return _wrapper

    def create(self, name: str, *, initialize=False) -> Script:
        """
        Creates a new script environment.
        """
        if vs.has_policy() and self.policy.api is None:
            raise RuntimeError("We do not control the current environment.")
        elif not vs.has_policy():
            vs.register_policy(self.policy)

        if name in self.environments:
            raise ValueError("The environment already exists")

        script = VSScript(self.policy)
        script._dispose_hook = lambda _: self.environments.pop(name)
        self.environments[name] = script

        if initialize:
            script.initialize()

        return script

    def get(self, name: str) -> t.Optional[Script]:
        """
        Returns the script with the given name.
        """
        return self.environments.get(name)

    def dispose_all(self) -> None:
        """
        Disposes all scripts
        """
        for env in self.environments.values():
            env.dispose()

    def disable(self) -> None:
        """
        Disposes all scripts and tries to clean up.
        """

        self.dispose_all()
        self.policy.api.unregister_policy()
        self.policy = _Policy()
