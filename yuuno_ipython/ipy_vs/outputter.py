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
import typing as t
from threading import RLock
from concurrent.futures import Future

import vapoursynth as vs
from yuuno.vs.utils import get_proxy_or_core
from yuuno.vs.flags import Features


T = t.TypeVar("T")


def as_completed(futures: t.Iterable[Future], prefetch: int, backlog: t.Optional[int]=None) -> t.Iterable[T]:
    if backlog is None:
        backlog = prefetch*3
    if backlog < prefetch:
        backlog = prefetch

    enum_fut = enumerate(futures)

    finished = False
    running = 0
    lock = RLock()
    reorder = {}

    def _request_next():
        nonlocal finished, running
        with lock:
            if finished:
                return

            ni = next(enum_fut, None)
            if ni is None:
                finished = True
                return

            running += 1

            idx, fut = ni
            reorder[idx] = fut
            fut.add_done_callback(_finished)

    def _finished(f):
        nonlocal finished, running
        with lock:
            running -= 1
            if finished:
                return

            if f.exception() is not None:
                finished = True
                return
            
            _refill()

    def _refill():
        if finished:
            return

        with lock:
            # Two rules: 1. Don't exceed the concurrency barrier.
            #            2. Don't exceed unused-frames-backlog
            while (not finished) and (running < prefetch) and len(reorder)<backlog:
                _request_next()
    _refill()

    sidx = 0
    fut: Future
    try:
        while (not finished) or (len(reorder)>0) or running>0:
            if sidx not in reorder:
                # Spin. Reorder being empty should never happen.
                continue

            # Get next requested frame
            fut = reorder[sidx]

            result = fut.result()
            del reorder[sidx]
            _refill()

            sidx += 1
            yield result

    finally:
        finished = True


def frames(clip, prefetch, backlog):
    return as_completed((clip.get_frame_async(frameno) for frameno in range(len(clip))), prefetch, backlog)

def encode(
        clip: vs.VideoNode,
        stream: t.IO[t.ByteString],
        *,
        y4m: bool = False,
        prefetch: t.Optional[int]=None,
        backlog: t.Optional[int]=None,
        progress: t.Optional[t.Callable[[int, int], None]]=None
) -> None:
    if prefetch is None:
        prefetch = get_proxy_or_core().num_threads

    if not isinstance(clip, vs.VideoNode):
        clip = clip[0]

    if y4m:
        if clip.format.color_family == vs.GRAY:
            y4mformat = 'mono'
            if clip.format.bits_per_sample > 8:
                y4mformat = y4mformat + str(clip.format.bits_per_sample)
        elif clip.format.color_family == vs.YUV:
            if clip.format.subsampling_w == 1 and clip.format.subsampling_h == 1:
                y4mformat = '420'
            elif clip.format.subsampling_w == 1 and clip.format.subsampling_h == 0:
                y4mformat = '422'
            elif clip.format.subsampling_w == 0 and clip.format.subsampling_h == 0:
                y4mformat = '444'
            elif clip.format.subsampling_w == 2 and clip.format.subsampling_h == 2:
                y4mformat = '410'
            elif clip.format.subsampling_w == 2 and clip.format.subsampling_h == 0:
                y4mformat = '411'
            elif clip.format.subsampling_w == 0 and clip.format.subsampling_h == 1:
                y4mformat = '440'
            else:
                raise ValueError("This is a very strange subsampling config.")

            if clip.format.bits_per_sample > 8:
                y4mformat = y4mformat + 'p' + str(clip.format.bits_per_sample)
        else:
            raise ValueError("Can only use vs.GRAY and vs.YUV for V4M-Streams")

        if len(y4mformat) > 0:
            y4mformat = 'C' + y4mformat

        data = f'YUV4MPEG2 {y4mformat} W{clip.width} H{clip.height} F{clip.fps_num}:{clip.fps_den} Ip A0:0 XLENGTH={len(clip)}\n'
        stream.write(data.encode("ascii"))
        if hasattr(stream, "flush"):
            stream.flush()

    frame: vs.VideoFrame
    for idx, frame in enumerate(frames(clip, prefetch, backlog)):
        if y4m:
            stream.write(b"FRAME\n")

        if Features.API4:
            iterator = frame
        else:
            iterator = frame.planes()

        for planeno, plane in enumerate(iterator):
            # This is a quick fix.
            # Calling bytes(VideoPlane) should make the buffer continuous by
            # copying the frame to a continous buffer
            # if the stride does not match the width*bytes_per_sample.
            try:
                if frame.get_stride(planeno) != frame.width*clip.format.bytes_per_sample:
                    stream.write(bytes(plane))
                else:
                    stream.write(plane)

            except BrokenPipeError:
                return

            if hasattr(stream, "flush"):
                stream.flush()

        if progress is not None:
            progress(idx+1, len(clip))

    stream.close()
