from multiprocessing import Pool
import time

from haas.module_import_error import ModuleImportError
from haas.suite import find_test_cases
from haas.result import ResultCollector
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
    def add_parser_arguments(self, parser, name, option_prefix, dest_prefix):  # pragma: no cover  # noqa
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
    result_collector = ResultCollector(buffer=True)
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

    def __init__(self, process_count=None, initializer=None,
                 maxtasksperchild=None, warnings=None):
        super(ParallelTestRunner, self).__init__(warnings=warnings)
        self.process_count = process_count
        self.initializer = initializer
        self.maxtasksperchild = maxtasksperchild

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
        return cls(process_count=args.processes, initializer=initializer,
                   maxtasksperchild=args.process_max_tasks)

    @classmethod
    def add_parser_arguments(self, parser, option_prefix, dest_prefix):
        process_count_help = (
            'Number of processes to use if running tests in paralled.  '
            'Defaults to number of processor cores.')
        process_init_help = (
            'The dotted module path to a subprocess initialization function. '
            'This function will be passed to the subprocess and called with '
            'zero arguments.')
        process_maxtasksperchild_help = (
            'The number of tasks each process is allowed to run before it is '
            'replaced by a new process.  Defaults to no limit.'
        )
        parser.add_argument(
            '--processes', help=process_count_help, type=int, default=None)
        parser.add_argument(
            '--process-init', help=process_init_help, default=None)
        parser.add_argument(
            '--process-max-tasks', help=process_maxtasksperchild_help,
            type=int, default=None,
        )

    def _handle_result(self, result, collected_result):
        for test_result in collected_result:
            test = test_result.test
            result.startTest(test, test_result.duration.start_time)
            result.add_result(test_result)
            result.stopTest(test)

    def _run_tests(self, result, test):
        pool = Pool(processes=self.process_count,
                    initializer=self.initializer,
                    maxtasksperchild=self.maxtasksperchild)

        try:
            def callback(collected_result):
                self._handle_result(result, collected_result)
            error_tests = []
            call_results = []
            for test_case in find_test_cases(test):
                if isinstance(test_case, ModuleImportError):
                    error_tests.append(test_case)
                else:
                    call_result = pool.apply_async(
                        _run_test_in_process, args=(test_case,),
                        callback=callback)
                    call_results.append(call_result)

            for test_case in error_tests:
                collected_result = _run_test_in_process(test_case)
                callback(collected_result)
        finally:
            pool.close()
            # In some cases (when processes > CPU_CORE_COUNT), the
            # combination of pool.close() and pool.join() does not
            # make the Pool terminate, one or more processes remains
            # alive and the program hangs.
            # To work around this, We wait for all jobs submitted to
            # the pool to complete, and then explicitly call
            # pool.terminate() before pool.join().
            while len(call_results) > 0:
                call_results[0].wait(0.25)
                call_results = [call_result for call_result in call_results
                                if not call_result.ready()]
            pool.terminate()
            pool.join()

    def run(self, result_collector, test_to_run):
        """Run the tests in subprocesses.

        """
        def test(result):
            self._run_tests(result_collector, test_to_run)
        return super(ParallelTestRunner, self).run(result_collector, test)
