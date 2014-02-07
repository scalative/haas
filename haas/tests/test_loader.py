# Copyright 2013-2014 Simon Jagoe
import unittest

from ..loader import Loader


class LoaderTestMixin(object):

    def setUp(self):
        class TestTestCase(unittest.TestCase):
            def test_method(self1):
                pass
        self.test_class = TestTestCase
        self.loader = Loader()

    def tearDown(self):
        del self.loader
        del self.test_class


class TestLoadTest(LoaderTestMixin, unittest.TestCase):

    def test_creates_instance_for_valid_test(self):
        test = self.loader.load_test(self.test_class, 'test_method')
        self.assertIsInstance(test, unittest.TestCase)
        self.assertIsInstance(test, self.test_class)


class TestFindTestMethodNames(LoaderTestMixin, unittest.TestCase):

    def test_finds_valid_test_names(self):
        names = self.loader.find_test_method_names(self.test_class)
        self.assertEqual(names, ['test_method'])


class TestLoadCase(LoaderTestMixin, unittest.TestCase):

    def test_creates_unittest_testsuite(self):
        suite = self.loader.load_case(self.test_class)
        self.assertIsInstance(suite, unittest.TestSuite)
