# -*- encoding: utf-8 -*-

# Yuuno - IPython + VapourSynth
# Copyright (C) 2018 cid-chan (Sarah <cid+yuuno@cid-chan.moe>)
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
from pathlib import Path
from typing import Dict, Union, Callable, Any, Optional

import vapoursynth

from yuuno import Yuuno
from yuuno.clip import Clip
from yuuno.utils import inline_resolved
from yuuno.multi_scripts.script import ScriptManager, Script

from yuuno.vs.vsscript.containermodule import create_module
from yuuno.vs.vsscript.vs_capi import ScriptEnvironment, does_own_vsscript
from yuuno.vs.vsscript.vs_capi import enable_vsscript, disable_vsscript
from yuuno.vs.vsscript.clip import WrappedClip
from yuuno.vs.utils import is_single


class VSScript(Script):

    def __init__(self, manager, name):
        self.manager = manager
        self.name = name

        self.env = ScriptEnvironment()
        self.exec_counter = 0
        self.module_dict = {}

        self.manager._on_create(self, self.env.id, self.name)

    @property
    def _yuuno(self):
        return Yuuno.instance()

    @property
    def alive(self) -> bool:
        """
        Checks if the environment is still alive.
        """
        return self.env is not None and self.env.alive

    def initialize(self) -> None:
        self.env.enable()
        self.env.perform(lambda: self._yuuno.get_extension('VapourSynth').update_core_values())

    def _invoke_exec_counter(self):
        self.exec_counter += 1
        return self.exec_counter

    def dispose(self) -> None:
        """
        Disposes the script.
        """
        self.manager._on_dispose(self.env.id, self.name)
        self.env.dispose()

    @inline_resolved
    def get_results(self) -> Dict[str, Clip]:
        """
        Returns a dictionary with clips
        that represent the results of the script.
        """
        return {str(k): WrappedClip(self, self._yuuno.wrap(v)) for k, v in self.env.outputs.items()}

    @inline_resolved
    def perform(self, cb: Callable[[], Any]) -> Any:
        return self.env.perform(cb)

    @inline_resolved
    def execute(self, code: Union[str, Path]) -> None:
        """
        Executes the code inside the environment
        """
        filename = "<yuuno %d:%d>" % (self.env.id, self._invoke_exec_counter())
        if isinstance(code, Path):
            filename = str(code)
            with open(code, "rb") as f:
                code = f.read()

        script = compile(code, filename, 'exec', dont_inherit=True)

        def _run():
            exec(script, self.module_dict, {})

        self.env.perform(_run)


class VSScriptManager(ScriptManager):

    def __init__(self):
        self._does_manage_vsscript = False
        self.envs: Dict[int, VSScript] = {}
        self.scripts: Dict[str, VSScript] = {}
        create_module(self._select_current_dict)

    def _current_script(self):
        assert hasattr(vapoursynth, 'vpy_current_environment')
        try:
            env = vapoursynth.vpy_current_environment()
        except RuntimeError:
            return None
        return self.envs.get(env.env_id, None)

    def _select_current_dict(self):
        env = self._current_script()
        if env is None:
            return {}
        return env.module_dict

    def _on_create(self, script, id, name):
        self.envs[id] = script
        self.scripts[name] = script

    def _on_dispose(self, id, name):
        del self.envs[id]
        del self.scripts[name]

    def env_wrapper_for(self, cls, wrapper=WrappedClip):
        def _wrapper(*args, **kwargs):
            current_env = self._current_script()
            return wrapper(current_env, cls(*args, **kwargs))
        return _wrapper

    def create(self, name: str, *, initialize=False) -> Script:
        """
        Creates a new script environment.
        """
        if is_single():
            enable_vsscript()
            self._does_manage_vsscript = True

        elif does_own_vsscript():
            pass

        # Make sure we have full control of VSScript
        elif not self._does_manage_vsscript:
            raise RuntimeError("The script manager does not control VSScript.")

        if name in self.scripts:
            raise ValueError("The script already exists.")

        # Create the core now.
        script = VSScript(self, name)
        self.scripts[name] = script
        if initialize:
            script.initialize()
        return script

    def get(self, name: str) -> Optional[Script]:
        """
        Returns the script with the given name.
        """
        return self.scripts[name]

    def dispose_all(self) -> None:
        """
        Disposes all scripts
        """
        for script in list(self.scripts.values()):
            script.dispose()

    def disable(self) -> None:
        """
        Disposes all scripts and tries to clean up.
        """
        self.dispose_all()
        if self._does_manage_vsscript:
            disable_vsscript()
            self._does_manage_vsscript = False
