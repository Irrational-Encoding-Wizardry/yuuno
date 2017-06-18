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
