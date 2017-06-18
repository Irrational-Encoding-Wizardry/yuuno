from typing import Any

from traitlets import HasTraits, Any


class Feature(HasTraits):
    """
    Defines a feature
    """

    environment: 'YuunoIPythonEnvironment' = Any()

    @classmethod
    def feature_name(cls):
        return cls.__name__.lower()

    def initialize(self):
        """
        Initializes a feature
        """

    def deinitialize(self):
        """
        Deinitializes a feature.
        """
