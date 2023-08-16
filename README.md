# anfema-django-testutils
The main intention of the `anfema_django_testutils` app is to provide a Django test runner which considers
snapshot tests as well as code coverage and human-readable html test reports. Moreover, the test result
`Precondition Failure` has been added.

This package integrates [snapshottest](https://github.com/syrusakbary/snapshottest) as well as
[coverage](https://coverage.readthedocs.io/en/latest/).

`anfema_django_testutils` is supported on:
- Python >= 3.9


- Source available at: https://github.com/anfema/anfema-django-testutils
- Documentation: https://anfema.github.io/anfema-django-testutils/index.html

## Installation
```bash
$ pip install anfema-django-testutils
```
## Setting up

Update your Django `settings.py` to use the `anfema_django_testutils` test runner:
```python
# settings.py

INSTALLED_APPS = [
    ...
    "mathfilters",
    "anfema_django_testutils",
]

TEST_RUNNER = "anfema_django_testutils.runner.TestRunner"
```

For further information see the `anfema_django_testutils` documentation.

## Usage
For writing test cases use the `anfema_django_testutils.testcases.TestCase` rather than the `django.test.TestCase`:

```python
# app/tests.py

from anfema_django_testutils.testcases import TestCase


class CustomTest(TestCase):
    ...
```

## Create documentation
To generate the `anfema_django_testutils` documentation from the local sources, run in a terminal:

```bash
$ pip install tox
```

```bash
$ tox -e docs -- docs/build
```

## License
Licensed under the MIT-clause license; see `LICENSE` for details.
