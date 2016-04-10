import itertools
import traceback


class MockDateTime(object):
    def __init__(self, ret):
        try:
            self.ret = iter(ret)
        except TypeError:
            self.ret = iter(itertools.repeat(ret))

    def utcnow(self):
        return next(self.ret)
