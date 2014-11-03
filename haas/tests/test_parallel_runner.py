import time

from mock import patch
from six.moves import StringIO

from ..plugins.parallel_runner import ChildResultHandler, ParallelTestRunner
from ..result import ResultCollecter, TestCompletionStatus, TestResult
from ..suite import TestSuite
from ..testing import unittest
from . import _test_cases


class TestChildResultHandler(unittest.TestCase):

    @patch('sys.stderr', new_callable=StringIO)
    @patch('sys.stdout', new_callable=StringIO)
    def test_basic_workflow(self, stdout, stderr):
        # Given
        handler = ChildResultHandler()
        test_result = object()

        # Then
        self.assertIsNone(handler.start_time)
        self.assertIsNone(handler.stop_time)
        self.assertEqual(handler.results, [])

        # When
        start_time = time.time()
        handler.start_test_run()

        # Then
        self.assertGreaterEqual(handler.start_time, start_time)
        self.assertIsNone(handler.stop_time)
        self.assertEqual(handler.results, [])

        # When
        handler.start_test(self)
        handler(test_result)
        handler.stop_test(self)

        # Then
        self.assertGreaterEqual(handler.start_time, start_time)
        self.assertIsNone(handler.stop_time)
        self.assertEqual(handler.results, [test_result])

        # When
        stop_time = time.time()
        handler.stop_test_run()

        # Then
        self.assertGreaterEqual(handler.start_time, start_time)
        self.assertLess(handler.start_time, stop_time)
        self.assertGreaterEqual(handler.stop_time, stop_time)
        self.assertEqual(handler.results, [test_result])

        # Finally, no output is produced
        self.assertEqual(stdout.getvalue(), '')
        self.assertEqual(stderr.getvalue(), '')


class TestParallelTestRunner(unittest.TestCase):

    def test_parallel_test_runner_with_subprocess(self):
        """Run a simple test case in a subprocess and receive the result.

        """
        # Given
        test_case = _test_cases.TestCase('test_method')
        test_suite = TestSuite([test_case])

        expected_result = TestResult.from_test_case(
            test_case, TestCompletionStatus.success)

        result_handler = ChildResultHandler()
        result_collector = ResultCollecter()
        result_collector.add_result_handler(result_handler)
        runner = ParallelTestRunner(1)

        # When
        runner.run(result_collector, test_suite)

        # Then
        self.assertEqual(result_handler.results, [expected_result])
