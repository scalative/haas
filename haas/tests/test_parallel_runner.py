import time

from mock import patch
from six.moves import StringIO

from ..plugins.parallel_runner import ChildResultHandler
from ..testing import unittest


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
