import math
import ipywidgets as widgets
import vapoursynth as vs
from IPython import display
from PIL.Image import NEAREST

from yuuno.vsimg import frame2image, image2bytes, get_bytelink

TILE_SIZE = 500


def _diff_frames_2(f1, f2=None, frameno=0, cap_size=True, force_width=None):
    if f2 is None:
        f2 = f1[1:]
    f1 = image2bytes(frame2image(f1[frameno]))
    f2 = image2bytes(frame2image(f2[frameno]))

    display.display(widgets.HTML(value="".join(['''
<div>
<style scoped>
div.vs-diff-container.vs-diff-two-frames > img {
   display: none;
   margin-top: 0 !important;
   ''',("max-width: 100%; height: auto;" if cap_size else ""),'''
   ''',(("width: %s" % force_width) if force_width is not None else ""), '''
}

div.vs-diff-container.vs-diff-two-frames:not(:hover) > img.vs-diff-first,
div.vs-diff-container.vs-diff-two-frames:hover > img.vs-diff-second {
   display: block;
}
</style>
<div class="vs-diff-container vs-diff-two-frames">
<img class="vs-diff-first" src="''',get_bytelink(f1),'''">
<img class="vs-diff-second" src="''',get_bytelink(f2),'''">
</div>
</div>
'''])))

def diff_frames(*clips, frameno=0, **kwargs):
    if len(clips) == 0:
        clips = tuple(vs._stored_outputs.items())
    elif len(clips) < 3:
        return _diff_frames_2(*clips, frameno=frameno, **kwargs)
    else:
        clips = tuple(enumerate(clips))

    image = widgets.Image(layout=widgets.Layout(max_width="100%", height="auto"))

    def _set_image(clip):
        img = image2bytes(frame2image(clip, frameno=frameno))
        def _handler(*args, **kwargs):
            image.value = img
        return _handler

    _set_image(clips[0][0])()

    buttons = []
    for i, clip in clips:
        button = widgets.Button(description=str(i))
        button.on_click(_set_image(clip))
        buttons.append(button)

    buttonrow = widgets.HBox(buttons)
    display.display(widgets.VBox([buttonrow, image]))

def inspect_frame(
        clip,
        sizes=((0.5,'50%'), (1,'100%'), (2,'200%'), (3,'300%')),
        default=1,
        frameno=0,
        max_size=(960, 540)):

    tiled_label = widgets.Label()
    frame = frame2image(clip[frameno])
    
    current = widgets.HTML()

    def _generate_html(width, height):
        def _tile_at(img, size, x, y):
            pos_x = x*size
            pos_y = y*size
            return img.crop((pos_x, pos_y, min(pos_x+size, width), min(pos_y+size, height)))
        def _tiles(resized):
            for row in range(math.ceil(height/TILE_SIZE)):
                yield '<div class="vs-scaler-tile-row">'
                for column in range(math.ceil(width/TILE_SIZE)):
                    img = _tile_at(resized, TILE_SIZE, column, row)
                    yield ''.join([
                        '<img class="vs-scaler-tile vs-scaler-tile-row-',
                        str(row),
                        ' vs-scaler-tile-column-',
                        str(column),
                        '" src="',
                        get_bytelink(image2bytes(img)),
                        '">'
                    ])
                yield '</div>'
        resized = frame.resize((int(width), int(height)), NEAREST)
        tiled = width > 5*1920 or height > 5*1080
        if tiled:
            container="".join(_tiles(resized))
        else:
            container = ''.join([
                '<img class="vs-scaler-image" src="',
                get_bytelink(image2bytes(resized)),'">'
            ])
        tiled_label.value = "Large image" if tiled else ""
        return "".join(['''
<div>
<style scoped>
div.vs-scaler {
  max-width: ''',str(max_size[0]),'''px;
  max-height: ''',str(max_size[1]),'''px;
  overflow: auto;
}

div.vs-scaler.vs-scaler-tiled > div.vs-scaler-tile-row {
    white-space: nowrap;
}
div.vs-scaler > div > img {
   margin: 0 !important;
   image-rendering: pixelated;
   -ms-interpolation-mode: nearest-neighbor;  /* IE (non-standard property) */
   display: inline;
}
</style>
<div class="vs-scaler ''',("vs-scaler-tiled" if tiled else ""),'''">''',container,'''</div>'''])
    
    def set_size(sz):
        def _handler(*args, **kwargs):
            current.value = _generate_html(sz*clip.width, sz*clip.height)
        return _handler
    set_size(default)()

    buttons = []
    if isinstance(sizes, dict):
        sizes = sizes.items()
    for size, name in sizes:
        button = widgets.Button(description=name)
        button.on_click(set_size(size))
        buttons.append(button)
    buttons.append(tiled_label)
    buttonrow = widgets.HBox(buttons)
    display.display(widgets.VBox([buttonrow, current]))

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
            height = clip.height,
            layout=widgets.Layout(
                max_width="100%",
                height="auto"
            )
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
    speed_slider = widgets.IntSlider(
        value=500,
        min=100,
        max=2000,
        step=20
    )

    frame_container = widgets.VBox([f for _, f in frames])

    speed_container = widgets.HBox([widgets.Label("Speed"), speed_slider])
    position_container = widgets.HBox([widgets.Label("Frame"), play, slider])
    controls = widgets.VBox([speed_container, position_container])
    main_box = widgets.VBox([controls, frame_container])

    widgets.jslink((play, "value"), (slider, "value"))
    widgets.jslink((speed_slider, "value"), (play, "interval"))
    
    def _do_step(frameno):
        rendered_frames = []
        for clip, frame in frames:
            rendered_frames.append((frame, image2bytes(frame2image(clip[frameno['new']]))))

        for widget, frame in rendered_frames:
            widget.value = frame

    slider.observe(_do_step, names="value")
    display.display(main_box)

__all__ = ["diff_frames", "show_clip", "frame_step", "inspect_frame"]
