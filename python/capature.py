import random
from hashlib import md5


def sign(_0x353d93: int):
    def generate_random_chars():
        _0xa5adc8 = []
        _0x5cdcca = '0123456789abcdef'
        _0xccd6e7 = 0x0
        while _0xccd6e7 < 0x24:
            _0xa5adc8.append(_0x5cdcca[random.randint(0, 0xf)])
            _0xccd6e7 += 1
        _0xa5adc8[0xe] = '4'
        _0xa5adc8[0x13] = _0x5cdcca[int(_0xa5adc8[0x13], 16) & 0x3 | 0x8]
        _0xa5adc8[0x8] = _0xa5adc8[0xd] = _0xa5adc8[0x12] = _0xa5adc8[0x17] = '-'
        return ''.join(_0xa5adc8)

    _0x4471c4 = md5((str(_0x353d93) + generate_random_chars()).encode("utf-8")).hexdigest()
    _0x353d93 = md5(
        (str(_0x353d93) + "42sxgHoTPTKbt0uZxPJ7ssOvtXr3ZgZ1" + "slide" + _0x4471c4).encode("utf-8")
    ).hexdigest() + ":" + str(int(_0x353d93) + 0x493e0)
    return [_0x4471c4, _0x353d93]
