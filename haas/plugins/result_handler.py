from argparse import Action
import sys
import time

from haas.result import TestCompletionStatus, separator2
from .i_result_handler_plugin import IResultHandlerPlugin


class VerbosityAction(Action):

    def __init__(self, callback, *args, **kwargs):
        self.callback = callback
        kwargs['nargs'] = 0
        super(VerbosityAction, self).__init__(*args, **kwargs)

    def __call__(self, parser, namespace, values, option_string):
        setattr(namespace, self.dest, self.const)
        self.callback(namespace)


class _WritelnDecorator(object):
    """Used to decorate file-like objects with a handy 'writeln' method"""
    def __init__(self, stream):
        self.stream = stream

    def __getattr__(self, attr):
        if attr in ('stream', '__getstate__'):
            raise AttributeError(attr)
        return getattr(self.stream, attr)

    def writeln(self, arg=None):
        if arg:
            self.write(arg)
        self.write('\n')  # text-mode streams translate to \r\n if needed


class QuietTestResultHandler(IResultHandlerPlugin):
    separator1 = '=' * 70
    separator2 = separator2

    def __init__(self, test_count):
        self.stream = _WritelnDecorator(sys.stderr)
        self._test_count = test_count
        self.tests_run = 0
        self.descriptions = True
        self.expectedFailures = expectedFailures = []
        self.unexpectedSuccesses = unexpectedSuccesses = []
        self.skipped = skipped = []
        self.failures = failures = []
        self.errors = errors = []
        self._collectors = {
            TestCompletionStatus.failure: failures,
            TestCompletionStatus.error: errors,
            TestCompletionStatus.unexpected_success: unexpectedSuccesses,
            TestCompletionStatus.expected_failure: expectedFailures,
            TestCompletionStatus.skipped: skipped,
        }

    @classmethod
    def from_args(cls, args, arg_prefix, test_count):
        return cls(test_count)

    @classmethod
    def add_parser_arguments(self, parser, option_prefix, dest_prefix):
        verbosity = next(group for group in parser._mutually_exclusive_groups
                         if group.title == 'verbosity')

        def callback(ns):
            setattr(ns, dest_prefix[:-1], 'quiet')

        action = lambda *a, **k: VerbosityAction(callback, *a, **k)
        verbosity.add_argument(
            '-q', '--quiet', action=action, const=0, default=1,
            dest='verbosity', help='Quiet output')

    def get_test_description(self, test):
        doc_first_line = test.shortDescription()
        if self.descriptions and doc_first_line:
            return '\n'.join((str(test), doc_first_line))
        else:
            return str(test)

    def start_test(self, test):
        self.tests_run += 1

    def stop_test(self, test):
        pass

    def start_test_run(self):
        pass

    def stop_test_run(self):
        self.print_errors()

    def print_errors(self):
        self.stream.writeln()
        self.print_error_list('ERROR', self.errors)
        self.print_error_list('FAIL', self.failures)

    def print_error_list(self, error_kind, errors):
        for result in errors:
            self.stream.writeln(self.separator1)
            self.stream.writeln(
                '%s: %s' % (error_kind, self.get_test_description(
                    result.test)))
            self.stream.writeln(self.separator2)
            self.stream.writeln(result.exception)

    def __call__(self, result):
        collector = self._collectors.get(result.status)
        if collector is not None:
            collector.append(result)


class StandardTestResultHandler(QuietTestResultHandler):

    _result_formats = {
        TestCompletionStatus.success: '.',
        TestCompletionStatus.failure: 'F',
        TestCompletionStatus.error: 'E',
        TestCompletionStatus.unexpected_success: 'u',
        TestCompletionStatus.expected_failure: 'x',
        TestCompletionStatus.skipped: 's',
    }

    @classmethod
    def add_parser_arguments(self, parser, option_prefix, dest_prefix):
        pass

    def stop_test_run(self):
        self.stream.write('\n')
        super(StandardTestResultHandler, self).stop_test_run()

    def __call__(self, result):
        super(StandardTestResultHandler, self).__call__(result)
        self.stream.write(self._result_formats[result.status])
        self.stream.flush()


class VerboseTestResultHandler(StandardTestResultHandler):

    _result_formats = {
        TestCompletionStatus.success: 'ok',
        TestCompletionStatus.failure: 'FAIL',
        TestCompletionStatus.error: 'ERROR',
        TestCompletionStatus.unexpected_success: 'unexpected success',
        TestCompletionStatus.expected_failure: 'expected failure',
        TestCompletionStatus.skipped: 'skipped',
    }

    @classmethod
    def add_parser_arguments(self, parser, option_prefix, dest_prefix):
        verbosity = next(group for group in parser._mutually_exclusive_groups
                         if group.title == 'verbosity')

        def callback(ns):
            setattr(ns, dest_prefix[:-1], 'verbose')

        action = lambda *a, **k: VerbosityAction(callback, *a, **k)
        verbosity.add_argument(
            '-v', '--verbose', action=action, const=2, default=1,
            dest='verbosity', help='Quiet output')

    def start_test(self, test):
        super(VerboseTestResultHandler, self).start_test(test)
        padding = len(str(self._test_count))
        prefix = '[{timestamp}] ({run: >{padding}d}/{total:d}) '.format(
            timestamp=time.ctime(),
            run=self.tests_run,
            padding=padding,
            total=self._test_count,
        )
        self.stream.write(prefix)
        description = self.get_test_description(test)
        self.stream.write(description)
        self.stream.write(' ... ')
        self.stream.flush()

    def __call__(self, result):
        super(VerboseTestResultHandler, self).__call__(result)
        self.stream.writeln()
        self.stream.flush()
