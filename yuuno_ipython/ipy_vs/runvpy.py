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


import runpy
from typing import Dict, Optional

import vapoursynth

from IPython.core.magic import Magics, magics_class
from IPython.core.magic import line_magic, line_cell_magic

from yuuno import Yuuno

from yuuno_ipython.ipython.magic import MagicFeature
from yuuno_ipython.ipython.utils import execute_code

from yuuno_ipython.ipy_vs.vs_feature import VSFeature
from yuuno.vs.utils import VapourSynthEnvironment


@magics_class
class RunVPyMagic(Magics):
    """
    Implements the Magics
    """

    @property
    def environment(self):
        return Yuuno.instance().environment

    @line_cell_magic
    def runvpy(self, line: str, cell: Optional[str]=None) -> Dict[int, vapoursynth.VideoNode]:
        if cell is None:
            return self.runvpy_line(line)

        return self.runvpy_cell(line, cell)

    @line_magic
    def execvpy(self, line: str):
        runpy.run_path(line, {}, "__vapoursynth__")

    def runvpy_line(self, line: str) -> Dict[int, vapoursynth.VideoNode]:
        outputs = VapourSynthEnvironment()
        with outputs:
            self.execvpy(line)

        return outputs.outputs

    def runvpy_cell(self, line: str, cell: str) -> Dict[int, vapoursynth.VideoNode]:
        outputs = VapourSynthEnvironment()

        with outputs:
            execute_code(cell, '<yuuno:runvpy>')

        raw_split = line.split(" ", 2)
        var_name = raw_split[0]
        if len(raw_split) == 1:
            self.environment.ipython.push({var_name: outputs.outputs})
        else:
            index = int(raw_split[1])
            self.environment.ipython.push({line.split()[0]: outputs.outputs[index]})

        return outputs.outputs


class RunVPy(VSFeature, MagicFeature):

    def initialize(self):
        self.register_magics(RunVPyMagic)
