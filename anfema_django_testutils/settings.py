from __future__ import annotations

from functools import lru_cache
from typing import TYPE_CHECKING

from django.conf import settings
from django.dispatch import receiver
from django.test.signals import setting_changed


if TYPE_CHECKING:
    from typing import Any

CONFIG_DEFAULTS = {
    "TEST_REPORT_DIR": "test-report",
    "TEST_REPORT_HTML_TEMPLATE": "test-results-template.html",
    "TEST_REPORT_CSS": "css/test-results.css",
    "COVERAGE_REPORT_ENABLED": True,
    "HTML_RESULTS_ENABLED": True,
    "TEST_REPORT_TITLE": "Test Results",
}


@lru_cache()
def get_config() -> dict[str, Any]:
    """Returns the current configuration"""
    return {conf: getattr(settings, conf, default) for conf, default in CONFIG_DEFAULTS.items()}


@receiver(setting_changed)
def update_testrunner_config(*, setting, **kwargs) -> None:
    """Refresh configuration when overriding settings."""
    if setting in CONFIG_DEFAULTS:
        get_config.cache_clear()
