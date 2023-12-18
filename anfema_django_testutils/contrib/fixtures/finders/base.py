from typing import Generator, Union

from django.contrib.staticfiles.finders import (
    AppDirectoriesFinder,
    BaseFinder,
    FileSystemFinder,
    FileSystemStorage,
    get_finder,
)


def find_file(finders, path: str, all: bool = False) -> Union[str, list[str], None]:
    """Find a fixture media file with the given path using all enabled fixture media files finders.

    :param str path: Path to search for.
    :param bool all: Defines whether to return only the first match or search for all matches.
    :return: If ``all`` is ``False`` (default), return the first matching absolute path (or ``None``
             if no match). Otherwise return a list.
    """
    matches = []
    for finder in get_finders(finders):
        result = finder.find(path, all=all)
        if not all and result:
            return result
        matches.extend([result] if not isinstance(result, (list, tuple)) else result)
    return matches or ([] if all else None)


def get_finders(finders: list[str]) -> Generator[BaseFinder, None, None]:
    """Yield enabled finder classes listed in *finders*."""
    yield from map(get_finder, finders)


class BaseFileSystemFinder(FileSystemFinder):
    search_dirs: list[str]

    def __init__(self, app_names=None, *args, **kwargs):
        self.locations = []
        self.storages = {}
        for root in self.search_dirs:
            if isinstance(root, (list, tuple)):
                prefix, root = root
            else:
                prefix = ""
            if (prefix, root) not in self.locations:
                self.locations.append((prefix, root))
        for prefix, root in self.locations:
            filesystem_storage = FileSystemStorage(location=root)
            filesystem_storage.prefix = prefix
            self.storages[root] = filesystem_storage
        super(BaseFinder, self).__init__(*args, **kwargs)

    def check(self):
        raise NotImplementedError


class BaseAppDirectoriesFinder(AppDirectoriesFinder):
    def check(self):
        raise NotImplementedError
