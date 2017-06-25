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


from yuuno.ipython.magic import MagicFeature, Magics
from IPython.core.magic import line_magic, magics_class
from IPython.display import display


@magics_class
class AppDrawer(Magics):

    def app_magic(self, app, line):
        local_ns = {'__app': app}
        return eval(f"__app({line})", self.shell.user_ns, local_ns)

    @line_magic
    def preview(self, line):
        from yuuno.ipython.apps.preview import Preview
        return self.app_magic(Preview, line)

    @line_magic
    def diff(self, line):
        from yuuno.ipython.apps.diff import Diff
        display(self.app_magic(Diff, line))
        return None

    @line_magic
    def compare(self, line):
        from yuuno.ipython.apps.compare import Compare
        return self.app_magic(Compare, line)

    @line_magic
    def inspect(self, line):
        from yuuno.ipython.apps.inspect import Inspect
        return self.app_magic(Inspect, line)


class Apps(MagicFeature):

    def initialize(self):
        self.register_magics(AppDrawer)
