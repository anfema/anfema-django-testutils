from __future__ import annotations

from functools import lru_cache
from typing import TYPE_CHECKING

from django.conf import settings
from django.dispatch import receiver
from django.test.signals import setting_changed


if TYPE_CHECKING:
    from typing import Any


CONFIG_DEFAULTS = {
    "FIXTURE_FINDERS": ["anfema_django_testutils.contrib.fixtures.finders.fixture.AppDirectoriesFinder"],
    "FIXTURE_DIRS": [],
    "FIXTURE_MEDIAFILE_FINDERS": ["anfema_django_testutils.contrib.fixtures.finders.media.AppDirectoriesFinder"],
    "FIXTURE_MEDIAFILE_DIRS": [],
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
