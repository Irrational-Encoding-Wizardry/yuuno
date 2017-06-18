from traitlets.config import Configurable


class Environment(Configurable):
    """
    Defines the current environment used in Yuuno.
    """

    def initialize(self) -> None:
        """
        Called by yuuno to tell it that yuuno has
        initialized to the point that it can now initialize
        interoperability for the given environment.
        """

    def deinitialize(self) -> None:
        """
        Called by yuuno before it deconfigures itself.
        """
