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
import shutil
from collections import ChainMap
from contextlib import contextmanager

from IPython.display import display

from yuuno_ipython.ipython.apps.preview import Preview
from yuuno_ipython.ipy_vs.vs_feature import VSFeature
from yuuno_ipython.ipy_vs.encode import EncodeMagic, _running as running_encodes
from yuuno_ipython.ipython.magic import MagicFeature
from yuuno_ipython.ipython.utils import execute_code

from yuuno import Yuuno
from yuuno.vs.utils import VapourSynthEnvironment

from IPython.core.magic import Magics, magics_class
from IPython.core.magic import cell_magic


@contextmanager
def _noop():
    return (yield)

@magics_class
class EditorMagics(Magics):
    preview = Preview(None)
    encode = EncodeMagic()

    yuuno_header = """
    import vapoursynth as vs
    from vapoursynth import core
    """

    @property
    def yuuno(self):
        return Yuuno.instance()

    @property
    def vsscript_feature(self) -> 'Use_VSScript':
        from yuuno_ipython.ipy_vs.vsscript import Use_VSScript
        for feature in self.yuuno.get_extension('ipy_vs').features:
            if isinstance(feature, Use_VSScript):
                return feature
        return None

    def parse_parameters(self, line):
        data = {}
        current_flag = None
        current_info = []
        rest_type = None
        rest = None
        for word in line.split():
            if rest is not None:
                rest.append(word)
                continue
            elif word in ("--", '|'):
                if current_flag is not None:
                    data[current_flag] = current_info
                current_flag = None
                rest = []
                rest_type = word
            elif word.startswith("--"):
                if current_flag is not None:
                    data[current_flag] = current_info

                current_flag = word[2:]
                current_info = []
            else:
                current_info.append(word)
        
        if rest is not None:
            data['--'] = rest

        if current_flag is not None:
            data[current_flag] = current_info

        return data

    @cell_magic
    def vspipe(self, line, cell):
        line = self.parse_parameters(line)

        if "help" in line:
            print("%%vspipe [--outputindex <OUTPUT-ID>] [OPTIONS] | [commandline]")
            print()
            print("%%vspipe emulates the vspipe-binary. It uses %encode under the hood.")
            print("Note that only one %%vspipe can run at the same time.")
            print()
            print("Options special to %%vspipe")
            print("--outputindex <OUTPUT-ID>   - Select output index")
            print("--y4m                       - Add YUV4MPEG headers to output")
            print("--start N                   - Set the output frame range (first frame)")
            print("--end N                     - Set the output frame range (last frame)")
            print("--requests N                - Set the number of concurrent frame requests")
            print()
            print("General options")
            print("--reset-core          - Reset the core before running the cell.")
            print("--isolate-core        - Use a temporary core for the encode.")
            print("--isolate-variables   - Make sure that variables set inside this cell do not affect the global environment.")
            return

        if len(running_encodes) > 0:
            print("There is already an encode running.")
            print("Please stop or finish the encode(s) and try again. Use %reattach to find running encodes.")
            return

        if "--" not in line and "|" not in line:
            print("Please provide a valid command-line.")
            return

        main = int(line.get("outputindex", [0])[0])
        start = None
        if "start" in line:
            start = int(line["start"][0])
        end = None
        if "end" in line:
            end = int(line["end"][0])+1
        requests = None
        if "requests" in line:
            requests = int(line["requests"][0])

        reset_core = False
        if self.vsscript_feature is not None and not VapourSynthEnvironment.single() and "reset-core" in line:
            reset_core = True

        ns = self.yuuno.environment.ipython.user_ns
        if "isolate-variables" in line:
            ns = ChainMap({}, ns)

        if reset_core:
            self.vsscript_feature.reset_script()

        script = _noop()
        after_exit = None
        if "isolate-core" in line:
            from yuuno_ipython.ipy_vs.vsscript import VSScriptWrapper
            script = VSScriptWrapper.with_name("vspipe-emulation")
            after_exit = lambda: script.dispose()

        with script:
            env = VapourSynthEnvironment()
            with env:
                execute_code(cell, "<vspreview>", True, ns=ns)
            outputs = env.outputs

        if main not in env.outputs:
            print("Couldn't find your output. Aborting.")
            return

        clip = outputs[main][start:end]
        encode = self.encode.begin_encode(clip, ' '.join(line['--']), y4m=('y4m' in line), prefetch=requests, after_exit=after_exit)
        display(encode)


    @cell_magic
    def vspreview(self, line, cell):
        line = self.parse_parameters(line)
        if "help" in line:
            print("%%vspreview [--main <OUTPUT-ID>] [--diff <OUTPUT-ID>] [OPTIONS]")
            print()
            print("%%vspreview shows a preview of the given script. It can diff two outputs with --diff.")
            print("It does not modify the outputs of the vapoursynth environment.")
            print("You can use --isolate-variables to sandbox changes of the environment to the cell. Any changes to variables")
            print("will not be visible outside the cell.")
            print()
            print("--main and --diff are ignored if there are less than 3 output-clips.")
            print()
            print("Options special to %%vspreview")
            print("--main <OUTPUT-ID>    - Select the output number to show as the main (defaults to 0 if not given.)")
            print("--diff <OUTPUT-IDS>   - Set the id to compare to")
            print()
            print("General options")
            print("--reset-core          - Reset the core.")
            print("--isolate-variables   - Make sure that variables set inside this cell do not affect the global environment.")
            return

        reset_core = False
        if self.vsscript_feature is not None and not VapourSynthEnvironment.single() and "reset-core" in line:
            reset_core = True
        
        diff = None
        if "diff" in line:
            diff = 1 if len(line["diff"]) == 0 else int(line["diff"][0])
        
        main = 1
        if "main" in line:
            if len(line["main"]) == 0:
                raise ValueError("You need to provide an output-id")
            main = int(line["main"][0])

        ns = self.yuuno.environment.ipython.user_ns
        if "isolate-variables" in line:
            ns = ChainMap({}, ns)

        # Reset the actual script
        if reset_core:
            self.vsscript_feature.reset_script()

        env = VapourSynthEnvironment()
        with env:
            execute_code(cell, "<vspreview>", True, ns=ns)
            
        outputs = env.outputs
        if len(outputs) == 1:
            main = next(iter(outputs))

        elif len(outputs) == 2:
            oiter = iter(sorted(iter(outputs)))
            main = next(oiter)
            diff = next(oiter)

        self.preview.clip = outputs.get(main, None)
        self.preview.diff = None if diff is None else outputs.get(diff, None)

        display(self.preview)


class StatefulEditorFeature(VSFeature, MagicFeature):

    def initialize(self):
        self.register_magics(EditorMagics)
