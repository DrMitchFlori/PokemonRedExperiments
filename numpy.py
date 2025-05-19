import math

class _FakeArray(list):
    def __mul__(self, other):
        return _FakeArray([x * other for x in self])
    def __rmul__(self, other):
        return _FakeArray([other * x for x in self])
    def __pow__(self, other):
        return _FakeArray([x ** other for x in self])
    def __rpow__(self, other):
        return _FakeArray([other ** x for x in self])


def arange(stop, start=0, step=1):
    if start != 0 or step != 1:
        return _FakeArray(list(range(start, stop, step)))
    return _FakeArray(list(range(stop)))


def sin(x):
    if isinstance(x, (list, _FakeArray)):
        return _FakeArray([math.sin(v) for v in x])
    return math.sin(x)


def zeros(n, dtype=None):
    return _FakeArray([0 for _ in range(n)])


def allclose(a, b, atol=1e-08):
    if len(a) != len(b):
        return False
    return all(abs(x - y) <= atol for x, y in zip(a, b))

pi = math.pi
