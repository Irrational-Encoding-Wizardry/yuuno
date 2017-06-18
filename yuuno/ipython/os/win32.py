import sys
import signal
import subprocess


def popen(*args, **kwargs):
    if "creationflags" not in kwargs:
        kwargs["creationflags"] = 512
    return subprocess.Popen(*args, **kwargs)


def interrupt_process(process):
    print("Due to limitations of the operating system, we can only kill the process.", file=sys.stderr)
    process.send_signal(signal.CTRL_BREAK_EVENT)
