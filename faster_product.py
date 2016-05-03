from itertools import count, chain


class Current(object):
    def __init__(self, iterable):
        self.iterator = iter(iterable)
        self.cur = None

    def __iter__(self):
        return self

    def __next__(self):
        cur = next(self.iterator)
        self.cur = cur
        return self.cur

    def next(self):
        res = self.__next__()
        yield res


def test_current():
    g = Current(iter(count(10)))
    assert g.cur is None
    assert next(g) == 10
    assert g.cur == 10
    assert g.cur == 10
    assert next(g) == 11
    assert g.cur == 11


test_current()


class Reset(object):
    def __init__(self, iterable):
        self._iterator = iter(iterable)
        self._orig_iter = self._iterator
        self._saved = []
        self._already_saved = 0

    def __iter__(self):
        return self

    def __next__(self):
        try:
            cur = next(self._iterator)
            if self._already_saved:
                self._already_saved -= 1
            else:
                self._saved.append(cur)
        except StopIteration:
            raise
        return cur

    def reset(self):
        self._iterator = chain(iter(self._saved), self._orig_iter)
        self._already_saved = len(self._saved)


def test_reset():
    a = iter(range(10))
    b = Reset(range(10))
    for x in range(5):
        assert next(b) == next(a)

    a = iter(range(10))
    b.reset()
    for x in range(2):
        assert next(b) == next(a)

    a = iter(range(10))
    b.reset()
    for x in range(7):
        assert next(b) == next(a)

    a = iter(range(10))
    b.reset()
    for x in a:
        assert next(b) == x

    a = iter(range(10))
    b.reset()
    for x in b:
        assert next(a) == x

    a = iter(range(10))
    b.reset()
    for x in b:
        assert next(a) == x


class Cycle(Reset):
    def __next__(self):
        try:
            cur = next(self._iterator)
            if self._already_saved:
                self._already_saved -= 1
            else:
                self._saved.append(cur)
        except StopIteration:
            self.reset()
            cur = next(self)
        return cur


class fast_product(object):
    def __init__(self, *iterables):
        self.gears = [Reset(x) for x in iterables]
        self.curs = [None for x in self.gears]
        self.reset_gears(len(self.curs))

    def reset_gears(self, i):
        # skip the 0 gear
        for gear in self.gears[:i]:
            gear.reset()
        for x in range(1, i):
            self.curs[x] = next(self.gears[x])

    def valid_state(self):
        return True

    def limit_reached(self):
        return False

    def __iter__(self):
        return self

    def __next__(self):
        i = 0
        while 1:
            self.i = i
            try:
                self.curs[i] = next(self.gears[i])
                if self.limit_reached():
                    raise StopIteration
                if not self.valid_state():
                    continue
                if i == 0:
                    return tuple(self.curs)
                i = 0
            except StopIteration:
                if i + 1 == len(self.gears):
                    raise
                i += 1
                self.reset_gears(i)


class limit_product(fast_product):
    def valid_state(self):
        return self.i + 1 == len(self.curs) or \
               self.curs[self.i] < self.curs[self.i + 1]

    def limit_reached(self):
        return self.i + 1 < len(self.curs) and \
               self.curs[self.i] >= self.curs[self.i + 1]


def test_limit_product():
    plimit = limit_product(range(7), range(7), range(7))
    assert list(plimit) == [(0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3),
                            (0, 1, 4), (0, 2, 4), (1, 2, 4), (0, 3, 4),
                            (1, 3, 4), (2, 3, 4), (0, 1, 5), (0, 2, 5),
                            (1, 2, 5), (0, 3, 5), (1, 3, 5), (2, 3, 5),
                            (0, 4, 5), (1, 4, 5), (2, 4, 5), (3, 4, 5),
                            (0, 1, 6), (0, 2, 6), (1, 2, 6), (0, 3, 6),
                            (1, 3, 6), (2, 3, 6), (0, 4, 6), (1, 4, 6),
                            (2, 4, 6), (3, 4, 6), (0, 5, 6), (1, 5, 6),
                            (2, 5, 6), (3, 5, 6), (4, 5, 6)]


test_limit_product()
