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


import sys


__all__ = ["popen", "interrupt_process"]


if sys.platform == "win32":
    from yuuno.multi_scripts.os.win32 import popen, interrupt_process, kill_process
else:
    from yuuno.multi_scripts.os.unix import popen, interrupt_process, kill_process
