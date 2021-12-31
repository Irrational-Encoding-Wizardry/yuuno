# -*- encoding: utf-8 -*-

# Yuuno - IPython + VapourSynth
# Copyright (C) 2018 cid-chan (Sarah <cid+yuuno@cid-chan.moe>)
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
import os
import functools
from pathlib import Path
from contextlib import contextmanager

from threading import Lock, Event, Thread
from queue import Queue, Empty
from concurrent.futures import Future

from ctypes import c_ubyte
from multiprocessing import Pipe, Pool, Process
from multiprocessing.sharedctypes import RawArray as Array
from multiprocessing.connection import Connection

from typing import List, Callable, Any, NamedTuple, Sequence, Dict, Union
from typing import TYPE_CHECKING

from traitlets.utils.importstring import import_item
from traitlets import Instance

from yuuno.multi_scripts.subprocess.basic_commands import BasicCommands
from yuuno.utils import future_yield_coro
from yuuno.core.environment import Environment
from yuuno.multi_scripts.utils import ConvertingMappingProxy
from yuuno.multi_scripts.script import Script
from yuuno.multi_scripts.environments import RequestManager
from yuuno.multi_scripts.subprocess.provider import ScriptProviderInfo, ScriptProvider
from yuuno.multi_scripts.subprocess.proxy import Responder, Requester
from yuuno.multi_scripts.subprocess.clip import ProxyClip

if TYPE_CHECKING:
    from yuuno.clip import Clip


# This sets the size of the frame-buffer.
# I expect 8K to be enough for now.
FRAME_BUFFER_SIZE = 7680*4320*3


class RequestQueueItem(NamedTuple):
    future: Future
    cb: Callable[[Any], Any]
    args: Sequence[Any]


class LocalSubprocessEnvironment(RequestManager, Environment):
    """
    Implements functions for a local subprocess environment.
    """
    _provider_meta: ScriptProviderInfo

    write: Connection
    read: Connection
    provider: ScriptProvider = Instance(ScriptProvider)

    _framebuffer: Array
    _framebuffer_lock: Lock

    queue: Queue
    stopped: Event
    responder: Responder
    commands: ConvertingMappingProxy[str, Callable[..., Any], Callable[[Any], Future]]

    def additional_extensions(self) -> List[str]:
        """
        Defines additional extensions that should be
        loaded inside the environment
        """
        result = []

        for ext in self._provider_meta.extensions:
            if not ext.startswith("="):
                ext = "="+ext

            name, extension = [s.strip() for s in ext.split("=")]
            extension = import_item(extension)

            if name:
                extension._name = name
            result.append(extension)

        return result

    def post_extension_load(self) -> None:
        """
        Called directly after extensions have been loaded
        (but not enabled)
        """
        self.queue = Queue()
        self.stopped = Event()
        self.handlers = {}
        self.commands = ConvertingMappingProxy(self.handlers, self._wrap2queue)

        # Let's initialize it here.
        provider_class = import_item(self._provider_meta.providercls)

        self.provider = provider_class(self.parent, **self._provider_meta.providerparams)

    def _wrap2queue(self, unwrapped: Callable[[Any], Any]) -> Callable[[Any], Future]:
        @functools.wraps(unwrapped)
        def _wrapper(data: Any) -> Future:
            fut = Future()
            self.queue.put(RequestQueueItem(fut, unwrapped, data))
            return fut
        return _wrapper

    def initialize(self) -> None:
        """
        Called by yuuno to tell it that yuuno has
        initialized to the point that it can now initialize
        interoperability for the given environment.
        """
        self.provider.initialize(self)
        self.handlers.update(BasicCommands(self.provider.get_script(), self).commands)
        self._framebuffer_lock = Lock()

    @contextmanager
    def framebuffer(self):
        with self._framebuffer_lock:
            yield memoryview(self._framebuffer).cast("B")

    def _copy_result(self, source: Future, destination: Future):
        def _done(_):
            if source.exception() is not None:
                destination.set_exception(source.exception())
            else:
                destination.set_result(source.result())
            self.queue.task_done()
        source.add_done_callback(_done)

    def run(self):
        """
        Wait for commands.
        """

        self.responder = Responder(self.read, self.write, self.commands)
        self.responder.start()

        self.responder.send(None)
        while not self.stopped.set():
            try:
                rqi: RequestQueueItem = self.queue.get(timeout=1)
            except Empty:
                continue

            if not rqi.future.set_running_or_notify_cancel():
                continue

            try:
                result = rqi.cb(**rqi.args)
            except KeyboardInterrupt:
                self.stop()
            except Exception as e:
                rqi.future.set_exception(e)
            else:
                if not isinstance(result, Future):
                    rqi.future.set_result(result)
                    self.queue.task_done()
                else:
                    self._copy_result(result, rqi.future)

        while True:
            try:
                rqi: RequestQueueItem = self.queue.get_nowait()
            except Empty:
                break

            rqi.future.set_exception(RuntimeError("System stoppped."))

        self.responder.stop()

    def stop(self):
        self.stopped.set()

    def deinitialize(self) -> None:
        """
        Called by yuuno before it deconfigures itself.
        """
        self.provider.deinitialize()

    @staticmethod
    def _preload():
        print(os.getpid(), ">", "Preloading.")
        from yuuno import init_standalone
        y = init_standalone()
        y.start()
        y.stop()
        print(os.getpid(), ">", "Preload complete.")

    @staticmethod
    def _check_parent():
        import psutil
        current = psutil.Process()
        current.parent().wait()
        print(os.getpid(), ">", "Parent died. Kill own process...")
        current.kill()

    @classmethod
    def execute(cls, read: Connection, write: Connection, framebuffer: Array):
        cls._preload()
        Thread(target=cls._check_parent,  daemon=True).start()

        from yuuno import Yuuno
        yuuno = Yuuno.instance(parent=None)
        env = cls(parent=yuuno, read=read, write=write)
        env._framebuffer = framebuffer
        yuuno.environment = env

        # Wait for the ProviderMeta to be set.
        print(os.getpid(), ">", "Ready to deploy!")
        env._provider_meta = read.recv()
        yuuno.start()
        print(os.getpid(), ">", "Deployed", env._provider_meta)

        # Run the environment
        env.run()

        # Stop Yuuno.
        yuuno.stop()


class Subprocess(Script):
    process: Process
    self_read: Connection
    self_write: Connection
    child_read: Connection
    child_write: Connection
    requester: Requester
    pool: Pool
    provider_info: ScriptProviderInfo

    running: bool

    def __init__(self, pool: Pool, provider_info: ScriptProviderInfo):
        self.process = None
        self.pool = pool
        self.self_read, self.self_write = Pipe(duplex=False)
        self.child_read, self.child_write = Pipe(duplex=False)
        self.requester = Requester(self.child_read, self.self_write)

        self.provider_info = provider_info

        # Allow an 8K image to be transmitted.
        # This should be enough.
        self._fb = Array(c_ubyte, FRAME_BUFFER_SIZE)
        self._fb_lock = Lock()

        self._create()
        self.running = False

    def _create(self):
        self.process = self.pool.Process(
            target=LocalSubprocessEnvironment.execute,
            args=(
                self.self_read, self.child_write,           # Commands
                self._fb
            )
        )
        self.process.start()

    @property
    def alive(self) -> bool:
        return self.running and self.process is not None and self.process.is_alive()

    def initialize(self):
        if self.alive:
            return
        if self.running:
            raise ValueError("Already disposed!")

        self.self_write.send(self.provider_info)

        # Block until initialization completes.
        self.child_read.recv()
        self.running = True
        self.requester.start()

    def dispose(self) -> None:
        """
        Disposes the script.
        """
        if not self.alive:
            return

        if self.requester.is_alive():
            self.requester.stop()
            self.requester.join()

        self.child_write.close()
        self.child_read.close()
        self.self_write.close()
        self.self_read.close()

        self.process.terminate()

    def __del__(self):
        self.dispose()

    @contextmanager
    def framebuffer(self):
        with self._fb_lock:
            yield memoryview(self._fb).cast("B")

    @future_yield_coro
    def get_results(self) -> Dict[str, 'Clip']:
        """
        Returns a dictionary with clips
        that represent the results of the script.
        """

        indexes = yield self.requester.submit("script/subprocess/results", {})
        return {name: ProxyClip(name, length, self) for name, length in indexes.items()}

    def execute(self, code: Union[str, Path]) -> Future:
        """
        Executes the code inside the environment
        """
        return self.requester.submit("script/subprocess/execute", {
            "type": "path" if isinstance(code, Path) else "string",
            "code": str(code)
        })

