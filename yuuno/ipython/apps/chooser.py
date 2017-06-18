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
