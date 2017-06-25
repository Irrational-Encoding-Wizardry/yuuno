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


from typing import List as TList

from ipywidgets import VBox
from ipywidgets import ToggleButtons

from traitlets import default, observe, validate, link
from traitlets import TraitError
from traitlets import Instance
from traitlets import List

from yuuno.ipython.apps.image import Image


class ImageChooser(VBox):
    """
    Implements an image chooser.
    """

    current: str = Instance(str)
    values: TList[str] = List(Instance(str))

    _ui_toggle: ToggleButtons = Instance(ToggleButtons)

    image: Image = Instance(Image)

    @default("image")
    def _default__image(self):
        return Image()

    @default("_ui_toggle")
    def _default__ui_toggle(self):
        return ToggleButtons()

    @validate('current')
    def _validate_current(self, proposal):
        if proposal.value not in self.values:
            raise TraitError("Current value not part of the values.")
        return proposal.value

    @observe('current')
    def _observe_current(self, proposal):
        self.set_image(proposal.new)

    def __init__(self, values, *args, **kwargs):
        super(ImageChooser, self).__init__(*args, **kwargs, values=values)

        self.children = [
            self._ui_toggle, self.image
        ]
        self._ui_toggle.options = self.values
        self._ui_toggle.value = self.current

        self._links = [
            link((self._ui_toggle, 'options'), (self, 'values')),
            link((self._ui_toggle, 'value'), (self, 'current'))
        ]

    def set_image(self, value):
        pass
