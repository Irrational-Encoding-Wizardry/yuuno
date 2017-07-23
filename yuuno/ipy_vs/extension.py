from typing import List as Listing

from traitlets import default
from traitlets import Instance, List, DottedObjectName
from traitlets.utils.importstring import import_item

from yuuno.yuuno import Yuuno
from yuuno.core.extension import Extension

from yuuno.ipython.feature import Feature


class IPythonVapoursynthExtension(Extension):
    """
    This extension implements VapourSynth-specific features for IPython.
    """

    feature_classes: Listing[str] = List(DottedObjectName(), default_value=[
        "yuuno.ipy_vs.encode.Encode",
        "yuuno.ipy_vs.runvpy.RunVPy"
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

        from yuuno.ipython.environment import YuunoIPythonEnvironment
        if not isinstance(Yuuno.instance().environment, YuunoIPythonEnvironment):
            return False

        from yuuno.vs.extension import VapourSynth
        return VapourSynth.is_supported()

    def initialize(self):
        for feature in self.feature_classes:
            feature = import_item(feature)
            feature_inst = feature(extension=self)
            self.features.append(feature_inst)
            feature_inst.initialize()

    def deinitialize(self):
        for feature in self.features[:]:
            feature.deinitialize()
            self.features.remove(feature)
