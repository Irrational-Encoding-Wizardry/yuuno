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
import math
from enum import IntEnum
from typing import TypeVar, NamedTuple, Tuple

from PIL.Image import Image

from yuuno.utils import inline_resolved, Future


T = TypeVar("T")


class Size(NamedTuple):
    width: int
    height: int


class SampleType(IntEnum):
    INTEGER = 0
    FLOAT = 1


class ColorFamily(IntEnum):
    GREY = 0
    RGB = 1
    YUV = 2


class RawFormat(NamedTuple):
    bits_per_sample: int
    num_planes: int
    family: ColorFamily
    sample_type: SampleType
    subsampling_h: int = 0
    subsampling_w: int = 0

    @property
    def bytes_per_sample(self) -> int:
        return int(math.ceil(self.bits_per_sample/8))
RawFormat.SampleType = SampleType
RawFormat.ColorFamily = ColorFamily


GRAY8 = RawFormat(8, 1, RawFormat.ColorFamily.GREY, RawFormat.SampleType.INTEGER)
RGB24 = RawFormat(8, 3, RawFormat.ColorFamily.RGB, RawFormat.SampleType.INTEGER)
RGBA32 = RawFormat(8, 4, RawFormat.ColorFamily.RGB, RawFormat.SampleType.INTEGER)


class Frame(object):
    """
    This class represents a single frame out of a clip.
    """

    def to_pil(self) -> Image:
        """
        Generates an RGB (or RGBA) 8bit PIL-Image from the frame.
        :return: A PIL-Image with the frame data.
        """

    def format(self) -> RawFormat:
        """
        Returns the raw-format of the image.
        :return: The raw-format of the image.
        """
        bands = self.to_pil().getbands()
        if len(bands) == 1:
            return GRAY8
        if len(bands) == 4:
            return RGBA32
        return RGB24

    def size(self) -> Size:
        p = self.to_pil()
        return Size(p.width, p.height)

    def plane_size(self, plane) -> int:
        """
        Automatically calculated from size and format.,

        :param plane:  The plane number.
        :return:       The size of a plane.
        """
        w, h = self.size()
        format = self.format()

        if 0 < plane < 4:
            w >>= format.subsampling_w
            h >>= format.subsampling_h

        return w*h*format.bytes_per_sample

    def to_raw(self) -> bytes:
        """
        Generates an image that corresponds to the given frame data.
        :return: A bytes-object with the frame data
        """
        p = self.to_pil()
        return b"".join(
            bytes(im.getdata()) for im in p.split()
        )

    @inline_resolved
    def get_raw_data_async(self) -> Tuple[Size, RawFormat, bytes]:
        return self.size(), self.format(), self.to_raw()


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

    def __getitem__(self, item: int) -> Future:
        """
        Extracts the frame from the clip.

        :param item: The frame number
        :return: A frame-instance with the given data.
        """
        raise NotImplementedError
