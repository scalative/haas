from multiprocessing import Pool
import time

from haas.suite import find_test_cases
from haas.result import ResultCollecter
from haas.utils import get_module_by_name
from .i_result_handler_plugin import IResultHandlerPlugin
from .runner import BaseTestRunner


class ChildResultHandler(IResultHandlerPlugin):
    """A result handler that simply collects :class`TestResults
    <haas.result.TestResult>` for returning to the parent process.

    """

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

    def __init__(self, process_count=None, initializer=None, warnings=None):
        super(ParallelTestRunner, self).__init__(warnings=warnings)
        self.process_count = process_count
        self.initializer = initializer

    @classmethod
    def from_args(cls, args, arg_prefix):
        """Create a :class:`~.ParallelTestRunner` from command-line arguments.

        """
        initializer_spec = args.process_init
        if initializer_spec is None:
            initializer = None
        else:
            module_name, initializer_name = initializer_spec.rsplit('.', 1)
            init_module = get_module_by_name(module_name)
            initializer = getattr(init_module, initializer_name)
        return cls(process_count=args.processes, initializer=initializer)

    @classmethod
    def add_parser_arguments(self, parser, option_prefix, dest_prefix):
        process_count_help = (
            'Number of processes to use if running tests in paralled.  '
            'Defaults to number of processor cores.')
        process_init_help = (
            'The dotted module path to a subprocess initialization function. '
            'This function will be passed to the subprocess and called with '
            'zero arguments.')
        parser.add_argument(
            '--processes', help=process_count_help, type=int, default=None)
        parser.add_argument(
            '--process-init', help=process_init_help, default=None)

    def _handle_result(self, result, collected_result):
        for test_result in collected_result:
            test = test_result.test
            result.startTest(test)
            result.add_result(test_result)
            result.stopTest(test)

    def _run_tests(self, result, test):
        pool = Pool(processes=self.process_count,
                    initializer=self.initializer)

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
        """Run the tests in subprocesses.

        """
        test = lambda result: self._run_tests(result_collector, test_to_run)
        return super(ParallelTestRunner, self).run(result_collector, test)
