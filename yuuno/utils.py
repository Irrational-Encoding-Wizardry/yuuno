# -*- coding: utf-8 -*-

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
import functools
from threading import Lock
from types import TracebackType
from typing import Optional, Type, NamedTuple, List, Any, TYPE_CHECKING
from typing import Callable, TypeVar, Generator, Tuple, Generic, Sequence
from concurrent.futures import Future as ConcFuture


T = TypeVar("T")
R = TypeVar("R")


class WaitResult(NamedTuple):
    completed: List[Any]
    failed: List[Any]


class AccumulatedException(Exception):

    def __init__(self, msg, exceptions):
        self.exceptions = exceptions
        super(AccumulatedException, self).__init__(msg)


class Future(Generic[T]):
    def result(self) -> T: pass
    def exception(self) -> Optional[BaseException]: pass
    def set_result(self, result: T): pass
    def set_exception(self, etype: Type[BaseException], eval: BaseException, tb: TracebackType): pass
    def add_done_callback(self, cb: 'Future[T]') -> None: pass


if hasattr(Future, "register"):
    if TYPE_CHECKING:
        from asyncio import Future as AIOFut
        Future.register(AIOFut)
    Future.register(ConcFuture)


def inline_resolved(func: Callable[..., T]) -> Callable[..., Future[T]]:
    @functools.wraps(func)
    def _wrapped(*args, **kwargs) -> Future:
        fut = ConcFuture()
        fut.set_running_or_notify_cancel()
        try:
            result_value = func(*args, **kwargs)
        except Exception as e:
            fut.set_exception(e)
        else:
            fut.set_result(result_value)
        return fut
    return _wrapped


def auto_join(func: Callable[..., Future[T]]) -> Callable[..., T]:
    @functools.wraps(func)
    def _wrapped(*args, **kwargs) -> T:
        fut = func(*args, **kwargs)
        return fut.result()
    return _wrapped


def future_yield_coro(func: Callable[..., Generator[Future[T], T, R]]) -> Callable[..., Future[R]]:
    @functools.wraps(func)
    def _wrapper(*args, **kwargs) -> Future:
        def _run(advance: Callable[..., Future[T]], args: Tuple) -> None:
            try:
                next_fut: ConcFuture = advance(*args)
            except StopIteration as e:
                error = None
                result = e.value
            except Exception as e:
                error = e
                result = None
            else:
                next_fut.add_done_callback(_advance)
                return

            if error:
                fut.set_exception(error)
            else:
                fut.set_result(result)

        def _advance(current: Future[T]) -> None:
            if current.exception():
                exc: BaseException = current.exception()
                args = (type(exc), exc, exc.__traceback__)
                advance = gen.throw
            else:
                args = (current.result(),)
                advance = gen.send

            _run(advance, args)

        # Create the future.
        fut: ConcFuture = ConcFuture()
        fut.set_running_or_notify_cancel()

        # Load the generator
        gen: Generator[Future[T], T, R] = func(*args, **kwargs)

        # Run the first iteration.
        _run(gen.send, (None,))

        return fut
    return _wrapper


@future_yield_coro
def gather(futures: [Sequence[Future[T]]]) -> Sequence[T]:
    def wait(wait_for: [Sequence[Future]]) -> Future:
        def remove(future):
            nonlocal running
            with running_lock:
                running -= 1
                if running > 0:
                    return

            failed = [f for f in wait_for if f.exception() is not None]
            completed = [f for f in wait_for if f.exception() is None]
            res.set_result(WaitResult(completed, failed))

        res = ConcFuture()
        res.set_running_or_notify_cancel()
        running = len(futures)
        running_lock: Lock = Lock()

        for fut in wait_for:
            fut.add_done_callback(remove)

        return res

    res: WaitResult = (yield wait(futures))
    if res.failed:
        if len(res.failed) == 1:
            raise res.failed[0].exception()

        raise AccumulatedException("Multiple errors occured.", res.failed)

    return [f.result() for f in res.completed]
