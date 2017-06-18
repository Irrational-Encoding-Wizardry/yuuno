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
