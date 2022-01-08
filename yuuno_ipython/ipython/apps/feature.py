# -*- encoding: utf-8 -*-

# Yuuno - IPython + VapourSynth
# Copyright (C) 2017,2018 cid-chan (Sarah <cid+yuuno@cid-chan.moe>)
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

from yuuno_ipython.ipython.magic import MagicFeature, Magics

from IPython.core.magic import line_magic, magics_class
from IPython.display import display


@magics_class
class AppDrawer(Magics):

    def app_magic(self, app, line):
        local_ns = {'__app': app}
        return eval(f"__app({line})", self.shell.user_ns, local_ns)

    @line_magic
    def preview(self, line):
        from yuuno_ipython.ipython.apps.preview import Preview
        return self.app_magic(Preview, line)


class Apps(MagicFeature):

    def initialize(self):
        self.register_magics(AppDrawer)

        from yuuno_ipython.ipython.apps.preview import Preview
        self.environment.parent.namespace["Preview"] = Preview

    def deinitialize(self):
        del self.environment.parent.namespace["Preview"]
