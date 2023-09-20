from __future__ import annotations

from typing import Union

from django.apps import apps

from ..settings import get_config
from .base import BaseAppDirectoriesFinder, BaseFileSystemFinder, find_file


class FileSystemFinder(BaseFileSystemFinder):
    """A media files finder that uses the ``FIXTURE_MEDIAFILE_DIRS`` setting to locate files."""

    search_dirs = get_config()["FIXTURE_MEDIAFILE_DIRS"]


class AppDirectoriesFinder(BaseAppDirectoriesFinder):
    """A media files finder that looks in the :file:`fixtures/media` folder of each app."""

    def __init__(self, app_names=None, *args, **kwargs):
        self.source_dir = apps.get_app_config("fixtures").fixturemedia_source_dir
        super().__init__(app_names=None, *args, **kwargs)


def find(path: str, all: bool = False) -> Union[str, list[str], None]:
    """Find a fixture media file with the given path using all enabled fixture media files finders.

    :param str path: Path to search for.
    :param bool all: Defines whether to return only the first match or search for all matches.
    :return: If ``all`` is ``False`` (default), return the first matching absolute path (or ``None``
             if no match). Otherwise return a list.
    """
    return find_file(get_config()["FIXTURE_MEDIAFILE_FINDERS"], path, all)
