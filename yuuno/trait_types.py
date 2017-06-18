from traitlets import TraitType


class Callable(TraitType):
    """
    Represents a callable object
    """

    def validate(self, obj, value):
        if not callable(value):
            self.error(obj, value)
        return value
