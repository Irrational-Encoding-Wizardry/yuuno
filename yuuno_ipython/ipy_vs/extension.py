# -*- encoding: utf-8 -*-

# Yuuno - IPython + VapourSynth
# Copyright (C) 2017,2018 cid-chan (Sarah <cid+yuuno@cid-chan.moe>)
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


from typing import List as Listing

from traitlets import default
from traitlets import Instance, List, DottedObjectName
from traitlets.utils.importstring import import_item

from yuuno.yuuno import Yuuno
from yuuno.core.extension import Extension

from yuuno_ipython.ipython.feature import Feature


class IPythonVapoursynthExtension(Extension):
    """
    This extension implements VapourSynth-specific features for IPython.
    """
    _name = "ipy_vs"

    feature_classes: Listing[str] = List(DottedObjectName(), default_value=[
        "yuuno_ipython.ipy_vs.log.LogWriterFeature",
        "yuuno_ipython.ipy_vs.encode.Encode",
        "yuuno_ipython.ipy_vs.runvpy.RunVPy",
        "yuuno_ipython.ipy_vs.vsscript.Use_VSScript",
        "yuuno_ipython.ipy_vs.stateful_editor.StatefulEditorFeature"
    ], config=True, help="List of additional features to load.")

    features: Listing[Feature] = List(Instance(Feature))

    yuuno: Yuuno = Instance(Yuuno)

    @default("features")
    def _default_features(self):
        return []

    @default("yuuno")
    def _default_yuuno(self):
        return Yuuno.instance()

    @classmethod
    def is_supported(cls):
        try:
            import IPython
        except ImportError:
            return False

        from yuuno_ipython.ipython.environment import YuunoIPythonEnvironment
        if not isinstance(Yuuno.instance().environment, YuunoIPythonEnvironment):
            return False

        from yuuno.vs.extension import VapourSynth
        return VapourSynth.is_supported()

    def initialize(self):
        for feature in self.feature_classes:
            self.yuuno.log.debug(f"Loading feature: {feature}")
            feature = import_item(feature)
            feature_inst = feature(extension=self)
            self.features.append(feature_inst)
            feature_inst.initialize()

    def deinitialize(self):
        for feature in self.features[:]:
            feature.deinitialize()
            self.features.remove(feature)
