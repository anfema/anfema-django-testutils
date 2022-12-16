from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AnfemaDjangoTestutilsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "anfema_django_testutils"
    label = "anfema_django_testutils"
    verbose_name = _("anfema django testutils")
