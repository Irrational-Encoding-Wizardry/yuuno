from typing import TypeVar

from PIL.Image import Image


T = TypeVar("T")


class Frame(object):
    """
    This class represents a single frame out of a clip.
    """

    def to_pil(self) -> Image:
        """
        Generates an RGB PIL-Image from the frame.
        :return: A PIL-Image with the frame data.
        """


class Clip(object):
    """
    Encapsulates a clip for the applications.

    Some special functions might require an extended
    interface that is defined in its respective places.

    .. automethod:: __len__
    .. automethod:: __getitem__
    """

    def __init__(self, clip: T) -> None:
        self.clip: T = clip

    def __len__(self) -> int:
        """
        Calculates the length of the clip in frames.

        :return: The amount of frames in the clip
        """
        raise NotImplementedError

    def __getitem__(self, item: int) -> Frame:
        """
        Extracts the frame from the clip.

        :param item: The frame number
        :return: A frame-instance with the given data.
        """
        raise NotImplementedError


