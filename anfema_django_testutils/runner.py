"""This module provides a TestRunner."""
from __future__ import annotations


__all__ = ('TestRunner',)

import argparse
import contextlib
import datetime
import itertools
import os
import pathlib
import re
import sys
import textwrap
import unittest.runner
from collections import defaultdict, namedtuple
from contextlib import nullcontext
from operator import attrgetter
from typing import TYPE_CHECKING
from unittest.result import TestResult
from unittest.runner import TextTestRunner
from unittest.suite import _ErrorHolder
from unittest.util import strclass

from django.contrib.staticfiles import finders
from django.core.management import color
from django.core.management.base import OutputWrapper
from django.template.loader import render_to_string
from django.test.runner import DiscoverRunner
from django.utils import termcolors, timezone

from coverage import Coverage
from snapshottest.django import TestRunnerMixin as SnapshotTestRunnerMixin

from .settings import get_config


# isort: off
if TYPE_CHECKING:
    import types
    import unittest
    from typing import Any, Dict, Tuple, Type, Union

    _SubTest = unittest.case._SubTest
    _SysExcInfoType = Union[
        Tuple[Type[BaseException], BaseException, types.TracebackType],
        Tuple[None, None, None],
    ]
# isort: on


class CoverageContext(Coverage):
    """Context manager to start and stop code coverage.

    :param str report_dir: Path to where the coverage report shall be stored.
    """

    def __init__(self, report_dir: str) -> None:
        super().__init__()
        self._report_dir = f"{report_dir}/coverage"
        self.stdout = OutputWrapper(sys.stdout)
        self.stderr = OutputWrapper(sys.stderr)
        self.style = color.no_style()
        self.stderr.style_func = self.style.ERROR

    def __enter__(self) -> CoverageContext:
        self.erase()
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.stop()
        self.save()
        self.html_report(directory=self._report_dir)
        self.stdout.write(f'Generated coverage report: "{pathlib.Path(self._report_dir, "index.html").absolute()}"')


class CodeCoverageTestRunnerMixin:
    """A TestRunner mixin class which takes code coverage into account."""

    def __init__(self, **kwargs) -> None:
        code_coverage_disabled = not kwargs["code_coverage_enabled"]
        self._code_coverage = nullcontext() if code_coverage_disabled else CoverageContext(kwargs["report_dir"])
        super().__init__(**kwargs)

    def run_tests(self, test_labels, extra_tests=None, **kwargs) -> int:
        with self._code_coverage:
            return super().run_tests(test_labels, extra_tests, **kwargs)


class HtmlTestResult(TestResult):
    options: dict  # Will be set by the TestRunner

    supported_results = (
        'error',
        'failure',
        'unexpected_success',
        'precondition_failure',
        'expected_failure',
        'passed',
        'skipped',
    )

    TestResultData = namedtuple('TestResultData', field_names=('name', 'result', 'duration', 'outcome'))
    _subtest_result_map: defaultdict[unittest.case.TestCase, list[tuple[_SubTest, str, _SysExcInfoType]]]

    @classmethod
    def create_color_style(cls) -> color.Style:
        """Create and return a custom color style based on the available options.

        This method creates a custom color style for console output based on the available options.
        If the `no-color` option is set or the console does not support color, the style will be configured
        to have no color for each supported result. Otherwise, individual styles will be created for each
        supported result, such as 'RESULT_ERROR', 'RESULT_FAILURE', 'RESULT_SKIPPED', etc., with specific
        color and text formatting.

        :returns: A custom color style object for console output.
        """
        style = color.color_style()

        if cls.options.get("no_color") or not color.supports_color():
            for result in cls.supported_results:
                setattr(style, f"RESULT_{result.upper()}", termcolors.make_style(""))
        else:
            style.RESULT_ERROR = termcolors.make_style(fg='red', opts=('bold',))
            style.RESULT_FAILURE = termcolors.make_style(fg='yellow', opts=('bold',))
            style.RESULT_SKIPPED = termcolors.make_style(fg='white', opts=('bold',))
            style.RESULT_PASSED = termcolors.make_style(fg='green', opts=('bold',))
            style.RESULT_EXPECTED_FAILURE = termcolors.make_style(fg='magenta', opts=('bold',))
            style.RESULT_UNEXPECTED_SUCCESS = termcolors.make_style(fg='yellow', opts=('bold',))
            style.RESULT_PRECONDITION_FAILURE = termcolors.make_style(fg='yellow', opts=('bold',))

        return style

    def __init__(self, *args, tests=None, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.dots = False
        self.showAll = False
        self.passed = []
        self.precondition_failures = []
        self.timestamp_start_testrun = None
        self.timestamp_stop_testrun = None
        self._test_result_data = defaultdict(list)
        self._subtest_result_map = defaultdict(list)
        self._all_tests = tests

        self.stdout = OutputWrapper(sys.stdout)
        self.stderr = OutputWrapper(sys.stderr)
        self.style = self.create_color_style()
        self.stderr.style_func = self.style.ERROR

    def _add_test_result_data(self, test, result, outcome=None) -> None:
        if isinstance(test, _ErrorHolder):
            # In case an _ErrorHolder instance has been passed, which means setting up the testcase has been failed,
            # none of the testcase`s test methods have been executed, and thus they will all be set to the same result.
            parent = re.search(r'\((.+)\)', test.description).group(1)
            module, testcase_name = parent.rsplit('.', 1)
            testcase_class = getattr(sys.modules[module], testcase_name)
            for test in filter(lambda testmethod: isinstance(testmethod, testcase_class), self._all_tests):
                self._add_test_result_data(test, result, outcome)
        else:
            timestamp = getattr(test, 'timestamp', None)
            duration = (timezone.now() - timestamp) if timestamp else datetime.timedelta(0)
            self._test_result_data[strclass(type(test))].append(
                HtmlTestResult.TestResultData(getattr(test, '_testMethodName'), result, duration, outcome or '')
            )

            self.testsRun = sum(map(len, self._test_result_data.values()))
            self.print_test_result(test, result)

    def create_report(self, result_data: dict) -> None:
        if self.options.get('html_results_enabled'):
            # Create report directory
            report_dir = pathlib.Path(self.options.get('report_dir'))
            report_dir.mkdir(exist_ok=True)

            # Create html test report
            html_template = get_config()['TEST_REPORT_HTML_TEMPLATE']
            result_data['supported_results'] = self.supported_results
            result_data['title'] = self.options.get('report_title')
            html_data = render_to_string(html_template, context=result_data)
            results_html_file = report_dir / 'test-results.html'
            results_html_file.write_text(html_data)

            # Copy css file into the report directory
            with contextlib.suppress(TypeError):
                css_file = pathlib.Path(get_config()['TEST_REPORT_CSS'])
                if not css_file.is_absolute():
                    css_file = pathlib.Path(finders.find(css_file))
                results_html_file.with_name(css_file.name).write_text(css_file.read_text())
            js_file = pathlib.Path(finders.find(pathlib.Path('js', 'test-results.js')))
            (report_dir / 'test-results.js').write_text(js_file.read_text())
            self.stdout.write(f'Generated test report: "{results_html_file.absolute()}"')

    def make_result_data(self) -> Dict[str, Any]:
        test_suite_exec_summary = dict()
        test_suite_exec_summary['testcases'] = {}
        test_suite_exec_summary.setdefault(
            'summary',
            dict(  # noqa: C406
                [
                    ('duration', datetime.timedelta()),
                    ('totals', 0),
                    ('timestamp', self.timestamp_start_testrun),
                    *dict.fromkeys(self.supported_results, 0).items(),
                ]
            ),
        )

        for testcase, tests in self._test_result_data.items():
            test_suite_exec_summary['summary']['totals'] += len(tests)

            for test_result in tests:
                test_case_execution = test_suite_exec_summary['testcases'].setdefault(testcase, {})
                test_case_executed_tests = test_case_execution.setdefault('tests', [])
                test_case_execution_summary = test_case_execution.setdefault(
                    'summary',
                    dict(  # noqa: C406
                        [
                            ('duration', datetime.timedelta()),
                            ('totals', 0),
                            *dict.fromkeys(self.supported_results, 0).items(),
                        ]
                    ),
                )

                test_suite_exec_summary['summary']['duration'] += test_result.duration
                test_suite_exec_summary['summary'][test_result.result] += 1
                test_case_execution_summary['duration'] += test_result.duration
                test_case_execution_summary['totals'] += 1
                test_case_execution_summary[test_result.result] += 1
                test_case_executed_tests.append(test_result)

        return test_suite_exec_summary

    def startTestRun(self) -> None:
        """Called once before any tests are executed."""
        self.timestamp_start_testrun = timezone.now()
        self.timestamp_stop_testrun = None
        self.stdout.write()

    def startTest(self, test: unittest.case.TestCase) -> None:
        """Called when the given test is about to be run"""
        test.timestamp = test.start_time = timezone.now()
        super().startTest(test)

    def stopTestRun(self) -> None:
        """Called once after all tests are executed."""
        super().stopTestRun()
        self.timestamp_stop_testrun = timezone.now()

    def stopTest(self, test: unittest.case.TestCase) -> None:
        """Called when the given test has been run"""
        super().stopTest(test)
        test.stop_time = timezone.now()
        if subtests_results := self._subtest_result_map.pop(test, None):
            result, outcome = self._resolve_subtests_results(test, subtests_results)
            self._add_test_result_data(test, result, outcome)

    def addSkip(self, test: unittest.case.TestCase, reason: str) -> None:
        """Called when a test is skipped."""
        super().addSkip(test, reason)
        self._add_test_result_data(test, 'skipped', reason)

    def addSuccess(self, test: unittest.case.TestCase) -> None:
        """Called when a test has completed successfully"""
        self.passed.append((test, ''))
        self._add_test_result_data(test, 'passed')

    def addUnexpectedSuccess(self, test: unittest.case.TestCase) -> None:
        """Called when a test was expected to fail, but succeed."""
        super().addUnexpectedSuccess((test, ''))
        self._add_test_result_data(test, 'unexpected_success')

    def addFailure(self, test: unittest.case.TestCase, err: _SysExcInfoType) -> None:
        """Called when an error has occurred."""
        if getattr(err[1], '__precondition_failure__', None):
            self.addPreconditionFailure(test, err)
        else:
            super().addFailure(test, err)
            self._add_test_result_data(test, 'failure', self._exc_info_to_string(err, test))

    def addExpectedFailure(self, test: unittest.case.TestCase, err: _SysExcInfoType) -> None:
        """Called when an expected failure/error occurred."""
        super().addExpectedFailure(test, err)
        self._add_test_result_data(test, 'expected_failure', self._exc_info_to_string(err, test))

    def addError(self, test: unittest.case.TestCase, err: _SysExcInfoType) -> None:
        """Called when an error has occurred."""
        if getattr(err[1], '__precondition_failure__', None):
            self.addPreconditionFailure(test, err)
        else:
            super().addError(test, err)
            self._add_test_result_data(test, 'error', self._exc_info_to_string(err, test))

    def addPreconditionFailure(self, test: unittest.case.TestCase, err: _SysExcInfoType) -> None:
        """Called when a precondition error has occurred."""
        self.precondition_failures.append((test, self._exc_info_to_string(err, test)))
        self._mirrorOutput = True
        self._add_test_result_data(test, 'precondition_failure', self._exc_info_to_string(err, test))

    def addSubTest(self, test: unittest.case.TestCase, subtest, err: _SysExcInfoType) -> None:
        """Called at the end of a subtest."""
        if err is not None:
            self._apply_subtest_result(test, subtest, err)
            if getattr(self, 'failfast', False):
                self.stop()
            if issubclass(err[0], test.failureException):
                errors = self.failures
            elif issubclass(err[0], test.preconditionFailureException):
                errors = self.precondition_failures
            else:
                errors = self.errors
            errors.append((subtest, self._exc_info_to_string(err, test)))
            self._mirrorOutput = True

    def wasSuccessful(self) -> bool:
        """Tells whether or not this result was a success."""
        return len(self.precondition_failures) == 0 and super().wasSuccessful()

    def print_test_result(self, test: unittest.case.TestCase, result: str) -> None:
        max_result_width = max(map(len, self.supported_results)) + 10
        cur_result_width = len(result)
        style = getattr(self.style, f"RESULT_{result.upper()}")

        self.stdout.write(style(result.upper()), ending="")
        self.stdout.write("." * (max_result_width - cur_result_width), ending="")
        self.stdout.write(" " + str(test))

    def printErrors(self) -> None:
        results = list(map(attrgetter('result'), itertools.chain.from_iterable(self._test_result_data.values())))
        skipped = results.count('skipped')
        passed = results.count('passed')
        expected_failures = results.count('expected_failure')
        precondition_failures = results.count('precondition_failure')
        failures = results.count('failure')
        unexpected_successes = results.count('unexpected_success')
        errors = results.count('error')

        style = self.style.SUCCESS if self.wasSuccessful() else self.style.ERROR

        self.stdout.write()
        self.stdout.write(
            style(
                f'{"OK" if self.wasSuccessful() else "FAILED"} (skipped={skipped}, passed={passed}, '
                f'expected failures={expected_failures}, precondition failures={precondition_failures}, '
                f'failures={failures}, unexpected successes={unexpected_successes}, errors={errors})'
            )
        )

    def _resolve_subtests_results(
        self, test: unittest.case.TestCase, results: list[tuple[_SubTest, str, _SysExcInfoType]]
    ) -> tuple[str, str]:
        result_priority_map = {'error': 1, 'failure': 2, 'precondition_failure': 3}
        reverse_result_priority_map = {v: k for k, v in result_priority_map.items()}
        outcome = ''
        result_priority = max(reverse_result_priority_map) + 1
        for subtest, result, err in results:
            assert result in result_priority_map, f'Invalid subtest result: {result!r}'
            header = f'{result.upper()}: {subtest.id()}'
            outcome += (
                textwrap.dedent(
                    f"""\
            {len(header)*"="}
            {header}
            {len(header)*"-"}
            """
                )
                + self._exc_info_to_string(err, test)  # noqa: W503
                + 2 * '\n'  # noqa: W503
            )
            result_priority = min(result_priority_map[result], result_priority)
        result = reverse_result_priority_map[result_priority]
        return result, outcome.strip()

    def _apply_subtest_result(self, test: unittest.case.TestCase, subtest: _SubTest, err: _SysExcInfoType) -> None:
        if getattr(err[1], '__precondition_failure__', None):
            result = 'precondition_failure'
        elif issubclass(err[0], test.failureException):
            result = 'failure'
        else:
            result = 'error'
        self._subtest_result_map[test].append((subtest, result, err))


class HtmlTestRunner(TextTestRunner):
    resultclass = HtmlTestResult

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('stream', open(os.devnull, 'w'))
        super().__init__(*args, **kwargs)

    def run(self, test: unittest.suite.TestSuite) -> HtmlTestResult:
        # ToDo: Consider to override the run() method to keep 'test'
        self._tests = list(test)
        result = super().run(test)
        result.create_report(result.make_result_data())
        return result

    def _makeResult(self) -> HtmlTestResult:
        return self.resultclass(self.stream, self.descriptions, self.verbosity, tests=self._tests)


class TestRunner(CodeCoverageTestRunnerMixin, SnapshotTestRunnerMixin, DiscoverRunner):
    test_runner = HtmlTestRunner

    @classmethod
    def add_arguments(cls, parser) -> None:
        super().add_arguments(parser)

        parser.add_argument(
            "--html",
            action=argparse.BooleanOptionalAction,
            dest="html_results_enabled",
            default=get_config()["HTML_RESULTS_ENABLED"],
            help="Enables respectively disables html results instead of using the HTML_RESULTS_ENABLED setting.",
        )
        parser.add_argument(
            "--coverage",
            action=argparse.BooleanOptionalAction,
            default=get_config()["COVERAGE_REPORT_ENABLED"],
            dest="code_coverage_enabled",
            help="Enables respectively disables code coverage instead of using the COVERAGE_REPORT_ENABLED setting.",
        )
        parser.add_argument(
            "--report-dir",
            action="store",
            dest="report_dir",
            metavar="DIR",
            default=get_config()["TEST_REPORT_DIR"],
            help="Defines the directory where to store the report artifacts. "
            "If this isn't provided, the TEST_REPORT_DIR setting will be used.",
        )

        parser.add_argument(
            "--report-title",
            action="store",
            dest="report_title",
            metavar="TITLE",
            default=get_config()["TEST_REPORT_TITLE"],
            help="A string which defines the test-report`s title."
            "If this isn't provided, the TEST_REPORT_TITLE setting will be used.",
        )

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.test_runner.resultclass.options = kwargs

    def suite_result(self, suite, result, **kwargs):
        return super().suite_result(suite, result, **kwargs) + len(result.precondition_failures)
