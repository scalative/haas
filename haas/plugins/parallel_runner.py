from multiprocessing import Pool
import time

from haas.discoverer import find_test_cases
from haas.result import ResultCollecter
from .i_result_handler_plugin import IResultHandlerPlugin
from .runner import BaseTestRunner


class ChildResultHandler(IResultHandlerPlugin):

    def __init__(self):
        self.start_time = None
        self.stop_time = None
        self.results = []

    # To keep the interface happy
    @classmethod
    def from_args(cls, args, arg_prefix, test_count):  # pragma: no cover
        pass

    # To keep the interface happy
    @classmethod
    def add_parser_arguments(self, parser, option_prefix, dest_prefix):  # pragma: no cover  # noqa
        pass

    def start_test(self, test):
        pass

    def stop_test(self, test):
        pass

    def start_test_run(self):
        self.start_time = time.time()

    def stop_test_run(self):
        self.stop_time = time.time()

    def __call__(self, result):
        self.results.append(result)


def _run_test_in_process(test_case):
    result_handler = ChildResultHandler()
    result_collector = ResultCollecter(buffer=True)
    result_collector.add_result_handler(result_handler)
    runner = BaseTestRunner()
    runner.run(result_collector, test_case)
    return result_handler.results


class ParallelTestRunner(BaseTestRunner):
    """Test runner that executes all tests via a ``multiprocessing.Pool``.

    .. warning::

        This makes the assumption that all test cases are completely
        independant and can be distributed arbitrarily to subprocesses.

    """

    def __init__(self, process_count=None, warnings=None):
        super(ParallelTestRunner, self).__init__(warnings=warnings)
        self.process_count = process_count

    @classmethod
    def from_args(cls, args, arg_prefix):
        return cls(process_count=args.processes)

    @classmethod
    def add_parser_arguments(self, parser, option_prefix, dest_prefix):
        help_ = ('Number of processes to use if running tests in paralled.  '
                 'Defaults to number of processor cores.')
        parser.add_argument('--processes', help=help_, type=int, default=None)

    def _handle_result(self, result, collected_result):
        for test_result in collected_result:
            test = test_result.test
            result.startTest(test)
            result.add_result(test_result)
            result.stopTest(test)

    def _run_tests(self, result, test):
        pool = Pool(processes=self.process_count)

        try:
            callback = lambda collected_result: self._handle_result(
                result, collected_result)
            for test_case in find_test_cases(test):
                pool.apply_async(
                    _run_test_in_process, args=(test_case,), callback=callback)
        finally:
            pool.close()
            pool.join()

    def run(self, result_collector, test_to_run):
        test = lambda result: self._run_tests(result_collector, test_to_run)
        result_collector.startTestRun()
        try:
            return super(ParallelTestRunner, self).run(
                result_collector, test)
        finally:
            result_collector.stopTestRun()
