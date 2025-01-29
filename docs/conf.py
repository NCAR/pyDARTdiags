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

project = 'pyDARTdiags'
copyright = '2024, University Corporation for Atmospheric Research'
author = 'Helen Kershaw'
#release = '0.0.42'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = []

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "pydata_sphinx_theme"
html_theme_options = {
    'external_links': [
        {'name': 'Release Notes', 'url': 'https://github.com/NCAR/pyDARTdiags/releases'},
    ],
    'icon_links': [
        {
            'name': 'GitHub',
            'url': 'https://github.com/NCAR/pyDARTdiags',
            'icon': 'fa-brands fa-github',
            'type': 'fontawesome',
        },
    ],
#    'navbar_align': 'left0',
    'use_edit_page_button': False,
    'navbar_start': ['navbar-logo'],
    'navbar_center': ['navbar-nav'],
    'header_links_before_dropdown': 6,
    'navbar_end': ['navbar-icon-links', 'theme-switcher'],
    "announcement": "WARNING: pyDARTdiags is currently in alpha stage of development - expect bugs and changes", 
}
html_show_sourcelink = False
html_title = project

extensions = [
    'sphinx_copybutton',
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.todo',
    'myst_parser',
    'sphinx_design',
    'sphinx_gallery.gen_gallery'
]

sphinx_gallery_conf = {
     'examples_dirs': '../examples',   # path to your example scripts
     'gallery_dirs': 'examples',  # path to where to save gallery generated output
     'default_thumb_file': 'images/py-dart-logo-thumb.png',
}
