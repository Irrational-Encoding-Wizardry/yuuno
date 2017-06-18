import signal
import subprocess


popen = subprocess.Popen


def interrupt_process(process):
    process.send_signal(signal.SIGINT)
