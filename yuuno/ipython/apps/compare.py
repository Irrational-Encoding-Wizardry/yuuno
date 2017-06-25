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


from yuuno import Yuuno
from yuuno.ipython.apps.chooser import ImageChooser
from yuuno.ipython.apps.mixins import InitialFrameMixin


class Compare(ImageChooser, InitialFrameMixin):
    """
    Shows an image-chooser with different clips.

    .. automethod:: __init__
    """

    def __init__(self, *images, **kwargs):
        self.images = images
        super(Compare, self).__init__(current="0", values=tuple(map(str, range(len(images)))), **kwargs)

    def set_image(self, value):
        img = Yuuno.instance().registry.wrap(self.images[int(value)])
        fno = min(self.frame_number, len(img)-1)
        self.image.image = img[fno].to_pil()
