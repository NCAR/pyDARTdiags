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


Observation sequence files have a header, followed by a linked list of observations ordered in time.
Here is an example of the header of an observation sequence file, an obs_seq.out the 
World Ocean Database (WOD) observations:

.. raw:: html

   <pre style="background-color: #f8f8f8; color: #000000;"><code>
      obs_sequence
    obs_kind_definitions
              <span style="color: red;">13</span>
              15 FLOAT_SALINITY                 
              16 FLOAT_TEMPERATURE              
              23 GLIDER_SALINITY                
              24 GLIDER_TEMPERATURE             
              27 MOORING_SALINITY               
              28 MOORING_TEMPERATURE            
              32 CTD_SALINITY                   
              33 CTD_TEMPERATURE                
              38 XCTD_SALINITY                  
              39 XCTD_TEMPERATURE               
              43 XBT_TEMPERATURE                
              46 APB_SALINITY                   
              47 APB_TEMPERATURE                
      num_copies:            1  num_qc:            1
      num_obs:        48982  max_num_obs:        48982
    <span style="color: blue;">WOD observation</span>                                                 
    <span style="color: green;">WOD QC</span>                                                          
      first:            1  last:        48982
    </code></pre>

The header starts with the keyword `obs_sequence`, then the keyword `obs_kind_definitions`
then on the next line, a number indicating the number of different types (kinds) of 
observations in the file. In this header there are  :color:`red:13` observation types (kinds) defined. 
The list of observation type follows, each observation type is defined by a unique integer.

.. Note::

   The type integers are only unique within the file, not across files. The parameter, e.g.
   "FLOAT_SALINITY" is what is used internally in DART to refer to this observation type. 


After the list of observation types, there are the number of copies `num_copies`, 
number of quality control copies `num_qc`, number of observations `num_obs`, and maximum 
number of observations, `max_num_obs`.

The names of the copies are listed one per line, the copies followed by the qc copies.
The order of these copies is the same for each observation. In this example, there is one copy 
:color:`blue:WOD observation` and one quality control copy, :color:`green:WOD QC`.
Every observation in the sequence has each of the copies and each of the quality control copies.

The last line of the header contains the first and last observation numbers. This is used to 
indicate the start and end of the linked list of observations in the file. In this example,
the first observation is OBS 1 and the last observation is OBS 48982. Note that because the sequence
is a linked list the order of observations in the file is not not necessarily the same as the order of the 
observations in time.

Here is the format of the observation sequence file after the header, showing the first two observations:

.. raw:: html

   <pre style="background-color: #f8f8f8; color: #000000;"><code>
    OBS            1
      <span style="color: blue;">26.0720005035400</span>    
      <span style="color: green;">0.000000000000000E+000</span> 
              -1           2          -1
    obdef
    loc3d
        3.692663001096695        0.2111673857993198         0.000000000000000      3
    kind
              16
    <span style="color: orange;">43560     151935</span>
      0.250000000000000    
    OBS            2
      <span style="color: blue;">3.379800033569336E-002</span> 
      0.000000000000000E+000
              1           3          -1
    obdef
    loc3d
        3.692663001096695        0.2111673857993198         0.000000000000000      3
    kind
              15
    <span style="color: orange;">43560     151935</span>
      2.500000000000000E-007
   </code></pre>


Each observation in the sequence starts with the keyword `OBS`, followed by the observation number
on the same line.  The copies for each observation are listed on the next lines, following 
the pattern of the header. In this example, the first copy is the 
:color:`blue:WOD observation` and second copy is :color:`green:WOD QC`.  The line after the copies
is the linked list information, which contains the previous observation number,
the next observation number, a third number (-1) which is reserved for use in DART.

The keyword `obdef` indicates the start of the observation definition. This is where any 
additional metadata for the observation is stored, for example a satellite observations may have
channel, platform, and sensor information. In this example, the observation definition is empty.

The keyword `loc3d` indicates the start of the 3D location of the observation, which is followed by
the observation's longitude, latitude in radians, and the vertical value and vertical coordinate 
(e.g. meters, pressure). The keyword `kind` indicates the type of observation, which is an integer that corresponds to the
observation kind defined in the header.  In this example, observation number 1 is a 16, which is 
a FLOAT_TEMPERATURE observation, and observation number 2 is 15 which is a FLOAT_SALINITY observation.

The next line is observation time in :color:`orange: seconds`, :color:`orange: days` since a reference time (usually 1601 01 01 00:00:00 for DART),
the last line of the observation is the observation error variance.


Working with Observation Sequence Objects
=========================================

PyDARTdiags enables you to interact with DART observation sequence files
using Python and `Pandas <https://pandas.pydata.org/>`_ - the Python Data Analysis Library. 
You read the observation sequence file into a ObsSequence object, which contains all the 
information about the observation sequence together with a Pandas DataFrame containing the data for 
all the observations in the sequence.

.. code-block:: python

    import pydartdiags.obs_sequence.obs_sequence as obsq
    obs_seq = obsq.ObsSequence('obs_seq.final')

You can then examine, change, and visualize the observation sequence data, 
and write out new observation sequence files.  In this example our observation sequence file
``obs_seq.final`` has been read into ``obs_seq``.

``obs_seq`` is the ObsSequence object.

You can think of the ObsSequence object a container for the observation sequence,
which includes the header information and the observation data. The ObsSequence object has attributes
that correspond to the header information, such as the number of observations, the observation types,
and the observation copies. You can access these attributes using the dot notation, for example:

.. code-block:: python

    print(obs_seq.copie_names) # print the names of the observation copies
   
For the example above, gives:

.. code-block:: text

    ['WOD observation', 'WOD QC']


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

You may want to synchronize the ObsSequence attributes with the DataFrame after making changes to the DataFrame
without calling write_obs_seq. You can do this by calling the :func:`obs_sequence.ObsSequence.update_attributes_from_df` method:

.. code-block:: python

    obs_seq.update_attributes_from_df()

A Note on Identity Observations
---------------------------------

Identity observations are a special type of observation, where the location and value of the observation is the 
identical to the state. They are used to sample the model state directly, essentially creating "observations" 
that are exact copies of certain state variables. Identity observations do not get listed in the header of 
the observation sequence file, they are denoted in a given observation by a type (kind) of -x where x is 
the index in the DART state vector that the observation corresponds to.

In the ObsSequence DataFrame, the type of identity observations is stored as this negative 
integer of the index in the DART state vector.


Multi-component Observations
------------------------------

:ref:`stats-multi-comp` are a observations constructed from component observation.
For example, U and V wind components can be combined into a single observation of horizontal wind speed.

You can create composite observations in your workflow as follows:

.. code-block:: python

    import pydartdiags.obs_sequence.obs_sequence as obsq
    obs_seq = obsq.ObsSequence('obs_seq.final')
    obs_seq.composite_types()

The default list of composite observation types is defined in 
`composite_types.yaml <https://github.com/NCAR/pyDARTdiags/blob/main/src/pydartdiags/obs_sequence/composite_types.yaml>`__
file. You can give a custom list of composite observation types by passing the path to a YAML file
to the `composite_types` method:  

.. code-block:: python

    obs_seq.composite_types(composite_types='my_composite_types.yaml')

.. Important::

    By default, duplicate composite observations treated as distinct observations
    because this is the behavior of the Fortran obs_diag code, which does not look 
    for nor identify duplicate observations. You can raise an exception if duplicate
    composite observations are found by passing the `raise_on_duplicate` argument: 

    .. code-block:: python

        obs_seq.composite_types(raise_on_duplicate=True)

    This will raise an exception if duplicate composite observations are found in the observation sequence.

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
