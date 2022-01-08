import typing as t
from yuuno.utils import Future


class Format(t.NamedTuple):
    channel_count: int
    samples_per_second: int
    frames: int
    sample_count: int


class Audio(object):

    def __init__(self, clip: t.Any):
        self.clip = clip

    def format(self) -> Format:
        raise NotImplementedError

    def __getitem__(self, frame: int) -> Future:
        raise NotImplementedError

    def __len__(self) -> int:
        raise NotImplementedError

