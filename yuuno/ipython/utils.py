from typing import Callable


class fake_dict(object):
    """
    Decorator for functions so that they behave like a dict
    """

    def __init__(self, func: Callable[[object], object]) -> None:
        self.func = func

    def __getitem__(self, it: object) -> object:
        return self.func(it)

