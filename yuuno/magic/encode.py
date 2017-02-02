import io
import ast
import sys
import shlex
import base64
import signal
import subprocess
from threading import Thread

import vapoursynth
from IPython import get_ipython
from IPython.display import HTML
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

    def __init__(self, clip, process, y4m=False):
        super(ClipPiper, self).__init__()
        self.clip = clip
        self.process = process
        self.alive = False
        self.y4m = y4m

    def run(self):
        self.alive = True
        try:
            self.clip.output(self.process.stdin, y4m=y4m, progress_update=self.ensure_dealive)
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

    def __init__(self, pipe, file, decode):
        super(OutputReader, self).__init__()
        self.pipe = pipe
        self.file = file
        self.decode = decode
        self.alive = False

    def run(self):
        self.alive = True
        while self.alive:
            ld = self.pipe.read(1)
            if self.decode:
                if not ld:
                    continue
                print(ld.decode('utf-8'), end="", file=self.file)
            else:
                self.file.write(ld)

    def stop_serving(self):
        self.alive = False

    def last_pass(self):
        if self.decode:
            print(self.pipe.read().decode('utf-8'), file=self.file)
        else:
            self.file.write(self.pipe.read())

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


def run_encoder(clip, cmd, stdout=sys.stdout, stderr=sys.stderr, decode_stdout=True, decode_stderr=True, y4m=True):
    """
    Starts the encoding process...
    """
    process = popen(shlex.split(cmd),
                    stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    d_thread = ClipPiper(clip, process, y4m=y4m)
    o_thread = OutputReader(process.stdout, stdout, decode_stdout)
    e_thread = OutputReader(process.stderr, stderr, decode_stderr)

    d_thread.start()
    o_thread.start()
    e_thread.start()

    try:
        while process.poll() is None:
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
        process.wait()

        o_thread.stop_serving()
        e_thread.stop_serving()

        d_thread.join()
        o_thread.join()
        e_thread.join()

        o_thread.last_pass()
        e_thread.last_pass()

    return process.returncode


def do_encode(line, cell=None, local_ns=None, stderr=sys.stderr, stdout=sys.stdout, decode_stdout=True, decode_stderr=True, y4m=True):
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
        except KeyError:
            return "The expression must compute to a VideoNode not '%r'." % clip

    return run_encoder(clip, cmd, stderr=stderr, stdout=stdout, decode_stdout=decode_stdout, decode_stderr=decode_stderr, y4m=y4m)


@line_cell_magic
def encode(line, cell=None, local_ns=None):
    """
    Encodes a clip. It will produce the y4m-output and pipe said output
    into an encoder process. The output of the encoder-process is piped
    back to the shell.
    
    *as line-magic*:
    Encodes a clip given by the first word in the first line.
    All following words are parsed as the command line passed to the process.
    
    *as cell-magic*:
    Encodes a clip that is evaluated by the cell. The arguments are the command
    line command for the encoder.

    The encoder receives y4m output.
        >>> %encode clip x264 --demuxer y4m - ...
        y4m [info]: 800x450p 0:0 @ 62500/2609 fps (cfr)
        x264 [info]: using cpu capabilities: MMX2 SSE2Fast SSSE3 SSE4.2 AVX
        x264 [info]: profile High, level 3.0
    or
        >>> %%encode x264 --demuxer y4m - ...
        ... clip
        y4m [info]: 800x450p 0:0 @ 62500/2609 fps (cfr)
        x264 [info]: using cpu capabilities: MMX2 SSE2Fast SSSE3 SSE4.2 AVX
        x264 [info]: profile High, level 3.0
    """
    return do_encode(line, cell, local_ns, y4m=True)

@line_cell_magic
def encode_raw(line, cell=None, local_ns=None):
    """
    Encodes a clip given by the first word in the first line and produes a live output of the
    console.
    
    Behaves like the `%%encode`-Magic. However the output will be as raw instead of y4m.
    """
    return do_encode(line, cell, local_ns, y4m=False)