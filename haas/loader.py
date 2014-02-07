# Copyright 2013-2014 Simon Jagoe
import inspect


class Loader(object):

    def __init__(self, test_suite_class=None, test_method_prefix='test'):
        super(Loader, self).__init__()
        self.test_method_prefix = test_method_prefix
        if test_suite_class is None:
            from unittest import TestSuite
            test_suite_class = TestSuite
        self.test_suite_class = test_suite_class

    def find_test_method_names(self, testcase):
        names = [name for name in dir(testcase)
                 if name.startswith(self.test_method_prefix)
                 and inspect.ismethod(getattr(testcase, name))]
        return names

    def load_test(self, testcase, method_name):
        """Create and return an instance of :class:`unittest.TestCase` for the
        specified unbound test method.

        Parameters
        ----------
        unbound_test : unbound method
            An unbound method of a :class:`unittest.TestCase`

        """
        return testcase(methodName=method_name)

    def load_case(self, testcase):
        """Load a TestSuite containing all TestCase instances for all tests in
        a TestCase subclass.

        Parameters
        ----------
        testcase : type
            A subclass of :class:`unittest.TestCase`

        """
        tests = [self.load_test(testcase, name)
                 for name in self.find_test_method_names(testcase)]
        return self.test_suite_class(tests)
