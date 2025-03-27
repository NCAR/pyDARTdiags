.. _devel:

=================
Developer Guide
=================

Contributions to pyDARTdiags are welcome! This page provides
information for developers of pyDARTdiags, including how to set up your development
environment and how to build the documentation locally. We also encourage you to read the
:doc:`contributors guide <CONTRIBUTING>`.

.. toctree::
   :hidden:
   :caption: Developer Guide

   CONTRIBUTING


Setting Up Your Development Environment
----------------------------------------

For developers of pyDARTdiags, we recommend installing pyDARTdiags as a local project in "editable" mode.
This allows you to make changes to the code and see the changes reflected in your environment without
having to reinstall the package.

To set up your development environment, follow these steps:

#. Create a Virtual Environment:

   .. code-block:: text

      python3 -m venv py-dart
      source py-dart/bin/activate 

#. Clone the Repository:

   .. code-block:: text

      git clone https://github.com/NCAR/pyDARTdiags.git
      cd pyDARTdiags

#. Install Dependencies:

   .. code-block:: text

      pip install -r docs/requirements.txt

#. Install the Package in Editable Mode:

   .. code-block:: text

      pip install -e .

pyDARTdiags is now installed in your virtual environment in editable mode.


Building the Documentation Locally
----------------------------------

The documentation is built using Sphinx, is written in rst or MyST, and can be found in the docs
directory. The API guide is built directly from docstrings in the python code, using Sphinx autodoc.

You can build the documentation with the following commands:

.. code-block :: text

   cd docs
   make html

The built documentation will be in the ``build/html`` directory. Open the ``index.html`` 
file in your browser to view the documentation.

You can check all the links in the documentation by running the following command:

.. code-block :: text

   make linkcheck

Creating Examples
-----------------

We use `Sphinx-Gallery <https://sphinx-gallery.github.io/stable/index.html>`_ to create 
examples for the documentation. The examples are in the ``pyDARTdiags/examples`` directory.
To create a new example, create a new Python file called ``plot_example_name.py`` 
in the appropriate subdirectory. The example will be run when the documentation is built.
For details on structuring your Sphinx-Gallery files take a look at the 
`Sphinx-Gallery syntax <https://sphinx-gallery.github.io/stable/syntax.html>`_.

Linting your code
-----------------

We use `black <https://black.readthedocs.io/en/stable/>`_ for code formatting.
Black will change your code to conform to the black style guide. To run black on the
pyDARTdiags code, run the following command at the root of the repository:

.. code-block :: text

   black src/pydartdiags

Black is run on pull requests to ensure that the code is formatted correctly.

Writing Tests
-------------

We use `pytest <https://docs.pytest.org/en/stable/>`_ for testing. Tests are in the test directory.
The test/data directory is used to store small files used for testing. It is not for storing large
files. 

.. code-block :: text

   pyDARTdiags/
               ├── docs/
               ├── src/
               ├── tests/
                         ├── data/      

To run the tests, you can use the following command:

.. code-block :: text

   pytest tests

Code Coverage
-------------

We use `Codecov <https://about.codecov.io/>`_ to measure the percentage of code covered by tests. 
You can view the code coverage reports for the project at 
`Codecov for pyDARTdiags <https://app.codecov.io/gh/NCAR/pyDARTdiags>`_.
Code coverage for the test can be calculated locally using the pytest-cov package. 

To create the coverage report, run the following command in the root directory:

.. code-block :: text

   pytest --cov=src tests

The coverage report will be displayed in the terminal.

To create a coverage report in HTML format, run the following command:

.. code-block :: text

   pytest --cov=src --cov-report=html
