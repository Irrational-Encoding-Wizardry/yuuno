import base64

import ipywidgets as widgets
from IPython import display

from yuuno.vsimg import frame2image, image2bytes


def _get_bytelink(data, format="image/png"):
    return "data:%s;base64,%s"%(format, base64.b64encode(data).decode())

def diff_frames(f1, f2=None, frameno=0):
    if f2 is None:
        f2 = f1[1:]
    f1 = image2bytes(frame2image(f1[frameno]))
    f2 = image2bytes(frame2image(f2[frameno]))

    display.display(display.HTML("".join(['''
<div>
<style scoped>
div.vs-diff-container {
   margin-top: 1em;
}

div.vs-diff-container > img {
   display: none;
   margin-top: 0 !important;
}

div.vs-diff-container:not(:hover) > img.vs-diff-first,
div.vs-diff-container:hover > img.vs-diff-second {
   display: block;
}
</style>
<div class="vs-diff-container">
<img class="vs-diff-first" src="''',_get_bytelink(f1),'''">
<img class="vs-diff-second" src="''',_get_bytelink(f2),'''">
</div>
</div>
'''])))


def show_clip(clip, *, lots_of_frames=False):
    if len(clip) > 20 and not lots_of_frames:
        display.display(
            display.HTML("<span style='color: red'>"
                         "A lot of frames are going to be shown. "
                         "Use lots_of_frames=True to force showing all of them"
                         "</span>")
        )
        return
    for frame in clip:
        display.display(display.Image(image2bytes(frame2image(frame))))


def frame_step(*clips):
    minlength = len(min(clips, key=len))

    frames = []
    for clip in clips:
        frames.append((clip, widgets.Image(
            value=image2bytes(frame2image(clip[0])),
            format="png",
            width = clip.width,
            height = clip.height
        )))
    slider = widgets.IntSlider(
        value=0,
        min=0,
        max=minlength-1,
        step=1,
        orientation="horizontal"
    )
    play = widgets.Play(
        value=0,
        min=0,
        max=minlength-1,
        step=1
    )
    widgets.jslink((slider, 'value'), (play, 'value'))

    frame_container = widgets.VBox([f for _, f in frames])
    controls = widgets.HBox([play, slider])
    main_box = widgets.VBox([controls, frame_container])
    
    def _do_step(frameno):
        for clip, frame in frames:
            frame.value = image2bytes(frame2image(clip[frameno['new']]))

    slider.observe(_do_step, names="value")
    display.display(main_box)
__all__ = ["diff_frames", "show_clip", "frame_step"]
