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
