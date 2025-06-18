.. _working-with-obsq:

=======================================
Observation Sequences
=======================================

DART uses observation sequence files to store observations and their associated
metadata. These files are used as input/output for the DART assimilation system.

There are three types of observation sequence file:

- **obs_seq.in**: A 'blank' observation sequence file which contains the locations of observations and their
  associated metadata, but no observation values. Typically this file is used as input for creating synthetic observations
  for a perfect-model or Observation System Simulation Experiment (OSSE) experiment.
- **obs_seq.out**: A observation sequence file which contains observations and their associated metadata. This 
  is used as input to filter, the DART assimilation program.
- **obs_seq.final**: A observation sequence file which contains the observations and their
  associated metadata after assimilation. This file is created by filter, the DART assimilation program.
  The assimilation data is the mean and standard deviation of the forward operator for 
  each observation, and optionally each ensemble members value of the forward operator.
  The prior assimilation data is always present in the observation sequence file after
  assimilation, the posterior assimilation data is only present if the user chooses to do
  posterior forward operator calculations.



Working with Observation Sequence Objects
=========================================

PyDARTdiags enables you to interact with DART observation sequence files
using Python and `Pandas <https://pandas.pydata.org/>`_ - the Python Data Analysis Library. 
You read the observation sequence file into a ObsSequence object, which contains all the 
information about the observation sequence together with a Pandas DataFrame containing the data for 
all the observations in the sequence.

.. code-block:: python

    obs_seq = obsq.ObsSequence('obs_seq.final')

You can then examine, change, and visualize the observation sequence data, 
and write out new observation sequence files.  In this example our observation sequence file
``obs_seq.final`` has been read into ``obs_seq``.

``obs_seq`` is the ObsSequence object.

``obs_seq.df`` is the DataFrame containing all the observations.

There are various modules in PyDARTdiags that are used to work with obs_sequence objects:

- :mod:`obs_sequence` - contains the ObsSequence class, which is used to read and write observation sequence files.
- :mod:`stats` - contains functions to calculate statistics on the observation sequence data.
- :mod:`matplots` - contains functions to plot the observation sequence data using 
  `Matplotlib <https://matplotlib.org/>`_, to produce similar output to the DART 
  `Matlab diagnostics <https://docs.dart.ucar.edu/en/latest/guide/matlab-observation-space.html>`_ .
- :mod:`plots` - contains functions to plot the observation sequence data using 
  `Plotly <https://plotly.com/>`_ to produce interactive plots

In addition, you can edit the observation sequence data directly using the Pandas DataFrame methods.
You can use the Pandas DataFrame methods to filter, group, and aggregate the observation sequence data.
For example, you can filter the observation sequence data to only include observations of a certain type, 
or filter by region by masking out lon-lat, or time period, or remove columns that you do not need.
There are examples of editing observation sequences in the :ref:`manip-examples-index` gallery.

To write your modified observation sequence data back to a file, you can use the
:func:`obs_sequence.ObsSequence.write_obs_seq` method:

.. code-block:: python

    obs_seq.write_obs_seq('modified_obs_seq.out')

The write_obs_seq method will update the attributes of the ObsSequence object. It updates the header 
with the number of observations, converts coordinates back to radians if necessary, 
sorts the DataFrame by time, and generates a linked list pattern for reading by DART programs.

.. Important::

    pyDARTdiags sorts by time and then creates a linked list pattern for reading by DART programs.
    The linked list is not used by pyDARTdiags, but is required for DART programs to read the observation sequence file.
    Do not edit the linked list column in the DataFrame as it will be overwritten when you call
    :func:`obs_sequence.ObsSequence.write_obs_seq` or :func:`obs_sequence.ObsSequence.update_attributes_from_df`

You may want to synchronize the ObsSequence attributes with the DataFrame after making changes to the DataFrame.
without calling write_obs_seq. You can do this by calling the :func:`obs_sequence.ObsSequence.update_attributes_from_df` method:

.. code-block:: python

    obs_seq.update_attributes_from_df()


Calculating Statistics
=======================

The :mod:`stats` module contains functions to calculate statistics on the given DataFrame.

.. Note::

    Note statistics calculations only apply to data from obs_seq.final files, as they 
    require assimilation information from DART

:func:`stats.diag_stats` modifies the DataFrame in place by adding the following columns:

- 'prior_sq_err' and 'posterior_sq_err': The square error for the 'prior' and 'posterior' phases.
- 'prior_bias' and 'posterior_bias': The bias for the 'prior' and 'posterior' phases.
- 'prior_totalvar' and 'posterior_totalvar': The total variance for the 'prior' and 'posterior' phases.


You may be interested in the statistics at various vertical levels. The :mod:`stats` module function
:func:`stats.bin_by_layer` will add two additional columns for the binned vertical levels and 
their midpoints:

- 'vlevels': The categorized vertical levels. [bottom, top]
- 'midpoint': The midpoint of each vertical level bin.

Similarly, you may want to bin the observations by time. The :mod:`stats` module function
:func:`stats.bin_by_time` will add two additional columns for the binned time and
their midpoints: 

- 'time_bin': The categorized time bins. [start, end]
- 'time_bin_midpoint': The midpoint of each time bin.

A detailed description of the statistics calculated by pyDARTdiags can be found in the
:ref:`statistics` section of the user guide.

Diagnostic plots
================

The module :mod:`matplots` contains functions to plot the observation sequence data using
`Matplotlib <https://matplotlib.org/>`_. These functions produce plots similar to the
DART `Matlab diagnostics <https://docs.dart.ucar.edu/en/latest/guide/matlab-observation-space.html>`_,
that is, time evolution and profiles of the statistics for a given observation type, 
and rank histograms for a given observation type. The :ref:`diag-examples-index` Gallery shows examples of how to use
these functions.

Diagnostics plots require assimilation information from DART, so they only work with obs_seq.final files.
For more general examples of visualization of observation sequences, see the the :ref:`vis-examples-index` Gallery.
