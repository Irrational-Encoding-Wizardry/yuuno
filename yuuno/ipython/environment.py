from typing import Sequence, Tuple as TTuple

from IPython.core.interactiveshell import InteractiveShell

from traitlets import Instance
from traitlets import List, Tuple
from traitlets import Bool, Integer, Float
from traitlets import DottedObjectName
from traitlets import CaselessStrEnum

from traitlets.utils.importstring import import_item

from yuuno.ipython.feature import Feature

from yuuno.core.environment import Environment
from yuuno.yuuno import Yuuno


class YuunoIPythonEnvironment(Environment):
    """
    Stores the state containing the current
    """

    ipython: InteractiveShell = Instance(InteractiveShell)
    features: Sequence[Feature] = List(Instance(Feature))

    formatter: bool = Bool(True, help="Register IPython-formatters for objects", config=True)
    namespace: bool = Bool(True, help="Automatically push modules and extensions into the user namespace.", config=True)
    encode: bool = Bool(True, help="Automatically register the encode-magic (currently Yuuno only)", config=True)
    apps: bool = Bool(True, help="Register interactive apps as line-magics to IPython", config=True)

    tiling_threshold: TTuple[int, int] = List(
        Integer(),
        help="From which image size on should Yuuno tile the image to prevent the browser from crashing. "
             "(For interactive applications only.)",
        default_value=(5*1920, 5*1080),
        config=True,
        maxlen=2,
        minlen=2
    )
    tile_size: TTuple[int, int] = List(
        Integer(),
        help="The size of the tiles when an interactive application shows a tiled image.",
        default_value=(512, 512),
        config=True,
        maxlen=2,
        minlen=2
    )
    tile_viewport_size: TTuple[int, int] = List(
        Integer(),
        help="Size of the viewport on tiled images.",
        default_value=(960, 540),
        config=True,
        maxlen=2,
        minlen=2
    )

    inspect_default_sizes: Sequence[float] = List(
        Float(),
        default_value=(1, 2, 5),
        help="Default values for the inspect widget",
        config=True
    )
    inspect_resizer: str = CaselessStrEnum(
        ['NEAREST', 'BILINEAR', 'BICUBIC', 'LANCZOS'],
        default_value='NEAREST',
        help="Which PIL scaler should be used to resize the image?",
        config=True
    )

    diff_scale: bool = Bool(True, help="Apply CSS-Scale on the diff widget")

    feature_classes: Sequence[str] = List(DottedObjectName(), default_value=[
        "yuuno.ipython.formatter.Formatter",
        "yuuno.ipython.namespace.Namespace",
        "yuuno.ipython.encode.Encode",
        "yuuno.ipython.apps.feature.Apps"
    ], config=True)

    def init_feature(self, cls):
        feature_name = cls.feature_name()
        if not getattr(self, feature_name, False):
            return None

        feature = cls(environment=self)
        feature.initialize()
        return feature

    def load_features(self):
        features = []
        for feature in self.feature_classes:
            feature_class = import_item(feature)
            feature_instance = self.init_feature(feature_class)
            if feature_instance is not None:
                features.append(feature_instance)
        self.features = features

    def unload_features(self):
        for feature in self.features:
            feature.deinitialize()

    def initialize(self):
        self.ipython.configurables += [self.parent]
        self.ipython.configurables += [self]
        self.ipython.configurables += self.parent.extensions

        self.load_features()

        self.parent.log.debug("Yuuno for IPython configured")

    def deinitialize(self):
        self.unload_features()

        self.ipython.configurables.remove(self)
        self.ipython.configurables.remove(self.parent)
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
