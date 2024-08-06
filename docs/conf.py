# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

# Add the path to modules and all subdirectories recursively
src_path = os.path.abspath('../src')
sys.path.insert(0, src_path)

for root, dirs, files in os.walk(src_path):
    for dir in dirs:
        sys.path.insert(0, os.path.join(root, dir))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'pydartdiags'
copyright = '2024, University Corporation for Atmospheric Research'
author = 'Helen Kershaw'
release = '0.0.3b'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = []

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']
html_theme_options = {
    'github_user': 'NCAR',
    'github_repo': 'pyDARTdiags',
    'github_button': 'true',
    'github_type': 'star',
    'fixed_sidebar': 'true',
    'sidebar_collapse': 'true',
    'sidebar_width': '325px',
    'page_width': '1200px',
    'show_powered_by' : 'false',
}



extensions = [
    'sphinx_copybutton',
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.todo',
]

