from pathlib import Path

from django.core.management.base import LabelCommand

from anfema_django_testutils.contrib.fixtures import finders


class Command(LabelCommand):
    help = "Finds the absolute paths for the given fixture file(s)."
    label = "FILE"

    def add_arguments(self, parser) -> None:
        super().add_arguments(parser)
        parser.add_argument(
            "--first",
            action="store_false",
            dest="all",
            help="Only return the first match for each fixture file.",
        )

    def log(self, msg: str, *, level: int = 1, style=None) -> None:
        """Small log helper"""
        if self.verbosity >= level:
            self.stdout.write((style or str)(msg))

    def set_options(self, **options) -> None:
        self.verbosity: int = options["verbosity"]
        self.all: bool = options["all"]

    def handle(self, *labels, **options):
        self.set_options(**options)
        return super().handle(*labels, **options)

    def handle_label(self, path, **options):
        result = finders.fixture.find(path, all=self.all)

        if result:
            if not isinstance(result, (list, tuple)):
                result = [result]
            self.log(f"Found {path!r} here:", level=1)
            for found_path in map(Path, result):
                self.log(f"  {found_path.resolve()}", level=1)
        else:
            self.log(f"No matching file found for {path!r}", level=1, style=self.style.ERROR)
        self.log("")
