import runpy
import types
from typing import Dict, Optional

import vapoursynth

from IPython.core.magic import Magics, magics_class
from IPython.core.magic import line_cell_magic

from yuuno.ipython.magic import MagicFeature
from yuuno.ipython.utils import execute_code

from yuuno.ipy_vs.vs_feature import VSFeature


class VapourSynthEnvironment(object):

    def __init__(self):
        self.previous_outputs = {}
        self.old_outputs = None

    @staticmethod
    def get_global_outputs():
        if hasattr(vapoursynth, "get_outputs"):
            return vapoursynth.get_outputs()
        return types.MappingProxyType(vapoursynth._get_output_dict("OutputManager.get_outputs"))

    def _set_outputs(self, output_dict):
        vapoursynth.clear_outputs()
        for k, v in output_dict.items():
            v.set_output(k)

    @property
    def outputs(self):
        if self.old_outputs is None:
            return self.previous_outputs
        return self.get_global_outputs()

    def __enter__(self):
        self.old_outputs = self.get_global_outputs().copy()
        self._set_outputs(self.previous_outputs)

    def __exit__(self, exc, val, tb):
        self.previous_outputs = self.get_global_outputs().copy()
        self._set_outputs(self.old_outputs)
        self.old_outputs = None


@magics_class
class RunVPyMagic(Magics):
    """
    Implements the Magics
    """

    @line_cell_magic
    def runvpy(self, line: str, cell: Optional[str]=None) -> Dict[int, vapoursynth.VideoNode]:
        if cell is None:
            return self.runvpy_line(line)

        return self.runpy_cell(line, cell)

    def runvpy_line(self, line: str) -> Dict[int, vapoursynth.VideoNode]:
        outputs = VapourSynthEnvironment()
        with outputs:
            runpy.run_path(line, {}, "__vapoursynth__")

        return outputs.outputs

    def runvpy_cell(self, line: str, cell: str) -> Dict[int, vapoursynth.VideoNode]:
        outputs = VapourSynthEnvironment()

        with outputs:
            execute_code(cell, "%%vpy")

        raw_split = line.split(" ", 2)
        var_name = raw_split[0]
        if len(raw_split) == 1:
            self.environment.ipython.push({var_name: outputs.outputs})
        else:
            index = int(raw_split[1])
            self.environment.ipython.push({line.split()[0]: outputs.outputs[index]})


class RunVPy(VSFeature, MagicFeature):

    def initialize(self):
        self.register_magics(RunVPyMagic)
