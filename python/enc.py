from hashlib import md5

def _0x4aac3d(_0xfd3213):
    _0x4e1fea = sorted(_0xfd3213.keys())
    _0x30ab3a = {}
    for _0x529462 in range(len(_0x4e1fea)):
        _0x30ab3a[_0x4e1fea[_0x529462]] = _0xfd3213[_0x4e1fea[_0x529462]]
    return _0x30ab3a

def enc(_0x1a35a1):
    _0x5f1401 = {
        'vVhWL': lambda _0x384730, _0x16064b: _0x384730 != _0x16064b,
        'QDtun': "GkU",
        'ZyxHo': "jlT",
        'NnIBP': lambda _0x96bdaa, _0x220d20: _0x96bdaa(_0x220d20),
        'OLlgO': lambda _0x597f06, _0x95c23: _0x597f06 + _0x95c23,
        'ndHxm': lambda _0x404294, _0x2adbc2: _0x404294 + _0x2adbc2,
        'RGnnK': lambda _0x461ef0, _0x3da61a: _0x461ef0 + _0x3da61a
    }
    if _0x5f1401["vVhWL"](_0x5f1401["QDtun"], _0x5f1401["ZyxHo"]):
        _0x16263b = "%sd`~7^/>N4!Q#){''"
        _0x4299a1 = _0x4aac3d(_0x1a35a1)
        _0x443159 = []
        for _0xdf82cf, _0x5e3e3f in _0x4299a1.items():
            _0x443159.append(
                _0x5f1401["OLlgO"](_0x5f1401["ndHxm"](_0x5f1401['RGnnK']('[', _0xdf82cf), '='), _0x5e3e3f) + ']')
        _0x443159.append(_0x5f1401["RGnnK"](_0x5f1401["RGnnK"]('[', _0x16263b), ']'))
        _0x2f67c8 = ''.join(_0x443159)
        return md5(_0x2f67c8.encode("utf-8")).hexdigest()