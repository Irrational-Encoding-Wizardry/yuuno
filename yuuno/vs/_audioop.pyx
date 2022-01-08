import typing as t
import audioop
import sys

from cython cimport view, cdivision


cdef bytes __byteswap(bytearray inp):
    if sys.byteorder == "big":
        return audioop.byteswap(inp, 4)
    else:
        return bytes(inp)

cdef float __clamp(float v, float min, float max) nogil:
    if v < min:
        return min
    elif v > max:
        return max
    else:
        return v


@cdivision(True)
def int8_to_float32(unsigned char[::1] inp, int bits_per_sample) -> bytes:
    data = bytearray(len(inp) * 4)
    cdef float[::1] view
    view = data

    cdef float* _view = &view[0]
    cdef unsigned char* _inp = &inp[0]

    cdef int shifted_by = 1 << (bits_per_sample-1)
    cdef float max_pos_value = shifted_by - 1
    cdef unsigned char v = 0

    if max_pos_value == 0:
        raise ValueError("Bits per Sample must be >0")

    for i in range(len(inp)):
        # Cast float as int in typing as the memoryview accepts floats.
        _view[i] = __clamp((_inp[i] - shifted_by) / max_pos_value, -1.0, 1)

    return __byteswap(data)


@cdivision(True)
def int16_to_float32(unsigned short[::1] inp, int bits_per_sample) -> bytes:
    data = bytearray(len(inp) * 4)
    cdef float[::1] view
    view = data

    cdef float* _view = &view[0]
    cdef unsigned short* _inp = &inp[0]

    cdef int shifted_by = 1 << (bits_per_sample-1)
    cdef float max_pos_value = shifted_by - 1
    cdef unsigned char v = 0

    if max_pos_value <= 8:
        raise ValueError("Bits per Sample must be >8")

    for i in range(len(inp)):
        # Cast float as int in typing as the memoryview accepts floats.
        _view[i] = __clamp((_inp[i] - shifted_by) / max_pos_value, -1.0, 1)

    return __byteswap(data)


@cdivision(True)
def int16_to_float32(unsigned int[::1] inp, int bits_per_sample) -> bytes:
    data = bytearray(len(inp) * 4)
    cdef float[::1] view
    view = data

    cdef float* _view = &view[0]
    cdef unsigned int* _inp = &inp[0]

    cdef int shifted_by = 1 << (bits_per_sample-1)
    cdef float max_pos_value = shifted_by - 1
    cdef unsigned char v = 0

    if max_pos_value <= 16:
        raise ValueError("Bits per Sample must be >16")

    for i in range(len(inp)):
        # Cast float as int in typing as the memoryview accepts floats.
        _view[i] = __clamp((_inp[i] - shifted_by) / max_pos_value, -1.0, 1)

    return __byteswap(data)
