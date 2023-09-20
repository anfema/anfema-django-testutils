import os

from django.apps import AppConfig
from django.core.checks import register
from django.utils.translation import gettext_lazy as _

from .checks import check_config


class FixturesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "anfema_django_testutils.contrib.fixtures"
    label = "fixtures"
    verbose_name = _("fixtures")

    fixture_source_dir = "fixtures"
    fixture_suffixes = [".json", ".yaml", ".yml", ".xml"]

    fixturemedia_source_dir = os.path.join(fixture_source_dir, "media")

    def ready(self):
        register(check_config, self.name)
