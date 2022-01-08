import sys
import audioop
import typing as t

# try:
#     from yuuno.vs._audioop import *
# 
# 
# except ImportError:
if True:

    def __clamp(v: float, min: float, max: float) -> float:
        if v < min:
            return min
        elif v > max:
            return max
        else:
            return v

    def __int_to_float32(inp: t.Sequence[int], bits_per_sample: int) -> bytes:
        data = bytearray(len(inp) * 4)
        _view = memoryview(data).cast("f")
        shifted_by = 1 << (bits_per_sample-1)
        max_pos_value = shifted_by - 1
        for i, v in enumerate(inp):
            # Cast float as int in typing as the memoryview accepts floats.
            _view[i] = t.cast(int, __clamp((v - shifted_by) / (max_pos_value), -1.0, 1))

        return byteswap(data)

    def int8_to_float32(inp: bytes, bits_per_sample: int) -> bytes:
        return __int_to_float32(inp, factor=4, bits_per_sample=bits_per_sample)

    def int16_to_float32(inp: bytes, bits_per_sample: int) -> bytes:
        return __int_to_float32(memoryview(inp).cast("H"), bits_per_sample=bits_per_sample)

    def int32_to_float32(inp: bytes, bits_per_sample: int) -> bytes:
        return __int_to_float32(memoryview(inp).cast("I"), bits_per_sample=bits_per_sample)


def to_float32_le(inp: bytes, bits_per_sample: int) -> bytes:
    if bits_per_sample == 0:
        raise ValueError("bits per sample may not be 0")
    elif bits_per_sample <= 8:
        return int8_to_float32(inp, bits_per_sample)
    elif bits_per_sample <= 16:
        return int16_to_float32(inp, bits_per_sample)
    elif bits_per_sample <= 32:
        return int32_to_float32(inp, bits_per_sample)
    else:
        raise ValueError("bits per sample may not exceed 32")


def byteswap(inp: bytearray) -> bytes:
    if sys.byteorder == "big":
        return audioop.byteswap(inp, 4)
    else:
        return bytes(inp)
