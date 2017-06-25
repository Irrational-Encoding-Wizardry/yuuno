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


from typing import Any as TAny

from ipywidgets import HBox, VBox, Layout
from ipywidgets import IntSlider, Button

from traitlets import default, directional_link, observe
from traitlets import Instance
from traitlets import Integer

from yuuno.ipython.apps.image import Image
from yuuno.ipython.apps.mixins import ClipWrapperMixin


class Preview(VBox, ClipWrapperMixin):
    """
    Implements a preview widget

    .. automethod:: __init__
    """

    _current: Image = Instance(Image)

    _ui_intslider: IntSlider = Instance(IntSlider)

    frame: int = Integer(default_value=0)

    @default("_current")
    def _default_current(self):
        return Image()

    @default("_ui_intslider")
    def _default_ui_intslider(self):
        return IntSlider(
            continuous_update=False,
            orientation="horizontal",
            step=1,
            min=0,
            value=self.frame,
            max=1,
            layout=Layout(flex="2 2 auto")
        )

    @observe("_clip")
    def _update_islider(self, proposal):
        clip: TAny = proposal.new
        current_frame = self.frame

        with self.hold_trait_notifications():
            self.frame = min(len(clip)-1, current_frame)

        self._ui_intslider.max = len(clip)-1
        self._ui_intslider.value = self.frame

        self._update_image(clip, self.frame)

    @observe("frame")
    def _update_shown_frame(self, proposal):
        self._update_image(self._clip, proposal.new)

    def __init__(self, clip=None, *args, **kwargs):
        super(Preview, self).__init__(*args, **kwargs, clip=clip)
        self.links = [directional_link((self._ui_intslider, 'value'), (self, 'frame'))]

        prev = Button(icon="fa-step-backward", layout=Layout(width="50px"))
        prev.on_click(lambda s: self.step(-1))
        next = Button(icon="fa-step-forward", layout=Layout(width="50px"))
        next.on_click(lambda s: self.step(1))

        self.children = [
            HBox([prev, next, self._ui_intslider]),
            self._current
        ]

    def step(self, difference):
        self._ui_intslider.value += difference

    def _update_image(self, clip, frame):
        self._current.image = clip[frame].to_pil()
