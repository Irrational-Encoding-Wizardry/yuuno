import ast
import sys
import shlex
import signal
import subprocess
from threading import Thread

import vapoursynth
from IPython import get_ipython
from yuuno.magic.util import line_cell_magic


def retrieve_clip(expr, local_ns=None):
    """
    Retrieves the clip from the simple expression given.
    """
    ipy = get_ipython()
    expr = ipy.input_transformer_manager.transform_cell(expr)
    expr_ast = ipy.compile.ast_parse(expr)
    expr_ast = ipy.transform_ast(expr_ast)

    code = ipy.compile(ast.Expression(expr_ast.body[0].value), '<encode-expr>', 'eval')
    return eval(code, ipy.user_ns, local_ns)


class ClipPiper(Thread):
    """
    Handles
    """

    def __init__(self, clip, process):
        super(ClipPiper, self).__init__()
        self.clip = clip
        self.process = process
        self.alive = False

    def run(self):
        self.alive = True
        try:
            self.clip.output(self.process.stdin, y4m=True, progress_update=self.ensure_dealive)
        except Exception:
            if not self.alive:
                return
            raise
        self.process.stdin.close()

    def ensure_dealive(self, cur_f, total_f):
        if not self.alive:
            self.process.stdin.close()
            raise KeyboardInterrupt

    def stop_serving(self):
        self.alive = False


class OutputReader(Thread):
    """
    Shows the output
    """

    def __init__(self, pipe, file):
        super(OutputReader, self).__init__()
        self.pipe = pipe
        self.file = file
        self.alive = False

    def run(self):
        self.alive = True
        while self.alive:
            ld = self.pipe.read(1)
            if not ld:
                continue
            print(ld.decode('utf-8').replace("\r\n", ""), end="", file=self.file)

    def stop_serving(self):
        self.alive = False

if sys.platform == "win32":
    def popen(*args, **kwargs):
        if "creationflags" not in kwargs:
            kwargs["creationflags"] = 512
        return subprocess.Popen(*args, **kwargs)

    def interrupt_process(process):
        print("Due to limitations of the operating system, we can only kill the process.", file=sys.stderr)
        process.send_signal(signal.CTRL_BREAK_EVENT)
else:
    popen = subprocess.Popen

    def interrupt_process(process):
        process.send_signal(signal.CTRL_C_EVENT)


def run_encoder(clip, cmd):
    """
    Starts the encoding process...
    """
    process = popen(shlex.split(cmd),
                    stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    d_thread = ClipPiper(clip, process)
    o_thread = OutputReader(process.stdout, sys.stdout)
    e_thread = OutputReader(process.stderr, sys.stderr)

    d_thread.start()
    o_thread.start()
    e_thread.start()

    try:
        while True:
            d_thread.join(timeout=.5)
            o_thread.join(timeout=.5)
            e_thread.join(timeout=.5)

    except KeyboardInterrupt:
        print("\nInterrupted", file=sys.stderr)
        d_thread.stop_serving()
        interrupt_process(process)
        try:
            process.wait(timeout=10)
        except TimeoutError:
            pass
        process.terminate()

    except:
        process.terminate()
        raise

    finally:
        d_thread.stop_serving()
        o_thread.stop_serving()
        e_thread.stop_serving()

        process.wait()
        d_thread.join()
        o_thread.join()
        e_thread.join()

        try:
            print(process.stdout.read().decode('utf-8'), end="")
        except ValueError:
            pass
        try:
            print(process.stderr.read().decode('utf-8'), end="")
        except ValueError:
            pass

    return process.returncode


@line_cell_magic
def encode(line, cell=None, local_ns=None):
    """
    Encodes a clip given by the first word in the first line.

    The encoder receives y4m output.
        >>> %encode clip x264 --y4m - ...
        y4m [info]: 800x450p 0:0 @ 62500/2609 fps (cfr)
        x264 [info]: using cpu capabilities: MMX2 SSE2Fast SSSE3 SSE4.2 AVX
        x264 [info]: profile High, level 3.0
    or
        >>> %%encode x264 --y4m - ...
        ... clip
        y4m [info]: 800x450p 0:0 @ 62500/2609 fps (cfr)
        x264 [info]: using cpu capabilities: MMX2 SSE2Fast SSSE3 SSE4.2 AVX
        x264 [info]: profile High, level 3.0

    """
    if cell is not None:
        cmd = line
        expr = cell
    else:
        try:
            expr, cmd = line.split(" ", 1)
        except ValueError:
            return "No command given"

    clip = retrieve_clip(expr, local_ns)

    if not isinstance(clip, vapoursynth.VideoNode):
        try:
            clip = vapoursynth.get_output(clip)
        except KeyError as e:
            return "The expression must compute to a VideoNode not '%r'." % clip

    return run_encoder(clip, cmd)
