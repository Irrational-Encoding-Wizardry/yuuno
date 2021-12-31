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
from typing import TYPE_CHECKING
from contextlib import contextmanager

from IPython import InteractiveShell
from IPython.core.magic import line_magic, cell_magic, magics_class

from yuuno import Yuuno
from yuuno_ipython.ipython.magic import MagicFeature, Magics
from yuuno_ipython.ipython.utils import execute_code
from yuuno_ipython.ipy_vs.vs_feature import VSFeature
from yuuno.vs.flags import Features

if TYPE_CHECKING:
    from vapoursynth import Environment
    from yuuno.vs.vsscript.script import ScriptManager, VSScript


_cur_env = None

def get_current_env() -> 'Environment':
    global _cur_env
    if _cur_env is None:
        import vapoursynth
        if Features.ENVIRONMENT_POLICIES:
            def __new_cur_env():
                return vapoursynth.get_current_environment().use()
            _cur_env = __new_cur_env
        else:
            _cur_env = vapoursynth.vpy_current_environment
    
    try:
        return _cur_env()
    except RuntimeError:
        return None


def env_from_script(script: 'VSScript') -> 'Environment':
    return script.perform(get_current_env).result()


@magics_class
class CoreControlMagics(Magics):

    @property
    def vsscript_feature(self) -> 'Use_VSScript':
        for feature in self.yuuno.get_extension('ipy_vs').features:
            if isinstance(feature, Use_VSScript):
                return feature
        raise Exception("Couldn't find Feature Instance? Report this error.")

    @property
    def script_manager(self) -> 'ScriptManager':
        return self.yuuno.get_extension('MultiScript').get_manager('VSScript')

    @property
    def yuuno(self):
        return Yuuno.instance()

    @cell_magic
    def isolated_core(self, line, cell):
        script: VSScript = self.script_manager.create('isolated-1', initialize=True)
        env = env_from_script(script)
        try:
            with env:
                with self.vsscript_feature.protect():
                    result = execute_code(cell, '<yuuno:isolated_core>', False)
                    if result is not None:
                        return result
        finally:
            script.dispose()

    @line_magic
    def reset_core(self, line):
        self.vsscript_feature.reset_script()


class VSScriptWrapper(object):

    def __init__(self, script):
        self.script = script
        self._env = env_from_script(self.script)

    @classmethod
    def with_name(cls, name):
        mgr = Yuuno.instance().get_extension('MultiScript')
        environment = Yuuno.instance().environment
        if mgr is None or not environment.use_vsscript:
            # VSScript is not enabled. Don't do anything.
            return

        manager: ScriptManager = mgr.get_manager('VSScript')
        if manager is None:
            # VSScript is not enabled. Don't do anything.
            return

        return cls(manager.create(name, initialize=True))

    def __enter__(self):
        return self._env.__enter__()

    def __exit__(self, *args, **kwargs):
        return self._env.__exit__(*args, **kwargs)

    def replace(self):
        """
        Replaces the top-most VapourSynth-Environment stack
        with the given VapourSynth environment.
        """
        cur_env = get_current_env()
        if get_current_env() != self._env:
            if not Features.ENVIRONMENT_POLICIES:
                # Hack to forcibly remove the environment from the stack.
                if cur_env is not None:
                    cur_env.__exit__()
            self._env.__enter__()

    def dispose(self):
        if get_current_env() == self._env:
            self._env.__exit__()
        self.script.dispose()


# noinspection PyPep8Naming
class Use_VSScript(VSFeature, MagicFeature):

    def __init__(self, *args, **kwargs):
        super(Use_VSScript, self).__init__(*args, **kwargs)
        self.events = {}

    def initialize(self):
        mgr = self.environment.parent.get_extension('MultiScript')
        if mgr is None or not self.environment.use_vsscript:
            # VSScript is not enabled. Don't do anything.
            return
        self.manager: ScriptManager = mgr.get_manager('VSScript')
        if self.manager is None:
            # VSScript is not enabled. Don't do anything.
            return

        self.events = {
            'pre_execute': [self._enter_env],
            'post_execute': [self._exit_env]
        }
        ipy: InteractiveShell = self.environment.ipython

        for name, evts in self.events.items():
            for evt in evts:
                ipy.events.register(name, evt)

        self.register_magics(CoreControlMagics)
        self._cell_level = 0
        self.manager: ScriptManager = mgr.get_manager('VSScript')
        self.script = None
        self.reset_script()

    @contextmanager
    def protect(self):
        self._cell_level += 1
        try:
            yield
        finally:
            self._cell_level -= 1

    def reset_script(self):
        if self.script is not None:
            self.script.dispose()

        self.script: VSScriptWrapper = VSScriptWrapper(self.manager.create('ipython', initialize=True))
        self._enter_env()

    def _enter_env(self):
        if self._cell_level > 0:
            return
        self.script.replace()

    def _exit_env(self):
        if self._cell_level > 0:
            return
        # Do nothing anymore.

    def deinitialize(self):
        if not self.events:
            return

        self.manager.dispose_all()

        ipy: InteractiveShell = self.environment.ipython

        for name, evts in self.events.items():
            for evt in evts:
                ipy.events.unregister(name, evt)

        super(Use_VSScript, self).deinitialize()
