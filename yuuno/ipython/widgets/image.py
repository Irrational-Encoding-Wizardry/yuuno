import base64
import math

import ipywidgets

from yuuno.util import fake_dict
from yuuno.core.settings import settings
from yuuno.core.converter import image_to_bytes
from yuuno.ipython.widgets.widget import Widget, Jinja2Mixin


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


class Image(Jinja2Mixin, ImageWidget):
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

        self.image_layout = ipywidgets.Layout()
        self.html_layout = ipywidgets.Layout()

        if self.scale:
            self.image_layout.height = "auto"
            self.image_layout.max_width = "100%"

        self.image_widget = ipywidgets.Image(layout=self.image_layout)
        self.iw_layout = ipywidgets.Layout(display="none")
        self.iw_container = ipywidgets.Box([self.image_widget], layout=self.iw_layout)
        self.html_widget = ipywidgets.HTML(layout=self.html_layout)
        self.container = ipywidgets.HBox([self.iw_container, self.html_widget])

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
        self.iw_layout.display = "inline"
        self.html_layout.display = "none"

        self.image_widget.value = image_to_bytes(self.image)

    def render_tiled_image(self):
        self.iw_layout.display = "none"
        self.html_layout.display = "inline"
        self.html_widget.value = f = self.render_tile_html()
        print(len(f))

    def get_tile(self, row, column, *, size=None):
        size = self.convert_tile_size(size)
        pos_x = column * size
        pos_y = row * size
        return self.image.crop((
            pos_x,                               pos_y,
            min(pos_x + size, self.image.width), min(pos_y + size, self.image.height)
        ))

    def get_tile_count(self, *, size=None):
        size = self.convert_tile_size(size)
        return math.ceil(self.image.height/size), math.ceil(self.image.width/size)

    def render_tile_html(self):
        @fake_dict
        def tiles(row):
            @fake_dict
            def column_tiles(column):
                return self.get_bytelink(image_to_bytes(self.get_tile(row, column)))
            return column_tiles
        row_count, column_count = self.get_tile_count()

        return self.get_html(
            {'rows': row_count, 'columns': column_count, 'tiles': tiles, 'viewport': self.viewport},
            'tiles.html'
        )

    def get_widget(self):
        return self.container

    @property
    def show_tiled(self):
        if self.image is None:
            return None

        if self.tiled is not None:
            return self.tiled

        return self.image.width > 5*1920 or self.image.height > 5*1080

    @staticmethod
    def convert_tile_size(size=None):
        if size is None:
            return int(settings.tile_size)
        return size


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
