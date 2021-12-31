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
import traceback
from multiprocessing.connection import Connection
from threading import Thread, RLock as Lock, Event
from typing import MutableMapping, Mapping, Optional, Any, Callable, Union
from typing import NamedTuple, List
from concurrent.futures import Future


class Response(NamedTuple):
    id: int
    data: Optional[Any] = None
    error: Optional[Exception] = None
    traceback: Optional[List[str]] = None
    protected: bool = False

    def store(self, fut: Future):
        if self.error is not None:
            fut.set_exception(self.error)
        else:
            fut.set_result(self.data)


class Request(NamedTuple):
    id: int
    type: str
    data: Any
    protect: bool = False

    def respond(self, data=None) -> Response:
        return Response(id=self.id, data=data, protected=self.protect)

    def fail(self, error=None) -> Response:
        return Response(
            id=self.id,
            error=error,
            traceback=traceback.format_tb(error.__traceback__),
            protected=self.protect
        )


class Handler(Thread):
    read: Connection
    write: Connection

    write_lock: Lock
    stopped: Event

    def __init__(self, read: Connection, write: Connection):
        super(Handler, self).__init__(daemon=True)
        self.read = read
        self.write = write

        self.stopped = Event()
        self.lock = Lock()

    def _handle(self, obj: Union[Request, Response]):
        pass

    def run(self):
        while not self.stopped.is_set():
            if not self.read.poll(1):
                continue

            data = self.read.recv()
            self._handle(data)

    def send(self, obj):
        with self.lock:
            self.write.send(obj)

    def stop(self):
        self.stopped.set()
        self.join()


class Responder(Handler):
    """
    Runs in the subprocess.

    It responds to the requests of the main-process.
    """

    handlers: Mapping[str, Callable[[Any], Future]]

    def __init__(self, read: Connection, write: Connection, handlers: Mapping[str, Callable[[Any], Future]]):
        super(Responder, self).__init__(read, write)
        self.handlers = handlers

    def _handle(self, obj: Request):
        print(os.getpid(), ">", obj)
        if obj.type not in self.handlers:
            self._send(obj.fail(NotImplementedError("Request not supported")))
            return

        cb = self.handlers[obj.type]
        fut = cb(obj.data)
        fut.add_done_callback(lambda f: self._respond(obj, f))

    def _respond(self, req: Request, res: Future):
        if res.exception():
            resp = req.fail(res.exception())
        else:
            resp = req.respond(res.result())
        self._send(resp)

    def _send(self, resp):
        self.send(resp)
        if resp.protected:
            resp = "(protected)"
        print(os.getpid(), ">", resp)


class Requester(Handler):
    """
    Runs in the main process.

    It waits for responses and sends new requests.
    """
    max_id: int
    max_id_lock: Lock
    waiting: MutableMapping[int, Future]

    def __init__(self, read: Connection, write: Connection):
        super(Requester, self).__init__(read, write)
        self.max_id = 0
        self.max_id_lock = Lock()
        self.waiting = {}

    def _handle(self, obj: Response):
        if obj.id not in self.waiting:
            return
        fut = self.waiting[obj.id]
        if fut.cancelled():
            return

        obj.store(fut)

    def _generate_id(self) -> int:
        with self.max_id_lock:
            new_id = self.max_id
            self.max_id += 1
        return new_id

    def submit(self, type: str, data: Any, protect: bool = False) -> Future:
        req = Request(id=self._generate_id(), type=type, data=data, protect=protect)
        fut = Future()
        fut.set_running_or_notify_cancel()
        self.waiting[req.id] = fut
        self.send(req)
        return fut
