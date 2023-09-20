from typing import Generator, Union

import django.contrib.staticfiles.finders
from django.apps import apps
from django.contrib.staticfiles.finders import BaseFinder
from django.contrib.staticfiles.utils import matches_patterns
from django.core.files.storage import FileSystemStorage

from ..settings import get_config
from .base import BaseAppDirectoriesFinder, BaseFileSystemFinder


searched_locations = django.contrib.staticfiles.finders.searched_locations


class FileSystemFinder(BaseFileSystemFinder):
    """A fixture files finder that that uses the ``FIXTURES_DIRS`` setting to locate fixture files."""

    search_dirs = get_config()["FIXTURE_DIRS"]

    def list(
        self, fixture_suffixes: list[str] = None, ignore_patterns: list[str] = None
    ) -> Generator[tuple[str, FileSystemStorage], None, None]:
        """Yields all fixture files found in the folder defined by the ``FIXTURES_DIRS`` setting.

        :param list fixture_suffixes: A list of file suffixes to match for fixture files.
        :param list ignore_patterns: A list of patterns to ignore when searching for fixtures.
        """
        patterns = [f"*{suffix}" for suffix in (fixture_suffixes or apps.get_app_config("fixtures").fixture_suffixes)]
        yield from filter(lambda p: matches_patterns(p[0], patterns), super().list(ignore_patterns))


class AppDirectoriesFinder(BaseAppDirectoriesFinder):
    """A fixture files finder that looks in the :file:`fixtures` folder of each app."""

    def __init__(self, app_names=None, *args, **kwargs):
        self.source_dir = apps.get_app_config("fixtures").fixture_source_dir
        super().__init__(app_names=None, *args, **kwargs)

    def list(
        self, fixture_suffixes: list[str] = None, ignore_patterns: list[str] = None
    ) -> Generator[tuple[str, FileSystemStorage], None, None]:
        """Yields all fixture files found in the :file:`fixtures` folder of each app.

        :param list fixture_suffixes: A list of file suffixes to match for fixture files.
        :param list ignore_patterns: A list of patterns to ignore when searching for fixtures.
        """

        patterns = [f"*{suffix}" for suffix in (fixture_suffixes or apps.get_app_config("fixtures").fixture_suffixes)]
        yield from filter(lambda p: matches_patterns(p[0], patterns), super().list(ignore_patterns))


def find(path: str, all: bool = False) -> Union[str, list[str], None]:
    """Find a fixture file with the given path using all enabled fixture files finders.

    :param str path: Path to search for.
    :param bool all: Defines whether to return only the first match or search for all matches.
    :return: If ``all`` is ``False`` (default), return the first matching absolute path (or ``None``
             if no match). Otherwise return a list.
    """
    searched_locations[:] = []
    matches = []
    for finder in get_finders():
        result = finder.find(path, all=all)

        if not all and result:
            return result
        if not isinstance(result, (list, tuple)):
            result = [result]
        matches.extend(result)
    return matches or ([] if all else None)


def get_finders() -> Generator[BaseFinder, None, None]:
    """Yield enabled fixture files finder classes."""
    finders = get_config()["FIXTURE_FINDERS"]
    yield from map(get_finder, finders)


def get_finder(import_path) -> BaseFinder:
    """Import a given fixture files finder class.

    :param str import_path: The full Python path to the class to be imported
    """
    return django.contrib.staticfiles.finders.get_finder(import_path)
