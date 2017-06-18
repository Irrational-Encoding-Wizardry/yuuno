from yuuno import Yuuno

from yuuno.ipython.apps.image import Image
from yuuno.ipython.apps.mixins import Jinja2Mixin, InitialFrameMixin


class Diff(InitialFrameMixin, Jinja2Mixin):
    """
    Implements a diff using a simple hover.

    This is a rather static "app" since does not rely on ipywidgets.

    .. automethod:: __init__
    """

    def __init__(self, *clips, **kwargs):
        super(Diff, self).__init__(**kwargs)
        self.clips = map(self.convert_clip, clips)

    def convert_clip(self, clip):
        clip = Yuuno.instance().registry.wrap(clip)
        return Image.get_bytelink(clip[self.frame_number].to_pil())

    def _repr_html_(self):
        return self.render("diff.html", {
            'img': tuple(self.clips),
            'cap_size': Yuuno.instance().environment.diff_scale
        })
