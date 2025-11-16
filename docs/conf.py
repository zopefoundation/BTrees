# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import datetime


# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
year = datetime.datetime.now().year

project = 'BTrees'
copyright = f'2012-{year}, Zope Foundation and contributors'
author = 'Zope Foundation and contributors'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.doctest',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    'sphinx.ext.viewcode',
    'repoze.sphinx.autointerface',
]

autodoc_default_options = {
    'members': None,
    'show-inheritance': None,
    'special-members': None,
    'undoc-members': None,
}
autodoc_member_order = 'groupwise'
autoclass_content = 'both'

templates_path = ['_templates']
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'furo'
html_static_path = ['_static']
html_css_files = [
    'custom.css'
]


# Example configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'persistent': ("https://persistent.readthedocs.io/en/latest/", None),
    'zodb': ("https://zodb.org/en/latest/", None),
    'zopeinterface': ("https://zopeinterface.readthedocs.io/en/latest/", None),
}
