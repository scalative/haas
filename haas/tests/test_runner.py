from mock import Mock, patch

from ..plugins.runner import BaseTestRunner
from ..testing import unittest


class TestBaseTestRunner(unittest.TestCase):

    @patch('warnings.filterwarnings')
    @patch('warnings.simplefilter')
    @patch('warnings.catch_warnings')
    def test_run_tests_no_warning_capture(self, catch_warnings, simplefilter,
                                          filterwarnings):
        # Given

        def test(result):
            self.test_result = result
        self.test_result = None
        result_collector = Mock()
        test_runner = BaseTestRunner()

        # When
        test_runner.run(result_collector, test)

        # Then
        self.assertIs(self.test_result, result_collector)
        result_collector.startTestRun.assert_called_once_with()
        result_collector.stopTestRun.assert_called_once_with()

        catch_warnings.assert_called_once_with()
        self.assertFalse(simplefilter.called)
        self.assertFalse(filterwarnings.called)

    @patch('warnings.filterwarnings')
    @patch('warnings.simplefilter')
    @patch('warnings.catch_warnings')
    def test_run_tests_ignore_warnings(self, catch_warnings, simplefilter,
                                       filterwarnings):
        # Given

        def test(result):
            self.test_result = result
        self.test_result = None
        result_collector = Mock()
        test_runner = BaseTestRunner(warnings='ignore')

        # When
        test_runner.run(result_collector, test)

        # Then
        self.assertIs(self.test_result, result_collector)
        result_collector.startTestRun.assert_called_once_with()
        result_collector.stopTestRun.assert_called_once_with()

        catch_warnings.assert_called_once_with()
        simplefilter.assert_called_once_with('ignore')
        self.assertFalse(filterwarnings.called)

    @patch('warnings.filterwarnings')
    @patch('warnings.simplefilter')
    @patch('warnings.catch_warnings')
    def test_run_tests_always_warn(self, catch_warnings, simplefilter,
                                   filterwarnings):
        # Given

        def test(result):
            self.test_result = result
        self.test_result = None
        result_collector = Mock()
        test_runner = BaseTestRunner(warnings='always')

        # When
        test_runner.run(result_collector, test)

        # Then
        self.assertIs(self.test_result, result_collector)
        result_collector.startTestRun.assert_called_once_with()
        result_collector.stopTestRun.assert_called_once_with()

        catch_warnings.assert_called_once_with()
        simplefilter.assert_called_once_with('always')
        filterwarnings.assert_called_once_with(
            'module', category=DeprecationWarning,
            message='Please use assert\w+ instead.')
