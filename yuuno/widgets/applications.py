import ipywidgets
from IPython.display import Image as IPyImage, HTML, display
from PIL.Image import NEAREST

from yuuno.glue import convert_clip, image_to_bytes
from yuuno.widgets.image import Image, BaseImageChooser, ImageChooser
from yuuno.widgets.widget import Widget


def dump(clip, converter=convert_clip, *, lots_of_frames=False):
    if len(clip) > 20 and not lots_of_frames:
        display(HTML("<span style='color: red'>"
                     "A lot of frames are going to be shown. "
                     "Use lots_of_frames=True to force showing all of them"
                     "</span>"))
        return

    for frame in clip:
        display(IPyImage(image_to_bytes(converter(frame, frame_no=0))))


class diff(Widget):
    """
    Represents a simple diff.
    """

    template = '''
<div class="vs-diff-simple">
<style scoped>
div.vs-diff-simple-container > img {
   display: none;
   margin-top: 0 !important;
   %s
}

div.vs-diff-simple-container:not(:hover) > img.vs-diff-first,
div.vs-diff-simple-container:hover > img.vs-diff-second {
   display: block;
}
</style>
<div class="vs-diff-simple-container">
  <img class="vs-diff-first" src="%s">
  <img class="vs-diff-second" src="%s">
</div>
</div>
'''

    def __init__(self, clip1, clip2, converter=convert_clip, cap_size=True, frame_no=0):
        self.clip1 = image_to_bytes(converter(clip1, frame_no=frame_no))
        self.clip2 = image_to_bytes(converter(clip2, frame_no=frame_no))
        self.cap_size = cap_size

    def generate_styles(self):
        return ''.join([
            ("max-width: 100%; height: auto;" if self.cap_size else "")
        ])

    def _repr_html_(self):
        return self.template % (
            self.generate_styles(),
            Image.get_bytelink(self.clip1),
            Image.get_bytelink(self.clip2)
        )

    def __getattribute__(self, item):
        if item == "_ipython_display_":
            raise AttributeError
        return super(diff, self).__getattribute__(item)


class compare(BaseImageChooser):
    """
    lets you compare mutliple files.
    """

    def __init__(self, *clips, frame_no=0, converter=convert_clip, **kwargs):
        self.converter = converter
        self.frame_no = frame_no
        super(compare, self).__init__([], self.change_clip, **kwargs)
        self.clips = clips

    @property
    def clips(self):
        return self._clips.values()
    @clips.setter
    def clips(self, value):
        self._clips = dict(enumerate(value))
        self.images = tuple(range(len(value)))

    def change_clip(self, val):
        clip = self._clips[val]
        return self.converter(clip, frame_no=self.frame_no)


class inspect(BaseImageChooser):
    """
    lets you compare mutliple files.
    """

    @staticmethod
    def _convert_size_iter(sizes):
        if isinstance(sizes, dict):
            sizes = sizes.items

        for size in sizes:
            if not isinstance(size, (list, tuple)):
                yield size, str(size)
            else:
                yield size

    def __init__(self, clip,
                 sizes=((1, '100%'), (2, '200%'), (5, '500%')),
                 frame_no=0, converter=convert_clip,
                 **kwargs):

        self.converter = converter
        self.frame_no = frame_no
        self._clip = self.converter(clip, frame_no=self.frame_no)
        sizes = tuple(self._convert_size_iter(sizes))
        self.sizes = dict((size[1], size[0]) for size in sizes)
        super(inspect, self).__init__(tuple(size[1] for size in sizes), self.change_clip, tiled=True, **kwargs)
        self.clip = clip

    @property
    def clip(self):
        return self._clip
    @clip.setter
    def clip(self, value):
        self._clip = self.converter(value, frame_no=self.frame_no)
        self.clear_cache()
        self.change_clip(self.current)

    def change_clip(self, val):
        self.current = val
        width = self.sizes[val] * self._clip.width
        height = self.sizes[val] * self._clip.height
        return self._clip.resize((int(width), int(height)), NEAREST)


class preview(Widget):

    def __init__(self, *clips, converter=convert_clip, initial=0, initial_speed=500):
        self.converter = converter
        self.frames = []
        for clip in clips:
            self.frames.append((clip, Image(
                aperture=True
            )))

        frames_container = ipywidgets.VBox([frame[1].get_widget() for frame in self.frames])

        minlength = len(min(clips, key=len))
        slider = ipywidgets.IntSlider(
            value=initial,
            min=0,
            max=minlength - 1,
            step=1,
            orientation="horizontal"
        )
        play = ipywidgets.Play(
            value=initial,
            min=0,
            max=minlength - 1,
            step=1
        )
        speed_slider = ipywidgets.IntSlider(
            value=initial_speed,
            min=100,
            max=2000,
            step=20
        )

        speed_container = ipywidgets.HBox([ipywidgets.Label("Speed"), speed_slider])
        position_container = ipywidgets.HBox([ipywidgets.Label("Frame"), play, slider])
        controls = ipywidgets.VBox([speed_container, position_container])
        self.main_box = ipywidgets.VBox([controls, frames_container])

        ipywidgets.jslink((play, "value"), (slider, "value"))
        ipywidgets.jslink((speed_slider, "value"), (play, "interval"))

        slider.observe(self.do_step, names="value")
        self.do_step({'new': initial})

    def do_step(self, val):
        val = val['new']

        rendered = []
        for clip, image in self.frames:
            rendered.append((image, self.converter(clip, frame_no=val)))

        for widget, frame in rendered:
            widget.image = frame

    def get_widget(self):
        return self.main_box
