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


from typing import Sequence, Tuple as TTuple

from IPython.core.interactiveshell import InteractiveShell

from traitlets import Instance
from traitlets import List
from traitlets import Bool, Integer, Float
from traitlets import DottedObjectName
from traitlets import CaselessStrEnum

from traitlets.utils.importstring import import_item

from yuuno_ipython.ipython.feature import Feature

from yuuno.core.environment import Environment
from yuuno.yuuno import Yuuno


class YuunoIPythonEnvironment(Environment):
    """
    Stores the state containing the current
    """

    ipython: InteractiveShell = Instance(InteractiveShell)
    features: Sequence[Feature] = List(Instance(Feature))

    no_env_wrap: bool = Bool(True, help="Overwrite the setting of Yuuno to execute all formatting calls inside the correct environment", config=True)

    formatter: bool = Bool(True, help="Register IPython-formatters for objects", config=True)
    namespace: bool = Bool(True, help="Automatically push modules and extensions into the user namespace.", config=True)
    apps: bool = Bool(True, help="Register interactive apps as line-magics to IPython", config=True)

    use_vsscript: bool = Bool(True, help="Use VSScript", config=True)

    feature_classes: Sequence[str] = List(DottedObjectName(), default_value=[
        "yuuno_ipython.ipython.formatter.Formatter",
        "yuuno_ipython.ipython.namespace.Namespace",
        "yuuno_ipython.ipython.apps.feature.Apps",
    ], config=True)

    def init_feature(self, cls):
        feature_name = cls.feature_name()
        if not getattr(self, feature_name, False):
            return None

        feature = cls(environment=self)
        feature.initialize()
        return feature

    def additional_extensions(self):
        result = []
        result.append("yuuno_ipython.ipy_vs.extension.IPythonVapoursynthExtension")
        if self.use_vsscript:
            result.append("yuuno.multi_scripts.extension.MultiScriptExtension")
        return result

    def load_features(self):
        features = []
        for feature in self.feature_classes:
            self.parent.log.debug(f"Loading feature: {feature}")
            feature_class = import_item(feature)
            feature_instance = self.init_feature(feature_class)
            if feature_instance is not None:
                features.append(feature_instance)
        self.features = features

    def unload_features(self):
        for feature in self.features:
            feature.deinitialize()

    def post_extension_load(self):
        if self.no_env_wrap:
            vs = self.parent.get_extension('VapourSynth')
            if vs is not None:
                vs.vsscript_environment_wrap = False
                self.parent.log.debug("Disabling Env-Wrapping for VapourSynth clips.")

    def initialize(self):
        self.ipython.configurables += [self.parent, self.parent.output]
        self.ipython.configurables += [self]
        self.ipython.configurables += self.parent.extensions

        self.load_features()

        self.parent.log.debug("Yuuno for IPython configured")

    def deinitialize(self):
        self.unload_features()

        self.ipython.configurables.remove(self)
        self.ipython.configurables.remove(self.parent)
        self.ipython.configurables.remove(self.parent.output)
        for extension in self.parent.extensions:
            self.ipython.configurables.remove(extension)

        self.parent.log.debug("Yuuno for IPython unloaded")


def load_ipython_extension(ipython: InteractiveShell) -> None:
    """
    Called when IPython load this extension.

    :param ipython:  The current IPython-console instance.
    """
    yuuno = Yuuno.instance(parent=ipython)
    yuuno.environment = YuunoIPythonEnvironment(parent=yuuno, ipython=ipython)
    yuuno.start()


def unload_ipython_extension(ipython) -> None:
    """
    Called when IPython unloads the extension.
    """
    yuuno = Yuuno.instance()
    yuuno.stop()
