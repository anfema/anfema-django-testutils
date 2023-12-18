"""Collection of various django related test utilities."""

__version__ = "0.8.0"


def load_tests(loader, tests, pattern):
    # Only consider tests within the tests folder. Otherwise the testcases module
    # produces conflicts with the standard pattern.
    return loader.discover(f"{__path__[0]}/tests", top_level_dir=__path__[0])
