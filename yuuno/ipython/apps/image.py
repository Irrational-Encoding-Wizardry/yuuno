import math
import base64

from typing import Optional
from typing import Dict as TDict, List as TList

from ipywidgets import Widget as IPyWidget
from ipywidgets import Layout
from ipywidgets import Box
from ipywidgets import Image as IPyWImage, HTML as IPyWHTML

from traitlets import observe, default
from traitlets import Instance
from traitlets import Bool, Dict, List
from traitlets import CaselessStrEnum

from PIL.Image import Image as PILImage

from yuuno import Yuuno
from yuuno.ipython.utils import fake_dict
from yuuno.ipython.apps.mixins import Jinja2Mixin
from yuuno.ipython.environment import YuunoIPythonEnvironment


class Image(Box, Jinja2Mixin):
    """
    Robust container for an image.
    """

    image: Optional[PILImage] = Instance(PILImage, allow_none=True)

    _children: TList[IPyWidget] = List(Instance(IPyWidget))

    image_widget: IPyWImage = Instance(IPyWImage)
    html_widget: IPyWHTML = Instance(IPyWHTML)

    layouts: TDict[str, Layout] = Dict(key_trait=CaselessStrEnum(['image', 'html']), value_trait=Instance(Layout))
    image_layout: Layout = Instance(Layout)

    mode: Optional[str] = CaselessStrEnum(['image', 'html'], allow_none=True)
    tiled: Optional[bool] = Bool(allow_none=True)

    @property
    def environment(self) -> YuunoIPythonEnvironment:
        return Yuuno.instance().environment

    @default("image_layout")
    def _default_image_layout(self):
        return Layout(max_width="100%", height="auto")

    @default("html_widget")
    def _default_html_widget(self):
        return IPyWHTML(layout=self.layouts['html'])

    @default("_children")
    def _default__children(self):
        box = Box([self.image_widget], layout=self.layouts['image'])
        return box, self.html_widget

    @default("image_widget")
    def _default_image_widget(self):
        return IPyWImage(layout=self.image_layout, format="png")

    @default("layouts")
    def _default_layout(self):
        return {
            'html': Layout(display="none"),
            'image': Layout(display="inline")
        }

    @observe("tiled")
    def _observe_tiled(self, proposal):
        tiled: Optional[bool] = proposal.new
        if tiled is None:
            self.mode = None
        elif tiled:
            self.mode = "html"
        else:
            self.mode = "image"

    @observe("mode")
    def _observe_mode(self, proposal):
        new: Optional[str] = proposal.new

        self.layouts['html'].display = 'none'
        self.layouts['image'].display = 'none'

        if new is not None:
            self.layouts[new].display = 'inline'

    @observe("image")
    def _observe_image(self, proposal):
        self.children = self._children

        new: Optional[PILImage] = proposal['new']
        if new is None:
            self.mode = None
            return

        thr_width, thr_height = self.environment.tiling_threshold
        self.tiled = (thr_width <= new.width) or \
                     (thr_height <= new.height)
        self._update(new)

    def update(self):
        return self._update(self.image)

    def _update(self, image: PILImage):
        if self.tiled is None:
            return

        if self.tiled:
            self._update_tiled_image(image)
        else:
            self._update_single_image(image)

    def _update_single_image(self, image: PILImage):
        raw = Yuuno.instance().output.bytes_of(image)
        self.image_widget.value = raw

    @staticmethod
    def get_bytelink(image: PILImage) -> str:
        return f"data:image/png;base64,{base64.b64encode(Yuuno.instance().output.bytes_of(image)).decode()}"

    def _get_tile(self, image: PILImage, row: int, column: int) -> PILImage:
        tile_width, tile_height = self.environment.tile_size
        pos_x = column * tile_width
        pos_y = row * tile_height
        cr = image.crop((
            pos_x,                                pos_y,
            min(pos_x + tile_width, image.width), min(pos_y + tile_height, image.height)
        ))

        return cr

    def _update_tiled_image(self, image: PILImage):
        columns = math.ceil(image.width/self.environment.tile_size[0])
        rows = math.ceil(image.height/self.environment.tile_size[1])
        @fake_dict
        def row_dict(row: int) -> fake_dict:
            @fake_dict
            def column_dict(column: int) -> str:
                return self.get_bytelink(self._get_tile(image, row, column))
            return column_dict

        self.html_widget.value = self.render("tiled.html", {
            "rows": rows, "columns": columns, "tiles": row_dict,
            'sizes': self.environment.tile_viewport_size
        })
