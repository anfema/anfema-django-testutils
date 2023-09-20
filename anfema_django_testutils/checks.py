from django.contrib.staticfiles import finders as staticfiles_finders
from django.core.checks import Error
from django.template.loader import TemplateDoesNotExist, get_template

from .settings import get_config


def check_config(app_configs, **kwargs):
    """Check the configuration settings for correctness."""
    from .apps import AnfemaDjangoTestutilsConfig

    app_label = AnfemaDjangoTestutilsConfig.label
    config = get_config()
    errors = []

    if not isinstance(config["TEST_REPORT_DIR"], str):
        errors.append(
            Error(
                "The TEST_REPORT_DIR setting must be a string.",
                id=f"{app_label}.E001",
                obj="Improper Configuration",
            ),
        )

    if not isinstance(test_report_html_template := config["TEST_REPORT_HTML_TEMPLATE"], str):
        errors.append(
            Error(
                "The TEST_REPORT_HTML_TEMPLATE setting must be a string.",
                id=f"{app_label}.E001",
                obj="Improper Configuration",
            ),
        )
    else:
        try:
            get_template(test_report_html_template)
        except TemplateDoesNotExist:
            errors.append(
                Error(
                    f"Could not find test report html template: {test_report_html_template!r}.",
                    id=f"{app_label}.E001",
                    obj="Improper Configuration",
                ),
            )

    if not isinstance(test_report_css := config["TEST_REPORT_CSS"], str):
        errors.append(
            Error(
                "The TEST_REPORT_CSS setting must be a string.",
                id=f"{app_label}.E001",
                obj="Improper Configuration",
            ),
        )
    elif not staticfiles_finders.find(test_report_css):
        errors.append(
            Error(
                f"Could not find test report css file: {test_report_css!r}.",
                id=f"{app_label}.E001",
                obj="Improper Configuration",
            ),
        )

    if not isinstance(config["COVERAGE_REPORT_ENABLED"], bool):
        errors.append(
            Error(
                "The COVERAGE_REPORT_ENABLED setting must be a boolean.",
                id=f"{app_label}.E001",
                obj="Improper Configuration",
            ),
        )

    if not isinstance(config["HTML_RESULTS_ENABLED"], bool):
        errors.append(
            Error(
                "The HTML_RESULTS_ENABLED setting must be a boolean.",
                id=f"{app_label}.E001",
                obj="Improper Configuration",
            ),
        )

    if not isinstance(config["TEST_REPORT_TITLE"], str):
        errors.append(
            Error(
                "The TEST_REPORT_TITLE setting must be a string.",
                id=f"{app_label}.E001",
                obj="Improper Configuration",
            ),
        )

    return errors
