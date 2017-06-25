# -*- encoding: utf-8 -*-

# Yuuno - IPython + VapourSynth
# Copyright (C) 2017 StuxCrystal
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


from PIL import Image as PILImageModule

from traitlets import validate

from yuuno import Yuuno
from yuuno.ipython.apps.chooser import ImageChooser
from yuuno.ipython.apps.mixins import InitialFrameMixin
from yuuno.ipython.apps.mixins import ClipWrapperMixin


class Inspect(ImageChooser, InitialFrameMixin, ClipWrapperMixin):
    """
    Inspects an image.

    .. automethod:: __init__
    """

    def __init__(self, clip, *args, **kwargs):
        if "values" not in kwargs:
            kwargs["values"] = tuple(map(str, Yuuno.instance().environment.inspect_default_sizes))

        if "current" not in kwargs:
            kwargs["current"] = kwargs["values"][0]

        super(Inspect, self).__init__(*args, **kwargs)
        self.clip = clip
        self.set_image(kwargs["current"])

    @property
    def scaler(self):
        return getattr(PILImageModule, Yuuno.instance().environment.inspect_resizer.upper())

    def set_image(self, value):
        if self._clip is None:
            return

        factor = float(value)
        image = self._clip[self.frame_number].to_pil()
        resized = image.resize((int(image.width*factor), int(image.height*factor)), self.scaler)
        with self.image.hold_trait_notifications():
            self.image.image = resized
        self.image.tiled = True
        self.image.update()
