from django.core.files.storage import FileSystemStorage
from django.core.management.base import BaseCommand

from anfema_django_testutils.contrib.fixtures.finders.base import get_finders
from anfema_django_testutils.contrib.fixtures.settings import get_config


class Command(BaseCommand):
    """Copies fixture media files from different locations to the settings.MEDIA_ROOT."""

    help = "Collect fixture media files in a single location."
    verbosity: int

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.media_storage = FileSystemStorage()
        self.ignore_patterns = []

    def log(self, msg: str, *, level: int = 1, style=None) -> None:
        """Small log helper"""
        if self.verbosity >= level:
            self.stdout.write((style or str)(msg))

    def set_options(self, **options) -> None:
        self.verbosity = options["verbosity"]

    def handle(self, **options):
        self.set_options(**options)

        finders = get_config()["FIXTURE_MEDIAFILE_FINDERS"]
        for finder_class in get_finders(finders):
            for path, storage in finder_class.list(self.ignore_patterns):
                source_path = storage.path(path)

                self.media_storage.delete(path)
                with storage.open(source_path) as fp:
                    self.log(f"Copy {source_path} -> {self.media_storage.path(path)}")
                    self.media_storage.save(path, fp)
