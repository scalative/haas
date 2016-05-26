from contextlib import contextmanager
import sys


class ExcInfoFixture(object):

    @contextmanager
    def failure_exc_info(self, msg=None):
        try:
            self.fail(msg)
        except self.failureException:
            yield sys.exc_info()

    @contextmanager
    def exc_info(self, cls):
        try:
            raise cls()
        except cls:
            yield sys.exc_info()


class MockDateTime(object):
    def __init__(self, ret):
        try:
            self.ret = iter(ret)
        except TypeError:
            self.ret = iter((ret,))

    def utcnow(self):
        try:
            return next(self.ret)
        except StopIteration:
            raise ValueError('No more mock values!')
