# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import pathlib
import sys


project_root_path = pathlib.Path(__file__).parents[2]
sys.path.insert(0, str(project_root_path))
from anfema_django_testutils import __version__ as version  # noqa: E402


# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'anfema-django-testutils'
copyright = '2022, anfema GmbH'
author = 'anfema GmbH'
release = version

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx_rtd_theme',
    'sphinx_copybutton',
    'sphinx.ext.autodoc',
    'sphinx_autodoc_typehints',
    'm2r2',
]

source_suffix = ['.rst', '.md']

templates_path = ['_templates']
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_static_path = ['_static']
html_theme = 'sphinx_rtd_theme'
html_theme_options = {
    'display_version': True,
    'navigation_depth': 1,
}

autodoc_member_order = 'bysource'

copybutton_prompt_text = r'>>> |\.\.\. |\$ |In \[\d*\]: | {2,5}\.\.\.: | {5,8}: '
copybutton_prompt_is_regexp = True

autodoc_mock_imports = ["django"]
