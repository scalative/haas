from datetime import datetime, timedelta
import statistics

from mock import patch
from six.moves import StringIO

from haas.result import TestResult, TestCompletionStatus, TestDuration
from haas.testing import unittest
from haas.tests import _test_cases
from haas.tests.fixtures import ExcInfoFixture
from ..result_handler import (
    QuietTestResultHandler,
    TimingResultHandler,
    VerboseTestResultHandler,
    sort_result_handlers,
    _format_stat_table,
)


class TestTimingResultHandler(ExcInfoFixture, unittest.TestCase):

    @patch('sys.stderr', new_callable=StringIO)
    def test_output_start_test_run(self, stderr):
        # Given
        handler = TimingResultHandler(number_to_summarize=5)

        # When
        handler.start_test_run()

        # Then
        output = stderr.getvalue()
        self.assertEqual(output, '')

    @patch('sys.stderr', new_callable=StringIO)
    def test_output_stop_test_run_success(self, stderr):
        # Given
        start_time = datetime(2015, 12, 23, 8, 14, 12)
        duration = timedelta(seconds=10, milliseconds=123)
        end_time = start_time + duration
        expected_duration = TestDuration(start_time, end_time)
        case = _test_cases.TestCase('test_method')
        handler = TimingResultHandler(number_to_summarize=5)
        handler.start_test_run()

        result = TestResult.from_test_case(
            case, TestCompletionStatus.success, expected_duration)
        handler(result)

        # When
        handler.stop_test_run()

        # Then
        output = stderr.getvalue()
        output_start = '\n\nTest timing report\n' + handler.separator2
        self.assertTrue(output.startswith(output_start))
        self.assertRegexpMatches(
            output.replace('\n', ''), r'--+.*?00:10\.123 test_method \(')

    @patch('time.ctime')
    @patch('sys.stderr', new_callable=StringIO)
    def test_output_start_test(self, stderr, mock_ctime):
        # Given
        case = _test_cases.TestCase('test_method')
        handler = TimingResultHandler(number_to_summarize=5)

        # When
        handler.start_test(case)

        # Then
        output = stderr.getvalue()
        self.assertEqual(output, '')

    @patch('sys.stderr', new_callable=StringIO)
    def test_no_output_stop_test(self, stderr):
        # Given
        handler = TimingResultHandler(number_to_summarize=5)
        case = _test_cases.TestCase('test_method')

        # When
        handler.stop_test(case)

        # Then
        output = stderr.getvalue()
        self.assertEqual(output, '')

    @patch('sys.stderr', new_callable=StringIO)
    def test_output_on_error(self, stderr):
        # Given
        start_time = datetime(2015, 12, 23, 8, 14, 12)
        duration = timedelta(seconds=10)
        end_time = start_time + duration
        expected_duration = TestDuration(start_time, end_time)
        case = _test_cases.TestCase('test_method')

        handler = TimingResultHandler(number_to_summarize=5)
        with self.exc_info(RuntimeError) as exc_info:
            result = TestResult.from_test_case(
                case, TestCompletionStatus.error, expected_duration,
                exception=exc_info)

        # When
        handler(result)

        # Then
        output = stderr.getvalue()
        self.assertEqual(output, '')

    @patch('sys.stderr', new_callable=StringIO)
    def test_output_on_failure(self, stderr):
        # Given
        start_time = datetime(2015, 12, 23, 8, 14, 12)
        duration = timedelta(seconds=10)
        end_time = start_time + duration
        expected_duration = TestDuration(start_time, end_time)
        case = _test_cases.TestCase('test_method')

        handler = TimingResultHandler(number_to_summarize=5)
        with self.failure_exc_info() as exc_info:
            result = TestResult.from_test_case(
                case, TestCompletionStatus.failure, expected_duration,
                exception=exc_info)

        # When
        handler(result)

        # Then
        output = stderr.getvalue()
        self.assertEqual(output, '')

    @patch('sys.stderr', new_callable=StringIO)
    def test_output_on_success(self, stderr):
        # Given
        start_time = datetime(2015, 12, 23, 8, 14, 12)
        duration = timedelta(seconds=10)
        end_time = start_time + duration
        expected_duration = TestDuration(start_time, end_time)
        case = _test_cases.TestCase('test_method')

        handler = TimingResultHandler(number_to_summarize=5)
        result = TestResult.from_test_case(
            case, TestCompletionStatus.success, expected_duration)

        # When
        handler(result)

        # Then
        output = stderr.getvalue()
        self.assertEqual(output, '')

    @patch('sys.stderr', new_callable=StringIO)
    def test_output_on_skip(self, stderr):
        # Given
        start_time = datetime(2015, 12, 23, 8, 14, 12)
        duration = timedelta(seconds=10)
        end_time = start_time + duration
        expected_duration = TestDuration(start_time, end_time)
        case = _test_cases.TestCase('test_method')

        handler = TimingResultHandler(number_to_summarize=5)
        result = TestResult.from_test_case(
            case, TestCompletionStatus.skipped, expected_duration,
            message='reason')

        # When
        handler(result)

        # Then
        output = stderr.getvalue()
        self.assertEqual(output, '')

    @patch('sys.stderr', new_callable=StringIO)
    def test_output_on_expected_fail(self, stderr):
        # Given
        start_time = datetime(2015, 12, 23, 8, 14, 12)
        duration = timedelta(seconds=10)
        end_time = start_time + duration
        expected_duration = TestDuration(start_time, end_time)
        case = _test_cases.TestCase('test_method')

        handler = TimingResultHandler(number_to_summarize=5)
        with self.exc_info(RuntimeError) as exc_info:
            result = TestResult.from_test_case(
                case, TestCompletionStatus.expected_failure, expected_duration,
                exception=exc_info)

        # When
        handler(result)

        # Then
        output = stderr.getvalue()
        self.assertEqual(output, '')

    @patch('sys.stderr', new_callable=StringIO)
    def test_output_on_unexpected_success(self, stderr):
        # Given
        start_time = datetime(2015, 12, 23, 8, 14, 12)
        duration = timedelta(seconds=10)
        end_time = start_time + duration
        expected_duration = TestDuration(start_time, end_time)
        case = _test_cases.TestCase('test_method')

        handler = TimingResultHandler(number_to_summarize=5)
        result = TestResult.from_test_case(
            case, TestCompletionStatus.unexpected_success, expected_duration)

        # When
        handler(result)

        # Then
        output = stderr.getvalue()
        self.assertEqual(output, '')

    @patch('sys.stderr', new_callable=StringIO)
    def test_output_with_error_on_stop_test_run(self, stderr):
        # Given
        start_time = datetime(2015, 12, 23, 8, 14, 12)
        duration = timedelta(hours=1543, seconds=12, milliseconds=234)
        end_time = start_time + duration
        expected_duration = TestDuration(start_time, end_time)
        case = _test_cases.TestCase('test_method')

        handler = TimingResultHandler(number_to_summarize=5)
        handler.start_test_run()
        with self.exc_info(RuntimeError) as exc_info:
            result = TestResult.from_test_case(
                case, TestCompletionStatus.error, expected_duration,
                exception=exc_info)

        # When
        handler(result)
        handler.stop_test_run()

        # Then
        output = stderr.getvalue()
        output_start = '\n\nTest timing report\n' + handler.separator2
        self.assertTrue(output.startswith(output_start))
        self.assertRegexpMatches(
            output.replace('\n', ''), r'--+.*?1543:00:12\.234 test_method \(')

    @patch('sys.stderr', new_callable=StringIO)
    def test_output_with_failure_on_stop_test_run(self, stderr):
        # Given
        start_time = datetime(2015, 12, 23, 8, 14, 12)
        duration = timedelta(hours=1, minutes=1, seconds=14, milliseconds=567)
        end_time = start_time + duration
        expected_duration = TestDuration(start_time, end_time)
        case = _test_cases.TestCase('test_method')

        handler = TimingResultHandler(number_to_summarize=5)
        handler.start_test_run()
        with self.failure_exc_info() as exc_info:
            result = TestResult.from_test_case(
                case, TestCompletionStatus.failure, expected_duration,
                exception=exc_info)

        # When
        handler(result)
        handler.stop_test_run()

        # Then
        output = stderr.getvalue()
        output_start = '\n\nTest timing report\n' + handler.separator2
        self.assertTrue(output.startswith(output_start))
        self.assertRegexpMatches(
            output.replace('\n', ''), r'--+.*?1:01:14\.567 test_method \(')

    def _calculate_statistics(self, test_durations):
        durations_secs = [
            i['seconds'] + (0.001 * i['milliseconds'])
            for i in test_durations
        ]
        durations_secs = sorted(durations_secs, reverse=True)
        tests_count = len(durations_secs)

        mean = TestDuration(statistics.mean(durations_secs))
        median = TestDuration(statistics.median(durations_secs))
        stdev = TestDuration(statistics.stdev(durations_secs))

        percentile_99_index = int(tests_count * 0.01)
        percentile_95_index = int(tests_count * 0.05)
        percentile_90_index = int(tests_count * 0.10)
        percentile_80_index = int(tests_count * 0.20)

        pairs = [
            ['Mean', str(mean).strip()],
            ['Std Dev', str(stdev).strip()],
            ['Median', str(median).strip()],
            ['80%', str(TestDuration(
                durations_secs[percentile_80_index])).strip()],
            ['90%', str(TestDuration(
                durations_secs[percentile_90_index])).strip()],
            ['95%', str(TestDuration(
                durations_secs[percentile_95_index])).strip()],
            ['99%', str(TestDuration(
                durations_secs[percentile_99_index])).strip()],
        ]

        return _format_stat_table(pairs)

    @patch('sys.stderr', new_callable=StringIO)
    def test_output_multiple_tests(self, stderr):
        # Given
        tests_start_time = datetime(2015, 12, 23, 8, 14, 12)
        test_durations = [
            dict(seconds=9, milliseconds=123),
            dict(seconds=2, milliseconds=50),
            dict(seconds=1, milliseconds=100),
            dict(seconds=6, milliseconds=0),
            dict(seconds=3, milliseconds=542),
        ]

        expected_stats = self._calculate_statistics(test_durations)

        test_start_time = None
        expected_durations = []
        for kwargs in test_durations:
            duration = timedelta(**kwargs)
            if test_start_time is None:
                test_start_time = tests_start_time
            end_time = test_start_time + duration
            expected_durations.append(TestDuration(test_start_time, end_time))
            test_start_time = end_time

        handler = TimingResultHandler(number_to_summarize=5)
        handler.start_test_run()

        def make_case():
            class Case(_test_cases.TestCase):
                pass
            return Case('test_method')

        for duration in expected_durations:
            result = TestResult.from_test_case(
                make_case(), TestCompletionStatus.success, duration)
            handler(result)

        # When
        handler.stop_test_run()

        # Then
        output = stderr.getvalue()
        output_start = '\n\nTest timing report\n' + handler.separator2
        self.assertTrue(output.startswith(output_start))
        self.assertRegexpMatches(
            output.replace('\n', ''), r'--+.*?00:09\.123 test_method \(')
        self.assertIn(expected_stats, output)


class TestSortResultHandlers(unittest.TestCase):

    def test_sort_result_handlers(self):
        # Given
        handlers = [QuietTestResultHandler(5), TimingResultHandler(5)]
        expected = handlers[::-1]

        # When
        sorted_handlers = sort_result_handlers(handlers)

        # Then
        self.assertEqual(sorted_handlers, expected)

    def test_sort_result_handlers_multiple_core(self):
        # Given
        handlers = [VerboseTestResultHandler(5), QuietTestResultHandler(5),
                    TimingResultHandler(5)]
        expected = handlers[::-1]

        # When
        sorted_handlers = sort_result_handlers(handlers)

        # Then
        self.assertEqual(sorted_handlers, expected)

        # Given
        handlers = [QuietTestResultHandler(5), VerboseTestResultHandler(5),
                    TimingResultHandler(5)]
        expected = [handlers[2], handlers[0], handlers[1]]

        # When
        sorted_handlers = sort_result_handlers(handlers)

        # Then
        self.assertEqual(sorted_handlers, expected)
