# -*- encoding: utf-8 -*-

# Yuuno - IPython + VapourSynth
# Copyright (C) 2017 cid-chan (Sarah <cid+yuuno@cid-chan.moe>)
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
from yuuno.audio import Audio
from yuuno_ipython.ipython.feature import Feature
from yuuno_ipython.ipython.environment import Environment
from yuuno_ipython.ipython.apps.preview import Preview
from yuuno_ipython.ipython.apps.audio import AudioWidget



class AbstractInlineFormat(HasTraits):
    clip: Clip = Any()
    environment: Environment = Instance(Environment)

    REPR_TYPES = {
    }


    def _repr_mimebundle_(self, include=None, exclude=None):
        data_dict = {}
        md_dict = {}

        mimes = set(include) if include is not None else set(self.REPR_TYPES.keys())
        mimes &= set(self.REPR_TYPES.keys())
        if exclude is not None:
            mimes ^= set(exclude)

        for mime in mimes:
            funcname = self.REPR_TYPES[mime]

            if not hasattr(self, funcname):
                continue

            raw = getattr(self, funcname)()
            if isinstance(raw, tuple) and len(raw) == 2:
                data, md = raw
            else:
                data = raw
                md = None

            if data is None:
                continue

            data_dict[mime] = data
            if md is not None:
                md_dict[mime] = md

        return data_dict, md_dict



class InlineFormatAudio(AbstractInlineFormat):

    preview: AudioWidget = Instance(AudioWidget, allow_none=True)

    REPR_TYPES = {
        "text/plain": "_repr_pretty",
        'application/vnd.jupyter.widget-view+json': '_repr_player'
    }

    @observe("clip")
    def _update_initial_frame(self, value):
        value = value['new']
        self.preview.clip = value

    @default("preview")
    def _default_preview(self):
        return AudioWidget(self.clip)

    def _repr_pretty(self):
        return f"<Audio {self.clip.format()!r} (backed: {self.clip.clip!r})>"

    def _repr_player(self):
        if self.preview._view_name is None:
            return

        return self.preview.get_view_spec()


class InlineFormatVideo(AbstractInlineFormat):
    """
    Represents an inline formatted object.
    """

    preview: Preview = Instance(Preview, allow_none=True)

    first_frame: Frame = Any(allow_none=True)
    _ipy_image_cache: IPyImage = None

    @observe("clip")
    def _update_initial_frame(self, value):
        value = value['new']
        self.first_frame = value[0].result()
        self._ipy_image_cache = None
        self.preview.clip = value

    @default("preview")
    def _default_preview(self):
        return Preview(self.clip)

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

    REPR_TYPES = {
        'image/png': '_repr_png',
        'text/plain': '_repr_pretty',
        'application/vnd.jupyter.widget-view+json': '_repr_preview'
    }

    def _repr_pretty(self):
        size = self.first_frame.size()
        return f"<{self.clip.clip!r} {size.width}x{size.height}, {len(self.clip)} frames>"

    def _repr_png(self, *args, **kwargs):
        return self.ipy_image._repr_png_(*args, **kwargs)

    def _repr_preview(self):
        if self.preview._view_name is None:
            return

        return self.preview.get_view_spec()


def InlineFormat(environment, clip):
    if isinstance(clip, Audio):
        return InlineFormatAudio(environment=environment, clip=clip)
    else:
        return InlineFormatVideo(environment=environment, clip=clip)


class Formatter(Feature):
    cache: WeakKeyDictionary = Instance(WeakKeyDictionary)
    
    @default("cache")
    def _default__cache(self):
        return WeakKeyDictionary()

    @property
    def display_formatters(self):
        return self.environment.ipython.display_formatter

    def wrap_cached(self, obj) -> Any:
        if obj in self.cache:
            return self.cache[obj]

        clip = self.environment.parent.registry.wrap(obj)
        wrapped = InlineFormat(environment=self.environment, clip=clip)
        self.cache[obj] = wrapped
        return wrapped

    def display(self, obj, *args, **kwargs):
        wrapper = self.wrap_cached(obj)
        return wrapper._repr_mimebundle_(*args, **kwargs)

    def initialize(self):
        for type in self.environment.parent.registry.all_types():
            self.environment.parent.log.debug(f"Registering {type!r} to IPython")
            self.display_formatters.mimebundle_formatter.for_type(type, self.display)

    def deinitialize(self):
        for type in self.environment.parent.registry.all_types():
            self.environment.parent.log.debug(f"Unregistering {type!r} from IPython")
            self.display_formatters.mimebundle_formatter.pop(type)
