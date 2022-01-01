# -*- encoding: utf-8 -*-

# Yuuno - IPython + VapourSynth
# Copyright (C) 2018,2022 cid-chan (Sarah <cid+yuuno@cid-chan.moe>)
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
import random
import jinja2
from IPython.display import display, HTML

from yuuno import Yuuno
from yuuno_ipython.utils import get_data_file

from yuuno.vs.utils import MessageLevel
from yuuno.vs.extension import VapourSynth

from yuuno_ipython.ipy_vs.vs_feature import VSFeature


class LogMessage(object):
    _jinja_template = None

    @classmethod
    def template(cls):
        if cls._jinja_template is None:
            path = get_data_file("html") / "log-message.html"
            with open(path, "r") as f:
                cls._jinja_template = jinja2.Template(f.read())
        return cls._jinja_template

    def __init__(self, level, message):
        self.level = level
        self.message = message

    def _repr_html_(self):
        return self.template().render({
            "random_id": hex(random.randint(0, 2**32))[2:],
            "level_class": self.level.lower(),
            "level": self.level,
            "message": self.message
        })

    def _repr_pretty_(self, p, cycle):
        p.text("[VapourSynth] %s: %s" % (self.level, self.message))


class LogWriterFeature(VSFeature):

    def _push_log_msg(self, level: MessageLevel, msg: str) -> None:
        level = level.value

        if level == MessageLevel.mtDebug:
            level = "Debug"
        elif level == MessageLevel.mtInfo:
            level = "Info"
        elif level == MessageLevel.mtWarning:
            level = "Warning"
        elif level == MessageLevel.mtCritical:
            level = "Critical"
        else:
            level = "Fatal"

        display(LogMessage(level, msg))

    def initialize(self):
        extension: VapourSynth = Yuuno.instance().get_extension('VapourSynth')
        if extension is None:
            return
        extension.log_handlers.append(self._push_log_msg)

    def deinitialize(self):
        extension: VapourSynth = Yuuno.instance().get_extension('VapourSynth')
        if extension is None:
            return
        extension.log_handlers.remove(self._push_log_msg)
