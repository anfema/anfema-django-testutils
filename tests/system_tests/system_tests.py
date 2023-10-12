import ast
import contextlib
import importlib.util
import shutil
import subprocess
import sys
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any
from unittest import TestCase

from anfema_django_testutils.settings import CONFIG_DEFAULTS


class SystemTestMixin:
    extra_settings: dict[str, Any] = None

    @classmethod
    def get_base_setting_file(cls) -> Path:
        """Returns the path to the base settings file for the test project."""
        return Path.cwd().joinpath("test_project", "settings.py")

    @classmethod
    def setUpClass(cls) -> None:
        cls._tmp_setting_file = cls.create_settings_file(**cls.extra_settings or {})

    @classmethod
    def tearDownClass(cls) -> None:
        cls._tmp_setting_file.close()

    @classmethod
    def create_settings_file(cls, **extra_settings) -> tuple[Path, Path]:
        """Creates a settings file based on the base settings file and with the given settings."""
        base_settings_file = cls.get_base_setting_file()
        tmp_setting_file = NamedTemporaryFile(dir=Path.cwd(), prefix="test_settings_", suffix=".py", mode="w")
        settings_file = Path(tmp_setting_file.name)

        settings_module_ast = ast.parse(base_settings_file.read_text())
        settings_module_ast.body.extend(
            [
                ast.Assign(targets=[ast.Name(id=k, ctx=ast.Store())], value=ast.Constant(value=v))
                for k, v in extra_settings.items()
            ]
        )
        settings_file.write_text(ast.unparse(ast.fix_missing_locations(settings_module_ast)))

        return tmp_setting_file

    @property
    def settings_file(self) -> Path:
        """Provides the path to the test project settings file."""
        return Path(self._tmp_setting_file.name)

    @contextlib.contextmanager
    def override_test_project_settings(self, **configs):
        settings_module_ast = ast.parse(settings_file_content := self.settings_file.read_text())

        for node in settings_module_ast.body:
            if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name):
                target_name = node.targets[0].id
                if target_name in configs:
                    node.value = ast.Constant(value=configs[target_name])

        settings_module_ast.body.extend(
            [
                ast.Assign(targets=[ast.Name(id=k, ctx=ast.Store())], value=ast.Constant(value=v))
                for k, v in configs.items()
                if k not in {node.targets[0].id for node in settings_module_ast.body if isinstance(node, ast.Assign)}
            ]
        )

        self.settings_file.write_text(ast.unparse(ast.fix_missing_locations(settings_module_ast)))

        try:
            yield
        finally:
            self.settings_file.write_text(settings_file_content)

    def get_setting(self, setting: str, default: Any = None) -> Any:
        """Retrieves a configuration from the settings file."""
        settings_module = importlib.import_module(self.settings_file.stem)
        return getattr(*[settings_module, setting] + [default] if default else [])

    def execute_django_tests(self, *tests: str):
        tests_module_parent = __name__.rsplit('.', 1)[0]
        tests = " ".join(f"{tests_module_parent}.{test}" for test in tests)

        args = [
            sys.executable,
            "-m",
            "manage",
            "test",
            tests,
            "--settings",
            self.settings_file.stem,
            "--testrunner",
            "anfema_django_testutils.runner.TestRunner",
        ]

        return subprocess.run(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )

    def remove_test_report_dir(self) -> None:
        """Removes the test report directory."""

        if (test_report_dir := Path(self.get_setting("TEST_REPORT_DIR", CONFIG_DEFAULTS["TEST_REPORT_DIR"]))).exists():
            shutil.rmtree(test_report_dir)

    def setUp(self):
        self.remove_test_report_dir()
        super().setUp()

    def tearDown(self):
        super().tearDown()
        self.remove_test_report_dir()

    def assertTestReportArtifacts(
        self, *, expect_html_report_artifacts: bool = None, expect_coverage_report_artifacts: bool = None
    ):
        test_report_dir = self.get_setting("TEST_REPORT_DIR", CONFIG_DEFAULTS["TEST_REPORT_DIR"])
        test_report_css = self.get_setting("TEST_REPORT_CSS", CONFIG_DEFAULTS["TEST_REPORT_CSS"])

        if expect_html_report_artifacts is not None:
            self.assertEqual(
                expect_html_report_artifacts,
                (file := Path(test_report_dir, "test-results.html")).exists(),
                msg=f"{file} is unexpectedly missing."
                if expect_html_report_artifacts
                else f"{file} unexpectedly exists.",
            )
            self.assertEqual(
                expect_html_report_artifacts,
                (file := Path(test_report_dir, Path(test_report_css).name)).exists(),
                msg=f"{file} is unexpectedly missing."
                if expect_html_report_artifacts
                else f"{file} unexpectedly exists.",
            )
            self.assertEqual(
                expect_html_report_artifacts,
                (file := Path(file := test_report_dir, "test-results.js")).exists(),
                msg=f"{file} is unexpectedly missing."
                if expect_html_report_artifacts
                else f"{file} unexpectedly exists.",
            )

        if expect_coverage_report_artifacts is not None:
            self.assertEqual(
                expect_coverage_report_artifacts,
                (file := Path(test_report_dir, "coverage", "index.html")).exists(),
                msg=f"{file} is unexpectedly missing."
                if expect_coverage_report_artifacts
                else f"{file} unexpectedly exists.",
            )


class ExitCodeTests(SystemTestMixin, TestCase):
    settings: dict[str, Any] = CONFIG_DEFAULTS

    def test_exit_codes(self):
        for test, expected_exit_code in [
            ("result_tests.ResultTests.test_skip", 0),
            ("result_tests.ResultTests.test_success", 0),
            ("result_tests.ResultTests.test_expected_failure", 0),
            ("result_tests.ResultTests.test_precondition_failure", 1),
            ("result_tests.ResultTests.test_failure", 1),
            ("result_tests.ResultTests.test_unexpected_success", 1),
            ("result_tests.ResultTests.test_error", 1),
            ("result_tests.ResultTests.test_subtest_success", 0),
            ("result_tests.ResultTests.test_subtest_expected_failure", 0),
            ("result_tests.ResultTests.test_subtest_precondition_failure", 1),
            ("result_tests.ResultTests.test_subtest_failure", 1),
            ("result_tests.ResultTests.test_subtest_unexpected_success", 1),
            ("result_tests.ResultTests.test_subtest_error", 1),
            ("result_tests.SetupFailPreconditionFailure.test_setup_precondition_failure", 1),
            ("result_tests.SetupTestDataError.test_setup_test_data_error", 1),
            ("test_setup_test_data_assertion_fails", 1),
        ]:
            with self.subTest(
                test=test,
                expected_exit_code=expected_exit_code,
            ):
                self.remove_test_report_dir()
                proc = self.execute_django_tests(test)
                self.assertEqual(proc.returncode, expected_exit_code)
                self.assertTestReportArtifacts(expect_html_report_artifacts=True, expect_coverage_report_artifacts=True)


class BasicConfigHtmlReportDisabledTests(SystemTestMixin, TestCase):
    def test_all_report_artifacts_on_default_settings(self):
        self.execute_django_tests("result_tests.ResultTests.test_success")
        self.assertTestReportArtifacts(expect_html_report_artifacts=True, expect_coverage_report_artifacts=True)

    def test_no_html_report_if_html_results_is_disabled(self):
        with self.override_test_project_settings(HTML_RESULTS_ENABLED=False):
            self.execute_django_tests("result_tests.ResultTests.test_success")
        self.assertTestReportArtifacts(expect_html_report_artifacts=False, expect_coverage_report_artifacts=True)

    def test_no_coverage_report_if_coverage_report_is_disabled(self):
        with self.override_test_project_settings(COVERAGE_REPORT_ENABLED=False):
            self.execute_django_tests("result_tests.ResultTests.test_success")
        self.assertTestReportArtifacts(expect_html_report_artifacts=True, expect_coverage_report_artifacts=False)

    def test_no_report_artifacts_if_html_report_and_coverage_report_are_disabled(self):
        with self.override_test_project_settings(HTML_RESULTS_ENABLED=False, COVERAGE_REPORT_ENABLED=False):
            self.execute_django_tests("result_tests.ResultTests.test_success")
        self.assertTestReportArtifacts(expect_html_report_artifacts=False, expect_coverage_report_artifacts=False)

    def test_default_test_report_dir_setting(self):
        directory_name = CONFIG_DEFAULTS["TEST_REPORT_DIR"]
        self.execute_django_tests("result_tests.ResultTests.test_success")
        self.assertTrue(Path(directory_name).exists(), msg=f"Test report directory {directory_name!r} is missing.")

    def test_test_report_dir_setting(self):
        with self.override_test_project_settings(TEST_REPORT_DIR=(directory_name := "another-test-report-dir")):
            self.execute_django_tests("result_tests.ResultTests.test_success")

        try:
            self.assertTrue(Path(directory_name).exists(), msg=f"Test report directory {directory_name!r} is missing.")
        finally:
            shutil.rmtree(directory_name)
