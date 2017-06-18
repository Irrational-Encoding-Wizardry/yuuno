from traitlets.config import Configurable


class Extension(Configurable):
    """
    This is an entrypoint for extensions to Yuuno.

    This can be used to add support for new frameservers
    to Yuuno.
    """


    @classmethod
    def is_supported(cls) -> bool:
        """
        Called to check if the extension is supported at all.
        :return: The result of this check.
        """
        return False

    def initialize(self) -> None:
        """
        Called by the Yuuno-singleton so that the extension
        can register its observers.
        """

    def deinitialize(self) -> None:
        """
        Called by the Yuuno-singleton so that the extension
        can clear the environment.
        """
