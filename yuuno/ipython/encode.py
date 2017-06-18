import io
import ast
import sys
import time
import shlex
import subprocess
from threading import Thread

from traitlets import Instance, default

from IPython.core.magic import Magics, magics_class
from IPython.core.magic import line_cell_magic

from yuuno import Yuuno
from yuuno.ipython.magic import MagicFeature
from yuuno.ipython.os import popen, interrupt_process
from yuuno.ipython.environment import YuunoIPythonEnvironment


class ClipFeeder(Thread):

    def __init__(self, clip, pipe, *args, **kwargs):
        super(ClipFeeder, self).__init__(name=f"<YuunoClipFeeder {clip!r} to {pipe!r}>")
        self.clip = clip
        self.pipe = pipe

        self.args = args
        self.kwargs = kwargs

    def stop(self):
        self.pipe.close()
        self.join()

    def run(self):
        try:
            self.clip.output(self.pipe, *self.args, **self.kwargs)
        except Exception as e:
            if e.__class__.__name__ != "Error":
                raise
        self.pipe.close()


class OutputFeeder(Thread):

    def __init__(self, process, pipe, output):
        super(OutputFeeder, self).__init__(name=f"<YuunoOutputFeeder {pipe!r} to {output!r}>")
        self.process = process
        self.pipe = pipe
        self.output = output

    def run(self):
        while self.process.poll() is None:
            ld = self.pipe.read(1).decode("utf-8")
            if not ld:
                time.sleep(0)
                continue
            print(ld, end='', file=self.output)

        res = self.pipe.read().decode("utf-8")
        if res:
            print(res, file=self.output)


@magics_class
class EncodeMagic(Magics):
    """
    Encode magics.
    """

    environment: YuunoIPythonEnvironment = Instance(YuunoIPythonEnvironment)

    @default("environment")
    def _default_environment(self):
        return Yuuno.instance().environment

    def begin_encode(self, clip, commandline, stdout=None, **kwargs):
        """
        Implements the actual encoding process

        :param clip:        The clip to encode.
        :param commandline: The command to execute
        :param stdout:      Where to send the stdout.
        :return:            The return code.
        """

        commandline = shlex.split(commandline)

        process = popen(
            commandline,
            stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=subprocess.PIPE,
        )

        feeder = ClipFeeder(clip, process.stdin, **kwargs)
        feeder.start()

        if stdout is None:
            stdout = sys.stdout

        stderr = OutputFeeder(process, process.stderr, sys.stderr)
        stderr.start()
        stdout = OutputFeeder(process, process.stdout, stdout)
        stdout.start()

        try:
            while process.poll() is None:
                if not feeder.is_alive():
                    try:
                        process.wait(timeout=0.5)
                    except subprocess.TimeoutExpired:
                        pass
                else:
                    feeder.join(timeout=0.5)

        except KeyboardInterrupt:
            interrupt_process(process)
            feeder.stop()
            try:
                process.wait(timeout=10)
            except TimeoutError:
                process.terminate()

        except:
            process.terminate()
            raise

        finally:
            stderr.join()
            stdout.join()
            time.sleep(.5)

        return process.returncode

    def execute_code(self, expr, file):
        ipy = self.environment.ipython
        expr = ipy.input_transformer_manager.transform_cell(expr)
        expr_ast = ipy.compile.ast_parse(expr)
        expr_ast = ipy.transform_ast(expr_ast)

        code = ipy.compile(ast.Expression(expr_ast.body[0].value), file, 'eval')
        return eval(code, ipy.user_ns, {})

    def prepare_encode(self, line, cell, stdout=None):
        if cell is None:
            cell, line = line.split(" ", 1)

        y4m = line.startswith("--y4m")
        if y4m:
            line = line[6:]
        commandline = self.environment.ipython.var_expand(line)
        clip = self.execute_code(cell, "<yuuno.ipython encode>")

        return self.begin_encode(clip, commandline, stdout=stdout, y4m=y4m)

    @line_cell_magic
    def encode(self, line, cell=None):
        """
        Encodes the video directly displaying the output.
        :param line:  The line
        :param cell:  The cell
        :return: The result-code
        """
        return self.prepare_encode(line, cell)

    @line_cell_magic
    def render(self, line, cell=None):
        """
        Renders the video into a bytes-io buffer.
        :param line: The line
        :param cell: The cell
        :return: The IO.
        """
        res = io.BytesIO()
        self.prepare_encode(line, cell, stdout=res)
        return res


class Encode(MagicFeature):

    def initialize(self):
        self.register_magics(EncodeMagic)
