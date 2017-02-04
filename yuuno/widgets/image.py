import math
import base64
import ipywidgets
from yuuno.widgets.widget import Widget
from yuuno.glue import image_to_bytes


TILE_SIZE = 540


class ImageWidget(Widget):

    def __init__(self, image=None):
        self._image = image

    @staticmethod
    def get_bytelink(data, format="image/png"):
        return "data:%s;base64,%s" % (format, base64.b64encode(data).decode())

    def update_image(self):
        raise NotImplemented

    @property
    def image(self):
        return self._image
    @image.setter
    def image(self, value):
        self._image = value
        self.update_image()


class RawImage(ImageWidget):

    def __init__(self, image=None, classes=""):
        super(RawImage, self).__init__(image)
        self.classes = classes

    def _repr_html_(self):
        return ''.join([
            '<img class="', self.classes, '" src="', self.get_bytelink(image_to_bytes(self.image)), '">'
        ])

    def get_widget(self):
        return ipywidgets.Image(value=self.image)


class Image(ImageWidget):
    """
    Represents an image.
    """

    def __init__(self, image=None, tiled=None, scale=True, tile_viewport=("960px", "540px"), aperture=True):
        """
        Stores the data for an image.

        :param tiled:  Show the image as tiles.
        :param image:  Show the image as is.
        """
        super(Image, self).__init__(image)
        self.tiled = tiled
        self.scale = scale
        self.aperture = aperture
        self.viewport = tile_viewport

        self.image_layout = ipywidgets.Layout(display="none")
        self.html_layout = ipywidgets.Layout(display="none")

        if self.scale:
            self.image_layout.height = "auto"
            self.image_layout.max_width = "100%"

        self.image_widget = ipywidgets.Image(layout=self.image_layout)
        self.html_widget = ipywidgets.HTML(layout=self.html_layout)
        self.container = ipywidgets.HBox([self.image_widget, self.html_widget])

    def clear_widgets(self):
        if not self.aperture:
            self.image_widget.image = b""
            self.html_widget.value = ""

    def update_image(self):
        """
        Ensures the right widget is shown.
        :return:
        """
        self.clear_widgets()

        if not self.show_tiled:
            self.render_untiled_image()
        else:
            self.render_tiled_image()

    def render_untiled_image(self):
        self.image_layout.display = "inline"
        self.html_layout.display = "none"

        self.image_widget.value = image_to_bytes(self.image)

    def render_tiled_image(self):
        self.image_layout.display = "none"
        self.html_layout.display = "inline"

        self.html_widget.value = ''.join(self._render_tiled_image())

    def get_tile(self, row, column, *, size=TILE_SIZE):
        pos_x = column * size
        pos_y = row * size
        return self.image.crop((
            pos_x,                               pos_y,
            min(pos_x + size, self.image.width), min(pos_y + size, self.image.height)
        ))

    def get_tile_count(self, *, size=TILE_SIZE):
        return math.ceil(self.image.height/size), math.ceil(self.image.width/size)

    def _render_tiled_image(self):
        row_count, column_count = self.get_tile_count()
        yield '<div class="vs-image-tiled">'
        yield '''
        <style scoped>
        .vs-image-tiled-main {
            overflow: scroll;
            max-width: %s;
            max-height: %s;
        }
        .vs-image-tiled-wrapper > .vs-image-tiled-row {
            white-space: nowrap;
        }

        .vs-image-tiled-wrapper > .vs-image-tiled-row > img {
            margin: 0 !important;
            image-rendering: pixelated;
            -ms-interpolation-mode: nearest-neighbor;  /* IE (non-standard property) */
            display: inline;
        }
        </style>
        '''%(self.viewport[0], self.viewport[1])
        yield '<div class="vs-image-tiled-main"><div class="vs-image-tiled-wrapper">'

        for r in range(row_count):
            yield '<div class="vs-image-tiled-row">'
            for c in range(column_count):
                tile = self.get_tile(r, c)
                yield ''.join([
                    '<img class="vs-image-tiled-img" src="', self.get_bytelink(image_to_bytes(tile)), '">'
                ])
            yield '</div>'

        yield '</div>'
        yield '</div>'
        yield '</div>'

    def get_widget(self):
        return self.container

    @property
    def show_tiled(self):
        if self.image is None:
            return None

        if self.tiled is not None:
            return self.tiled

        return self.image.width > 5*1920 or self.image.height > 5*1080


#################################################################################################


class BaseImageChooser(Image):

    def __init__(self, images, callback, *args, cache=True, **kwargs):
        super(BaseImageChooser, self).__init__(None, *args, **kwargs)
        self.callback = callback
        self.cache = cache
        self._cache = {}

        self.buttons_container = ipywidgets.ToggleButtons()
        self.buttons_container.observe(self.on_set, names="value")

        self.images = images

    @property
    def images(self):
        return self._images
    @images.setter
    def images(self, value):
        self._images = value
        self._cache = {}
        self.update_image_list()

    def update_image_list(self):
        self.buttons_container.options = self.images
        if len(self.images) > 1:
            self.buttons_container.value = self.images[0]

    def on_set(self, value):
        value = value['new']
        if value in self._cache:
            result = self._cache[value]
        else:
            result = self.callback(value)
            if self.cache:
                self._cache[value] = result

        self.image = result

    def clear_cache(self):
        self._cache = {}

    def get_widget(self):
        return ipywidgets.VBox([self.buttons_container, super(BaseImageChooser, self).get_widget()])


class ImageChooser(BaseImageChooser):
    def __init__(self, images, *args, **kwargs):
        super(ImageChooser, self).__init__(images, self.set_image_raw, *args, **kwargs)

    @property
    def images(self):
        return self._images
    @images.setter
    def images(self, value):
        self._images = list(v[0] for v in value)
        self._raw_images = dict(value)
        self.update_image_list()

    def set_image_raw(self, value):
        return self._raw_images[value]