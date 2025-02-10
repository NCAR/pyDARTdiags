=============
Install Guide
=============

Requirements
------------

pyDARTdiags currently supports Python 3.8 and above.
pyDARTdiags requires the following packages:

.. code-block :: text

    "pandas>=2.2.0",
    "numpy>=1.26",
    "plotly>=5.22.0",
    "pyyaml>=6.0.2",
    "matplotlib>=3.9.4"

Installation
------------

pyDARTdiags can be installed through pip.  We recommend installing pydartdiags in a virtual environment:

.. code-block :: text

    python3 -m venv dartdiags
    source dartdiags/bin/activate
    pip install pydartdiags