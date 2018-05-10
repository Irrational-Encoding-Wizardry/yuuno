# -*- encoding: utf-8 -*-

# Yuuno - IPython + VapourSynth
# Copyright (C) 2017 StuxCrystal (Roland Netzsch <stuxcrystal@encode.moe>)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
from weakref import WeakKeyDictionary
from PIL.Image import Image

from traitlets import observe, default
from traitlets import HasTraits, Instance, Any

from IPython.display import Image as IPyImage

from yuuno.clip import Clip, Frame
from yuuno_ipython.ipython.feature import Feature
from yuuno_ipython.ipython.environment import Environment


class InlineFormat(HasTraits):
    """
    Represents an inline formatted object.
    """

    clip: Clip = Any()
    environment: Environment = Instance(Environment)

    first_frame: Frame = Any(allow_none=True)
    _ipy_image_cache: IPyImage = None

    @observe("clip")
    def _update_initial_frame(self, value):
        value = value['new']
        self.first_frame = value[0].result()
        self._ipy_image_cache = None

    @property
    def ipy_image(self) -> IPyImage:
        """
        Converts a clip to an image.
        """
        if self._ipy_image_cache is not None:
            return self._ipy_image_cache

        size = self.first_frame.size()
        raw = self.environment.parent.output.bytes_of(self.first_frame.to_pil())
        self._ipy_image_cache = IPyImage(
            data=raw,
            format="png",
            embed=True,
            unconfined=True,
            width=size.width,
            height=size.height
        )
        return self._ipy_image_cache

    def _repr_pretty_(self, pp, cycle):
        size = self.first_frame.size()
        pp.text(f"<{self.clip.clip!r} {size.width}x{size.height}, {len(self.clip)} frames>")

    def _repr_html_(self, *args, **kwargs):
        return self.ipy_image._repr_html_(*args, **kwargs)

    def _repr_png_(self, *args, **kwargs):
        return self.ipy_image._repr_png_(*args, **kwargs)


class Formatter(Feature):

    type_to_repr = {
        'image/png': '_repr_png_',
        # 'text/html': '_repr_html_',
        'text/plain': '_repr_pretty_'
    }

    cache: WeakKeyDictionary = Instance(WeakKeyDictionary)

    @default("cache")
    def _default__cache(self):
        return WeakKeyDictionary()

    @property
    def display_formatters(self):
        return self.environment.ipython.display_formatter.formatters

    def wrap_cached(self, obj) -> InlineFormat:
        if obj in self.cache:
            return self.cache[obj]

        clip = self.environment.parent.registry.wrap(obj)
        wrapped = InlineFormat(environment=self.environment, clip=clip)
        self.cache[obj] = wrapped
        return wrapped

    def display(self, format):
        formatter_type = self.type_to_repr.get(format)

        def _callback(obj, *args, **kwargs):
            wrapper = self.wrap_cached(obj)
            return getattr(wrapper, formatter_type)(*args, **kwargs)
        return _callback

    def initialize(self):
        for type in self.environment.parent.registry.all_types():
            self.environment.parent.log.debug(f"Registering {type!r} to IPython")
            for format in self.type_to_repr:
                cb = self.display(format)
                self.display_formatters[format].for_type(type, cb)

    def deinitialize(self):
        for type in self.environment.parent.registry.all_types():
            self.environment.parent.log.debug(f"Unregistering {type!r} from IPython")
            for format in self.type_to_repr:
                self.display_formatters[format].pop(type)
