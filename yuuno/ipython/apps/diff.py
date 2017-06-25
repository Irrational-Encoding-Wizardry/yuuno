# -*- encoding: utf-8 -*-

# Yuuno - IPython + VapourSynth
# Copyright (C) 2017 StuxCrystal
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
