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
