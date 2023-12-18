from pathlib import Path

from django.core.checks import Error, Warning

from .settings import get_config


def check_config(app_configs=None, **kwargs):
    """Check the configuration settings for correctness."""
    from .apps import FixturesConfig

    errors = []

    app_label = FixturesConfig.label
    config = get_config()

    if not isinstance(config["FIXTURE_FINDERS"], (tuple, list)):
        errors.append(
            Error(
                "The FIXTURE_FINDERS setting must be a list or tuple.",
                id=f"{app_label}.E001",
                obj="Improper Configuration",
            ),
        )
    if not isinstance(config["FIXTURE_DIRS"], (tuple, list)):
        errors.append(
            Error(
                "The FIXTURE_DIRS setting must be a a list or tuple.",
                id=f"{app_label}.E001",
                obj="Improper Configuration",
            ),
        )
    elif not all([isinstance(i, str) for i in config["FIXTURE_DIRS"]]):
        errors.append(
            Error(
                "At least one item of FIXTURE_DIRS settings is not a string.",
                id=f"{app_label}.E001",
                obj="Improper Configuration",
            ),
        )
    else:
        for path in filter(lambda p: not Path(p).exists(), config["FIXTURE_DIRS"]):
            errors.append(
                Warning(
                    f"The FIXTURE_DIRS settings contains a non-existing path: {path!r}.",
                    id=f"{app_label}.W001",
                    obj="Improper Configuration",
                ),
            )

    if not isinstance(config["FIXTURE_MEDIAFILE_FINDERS"], (tuple, list)):
        errors.append(
            Error(
                "The FIXTURE_MEDIAFILE_FINDERS setting must be a list or tuple.",
                id=f"{app_label}.E001",
                obj="Improper Configuration",
            ),
        )

    if not isinstance(config["FIXTURE_MEDIAFILE_DIRS"], (tuple, list)):
        errors.append(
            Error(
                "The FIXTURE_MEDIAFILE_DIRS setting must be a a list or tuple.",
                id=f"{app_label}.E001",
                obj="Improper Configuration",
            ),
        )
    elif not all([isinstance(i, str) for i in config["FIXTURE_MEDIAFILE_DIRS"]]):
        errors.append(
            Error(
                "At least one item of FIXTURE_MEDIAFILE_DIRS settings is not a string.",
                id=f"{app_label}.E001",
                obj="Improper Configuration",
            ),
        )
    else:
        for path in filter(lambda p: not Path(p).exists(), config["FIXTURE_MEDIAFILE_DIRS"]):
            errors.append(
                Warning(
                    f"The FIXTURE_MEDIAFILE_DIRS settings contains a non-existing path: {path!r}.",
                    id=f"{app_label}.W001",
                    obj="Improper Configuration",
                ),
            )

    return errors
