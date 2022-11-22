Configuration
~~~~~~~~~~~~~

Django settings
---------------

Update your django :file:`settings.py` to use the :mod:`anfema_django_testutils` test runner:

.. code-block::

    # settings.py

    INSTALLED_APPS = [
        ...
        "mathfilters",
        "anfema_django_testutils",
    ]

    ...

    TEST_RUNNER = "anfema_django_testutils.runner.TestRunner"


Options
-------
The :mod:`anfema_django_testutils` provides some options that can be set in your django :file:`settings.py`:

.. option:: COVERAGE_REPORT_ENABLED

    If set to :code:`True` (default), a coverage report will be generated.

.. option:: HTML_RESULTS_ENABLED

    If set to :code:`True` (default), test results will be stored within an HTML report.

.. option:: TEST_REPORT_DIR

    A string which defines the path to where the test report will be stored.

    | Default is :code:`"test-report"`.

.. option:: TEST_REPORT_HTML_TEMPLATE

    A string which defines the HTML template to be used to generate the test report.

    | Default is :code:`"test-results-template.html"`.

.. option:: TEST_REPORT_CSS

    A string which defines the CSS file to be used by the test test report generator.

    | Default is :code:`"test-results.css"`.

Coverage settings
-----------------

The coverage options can be specified in the projects :file:`pyproject.toml` file,
for instance:

.. code-block:: toml

    [tool.coverage.report]
    exclude_lines = [
        "pragma: no cover",
        "if TYPE_CHECKING:",
    ]
    skip_empty = true
    omit = [
        "*/tests/*",
        "*/tests.py",
    ]

See the `coverage documentation <https://coverage.readthedocs.io/en/6.5.0/config.html#configuration-reference>`_ for more information.

Running tests
-------------

Using the :mod:`anfema_django_testutils` app extends

.. code-block:: bash

    $ python manage.py test

by following parameters:

.. code-block:: text

  --snapshot-update     Update the snapshots automatically.
  --html, --no-html     Enables respectively disables html results instead of
                        using the HTML_RESULTS_ENABLED setting. (default:
                        True)
  --coverage, --no-coverage
                        Enables respectively disables code coverage instead of
                        using the COVERAGE_REPORT_ENABLED setting. (default:
                        True)
  --report-dir DIR      Defines the directory where to store the report
                        artifacts. If this isn't provided, the TEST_REPORT_DIR
                        setting will be used.