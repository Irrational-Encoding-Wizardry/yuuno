import sys


__all__ = ["popen", "interrupt_process"]


if sys.platform == "win32":
    from yuuno.ipython.os.win32 import popen, interrupt_process
else:
    from yuuno.ipython.os.unix import popen, interrupt_process
