from argparse import ArgumentParser
from datetime import datetime, timedelta
import time

from mock import Mock, patch
from six.moves import StringIO

from ..plugins.discoverer import _create_import_error_test
from ..plugins.parallel_runner import ChildResultHandler, ParallelTestRunner
from ..result import (
    ResultCollector, TestCompletionStatus, TestResult, TestDuration)
from ..suite import TestSuite
from ..testing import unittest
from . import _test_cases
from .fixtures import MockDateTime


class AsyncResult(object):

    def ready(self):
        return True

    def wait(self, timeout):
        pass


def apply_async(func, args=None, kwargs=None, callback=None):
    if args is None:
        args = ()
    if kwargs is None:
        kwargs = {}
    result = func(*args, **kwargs)
    if callback is not None:
        callback(result)
    return AsyncResult()


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

    @patch('haas.plugins.parallel_runner.Pool')
    def test_parallel_test_runner_mock_subprocess(self, pool_class):
        # Given
        pool = Mock()
        pool_class.return_value = pool
        pool.apply_async.side_effect = apply_async

        test_case = _test_cases.TestCase('test_method')
        test_suite = TestSuite([test_case])

        start_time = datetime(2015, 12, 23, 8, 14, 12)
        duration = timedelta(seconds=10)
        end_time = start_time + duration

        duration = TestDuration(start_time, end_time)
        expected_result = TestResult.from_test_case(
            test_case, TestCompletionStatus.success, duration)

        processes = 5

        result_handler = ChildResultHandler()
        result_collector = ResultCollector()
        result_collector.add_result_handler(result_handler)
        runner = ParallelTestRunner(processes)

        # When
        with patch('haas.result.datetime', new=MockDateTime(
                [start_time, end_time])):
            runner.run(result_collector, test_suite)

        # Then
        self.assertEqual(result_handler.results, [expected_result])
        pool_class.assert_called_once_with(
            processes=processes, initializer=None,
            maxtasksperchild=None)
        pool.close.assert_called_once_with()
        pool.join.assert_called_once_with()

    @patch('haas.plugins.parallel_runner.Pool')
    def test_parallel_runner_single_start_stop_test_run(self, pool_class):
        # Given
        pool = Mock()
        pool_class.return_value = pool
        pool.apply_async.side_effect = apply_async

        test_case = _test_cases.TestCase('test_method')
        test_suite = TestSuite([test_case])

        result_collector = Mock()
        runner = ParallelTestRunner()

        # When
        runner.run(result_collector, test_suite)

        # Then
        pool_class.assert_called_once_with(
            processes=None, initializer=None,
            maxtasksperchild=None)
        pool.close.assert_called_once_with()
        pool.join.assert_called_once_with()
        result_collector.startTestRun.assert_called_once_with()
        result_collector.stopTestRun.assert_called_once_with()

    @patch('haas.plugins.parallel_runner.Pool')
    def test_parallel_runner_initializer(self, pool_class):
        # Given
        initializer = Mock()
        pool = Mock()
        pool_class.return_value = pool
        pool.apply_async.side_effect = apply_async

        test_case = _test_cases.TestCase('test_method')
        test_suite = TestSuite([test_case])

        start_time = datetime(2015, 12, 23, 8, 14, 12)
        duration = timedelta(seconds=10)
        end_time = start_time + duration

        duration = TestDuration(start_time, end_time)
        expected_result = TestResult.from_test_case(
            test_case, TestCompletionStatus.success, duration)

        processes = 5

        result_handler = ChildResultHandler()
        result_collector = ResultCollector()
        result_collector.add_result_handler(result_handler)
        runner = ParallelTestRunner(processes, initializer=initializer)

        # When
        with patch('haas.result.datetime', new=MockDateTime(
                [start_time, end_time])):
            runner.run(result_collector, test_suite)

        # Then
        self.assertEqual(result_handler.results, [expected_result])
        pool_class.assert_called_once_with(
            processes=processes, initializer=initializer,
            maxtasksperchild=None)
        pool.close.assert_called_once_with()
        pool.join.assert_called_once_with()

    @patch('haas.plugins.parallel_runner.Pool')
    def test_parallel_runner_constructor_processes(self, pool_class):
        # Given
        pool = Mock()
        pool_class.return_value = pool
        pool.apply_async.side_effect = apply_async

        test_case = _test_cases.TestCase('test_method')
        test_suite = TestSuite([test_case])

        start_time = datetime(2015, 12, 23, 8, 14, 12)
        duration = timedelta(seconds=10)
        end_time = start_time + duration

        duration = TestDuration(start_time, end_time)
        expected_result = TestResult.from_test_case(
            test_case, TestCompletionStatus.success, duration)

        opt_prefix = '--parallel-'
        dest_prefix = 'parallel_'
        parser = ArgumentParser()
        ParallelTestRunner.add_parser_arguments(
            parser, opt_prefix, dest_prefix)
        args = parser.parse_args(['--processes', '4',
                                  '--process-max-tasks', '1'])

        result_handler = ChildResultHandler()
        result_collector = ResultCollector()
        result_collector.add_result_handler(result_handler)
        runner = ParallelTestRunner.from_args(args, dest_prefix)

        # When
        with patch('haas.result.datetime', new=MockDateTime(
                [start_time, end_time])):
            runner.run(result_collector, test_suite)

        # Then
        self.assertEqual(result_handler.results, [expected_result])
        pool_class.assert_called_once_with(
            processes=4, initializer=None, maxtasksperchild=1)
        pool.close.assert_called_once_with()
        pool.join.assert_called_once_with()

    @patch('haas.plugins.parallel_runner.Pool')
    def test_parallel_runner_constructor_initializer(self, pool_class):
        # Given
        pool = Mock()
        pool_class.return_value = pool
        pool.apply_async.side_effect = apply_async

        test_case = _test_cases.TestCase('test_method')
        test_suite = TestSuite([test_case])

        start_time = datetime(2015, 12, 23, 8, 14, 12)
        duration = timedelta(seconds=10)
        end_time = start_time + duration

        duration = TestDuration(start_time, end_time)
        expected_result = TestResult.from_test_case(
            test_case, TestCompletionStatus.success, duration)

        opt_prefix = '--parallel-'
        dest_prefix = 'parallel_'
        parser = ArgumentParser()
        ParallelTestRunner.add_parser_arguments(
            parser, opt_prefix, dest_prefix)
        args = parser.parse_args(
            ['--process-init',
             'haas.tests._test_cases.subprocess_initializer'])

        result_handler = ChildResultHandler()
        result_collector = ResultCollector()
        result_collector.add_result_handler(result_handler)
        runner = ParallelTestRunner.from_args(args, dest_prefix)

        # When
        with patch('haas.result.datetime', new=MockDateTime(
                [start_time, end_time])):
            runner.run(result_collector, test_suite)

        # Then
        from haas.tests._test_cases import subprocess_initializer

        self.assertEqual(result_handler.results, [expected_result])
        pool_class.assert_called_once_with(
            processes=None, initializer=subprocess_initializer,
            maxtasksperchild=None)
        pool.close.assert_called_once_with()
        pool.join.assert_called_once_with()


class TestParallelRunnerImportError(unittest.TestCase):

    @patch('haas.plugins.parallel_runner.Pool')
    def test_parallel_distribute_module_import_error(self, pool_class):
        # Given
        pool = Mock()
        pool_class.return_value = pool

        try:
            import haas.i_dont_exist  # noqa
        except ImportError:
            test_case = _create_import_error_test('haas.i_dont_exist')
        else:
            self.fail('Module haas.i_dont_exist not expected to exist')
        test_suite = TestSuite((test_case,))

        opt_prefix = '--parallel-'
        dest_prefix = 'parallel_'
        parser = ArgumentParser()
        ParallelTestRunner.add_parser_arguments(
            parser, opt_prefix, dest_prefix)
        args = parser.parse_args([])

        result_handler = ChildResultHandler()
        result_collector = ResultCollector()
        result_collector.add_result_handler(result_handler)
        runner = ParallelTestRunner.from_args(args, dest_prefix)

        # When
        runner.run(result_collector, test_suite)

        self.assertEqual(result_collector.testsRun, 1)
        self.assertFalse(result_collector.wasSuccessful())
        self.assertFalse(pool.apply_async.called)
