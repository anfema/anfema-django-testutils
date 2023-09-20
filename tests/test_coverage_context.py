import os
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from django.core.management.base import OutputWrapper

from anfema_django_testutils.runner import CoverageContext


@patch.object(CoverageContext, 'start')
@patch.object(CoverageContext, 'erase')
@patch.object(CoverageContext, 'stop')
@patch.object(CoverageContext, 'save')
@patch.object(CoverageContext, 'html_report')
class CoverageContextTestCase(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report_dir = TemporaryDirectory()
        cls.null_stream = open(os.devnull, 'w')
        cls.coverage_context = CoverageContext(cls.report_dir)
        cls.coverage_context.stdout = OutputWrapper(cls.null_stream)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.report_dir.cleanup()
        cls.null_stream.close()

    def test_coverage_context_enter(
        self,
        mock_coverage_context_html_report,
        mock_coverage_context_save,
        mock_coverage_context_stop,
        mock_coverage_context_erase,
        mock_coverage_context_start,
    ):
        """Feature: Coverage Context

        Scenario: Entering Coverage Context
            Given a Coverage Context instance
            When entering the Coverage Context
            Then it should return the same instance
            And the 'start' method of Coverage Context should be called once
            And the 'erase' method of Coverage Context should be called once
        """
        self.assertIs(self.coverage_context.__enter__(), self.coverage_context)
        mock_coverage_context_start.assert_called_once()
        mock_coverage_context_erase.assert_called_once()

    def test_coverage_context_exit(
        self,
        mock_coverage_context_html_report,
        mock_coverage_context_save,
        mock_coverage_context_stop,
        mock_coverage_context_erase,
        mock_coverage_context_start,
    ):
        """Feature: Coverage Context

        Scenario: Exiting Coverage Context
            Given a Coverage Context instance
            When exiting the Coverage Context
            Then the 'stop' method of Coverage Context should be called once
            And the 'save' method of Coverage Context should be called once
            And the 'html_report' method of Coverage Context should be called once
            And it should specify the correct report directory
        """
        self.coverage_context.__exit__(None, None, None)
        mock_coverage_context_stop.assert_called_once()
        mock_coverage_context_save.assert_called_once()
        mock_coverage_context_html_report.assert_called_once_with(directory=f"{self.report_dir}/coverage")
