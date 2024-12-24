.. _devel:

=================
Developer Guide
=================

Contributions to pyDARTdiags are welcome! We encourage you to contribute to pyDARTdiags by
reporting issues, suggesting new features, and submitting pull requests.  This page provides
information for developers of pyDARTdiags, including how to set up your development
environment and how to build the documentation locally. We also encourage you to read the
:doc:`contributors guide <CONTRIBUTING>`.


.. toctree::
   :maxdepth: 1
   :hidden:

   CONTRIBUTING


Editable Installation
---------------------

For developers of pyDARTdiags, we recommend installing pyDARTdiags as a 
local project in “editable” mode in your virtual environment. This allows you to
make changes to the code and see the changes reflected in your environment without
having to reinstall the package.

.. code-block :: text

   git clone https://github.com/NCAR/pyDARTdiags
   python -m pip install -e pyDARTdiags



Building the Documentation Locally
----------------------------------

To build the documentation locally, you will need to install the dependencies. 
The dependencies are listed in the ``docs/requirements.txt`` file. You can install
the dependencies with the following command:

.. code-block :: text

   python -m pip install -r docs/requirements.txt

Then you can build the documentation with the following commands:

.. code-block :: text

   cd docs
   make html

The built documentation will be in the ``build/html`` directory. Open the ``index.html`` 
file in your browser to view the documentation.


Writing Tests
-------------

We use `pytest <https://docs.pytest.org/en/stable/>`_ for testing. Tests are in the test directory.
The test/data directory is used to store small files used for testing. It is not for storing large
files. 

.. code-block :: text

   pyDARTdiags/
               ├── docs/
               ├── src/
               ├── test/
                        ├── data/      

To run the tests, you can use the following command:

.. code-block :: text

   pytest tests