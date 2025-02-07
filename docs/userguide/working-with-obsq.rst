==================================
Working with obs_sequence objects
==================================

DART uses observation sequence files to store observations and their associated
metadata. These files are used as input to the DART assimilation system, and after
assimilation, the observation sequence files are updated with the assimilation data.

The assimilation data is the mean and standard deviation of the forward operator for 
each observation, and optionally each ensemble members value of the forward operator.
The prior assimilation data is always present in the observation sequence file, the
posterior assimilation data is only present if the user choses to do posterior forward
operator calculations.

PyDARTdiags enables you to interact with DART observation sequence files
using Python and `Pandas <https://pandas.pydata.org/>`_ - the Python Data Analysis Library. 
You read the observation sequence file into a obs_seq object, which contains the 
observation sequence data in a Pandas DataFrame.

.. code-block:: python

    obs_seq = obsq.obs_sequence('obs_seq.final')

You can then examine, change, and visualize the observation sequence data, 
and write out new observation sequence files. 

``obs_seq`` is the obs_sequence object.

``obs_seq.df`` is the DataFrame containing all the observations.

There are various modules in PyDARTdiags that are used to work with obs_sequence objects:

- :mod:`obs_sequence` - contains the obs_sequence class, which is used to read and write observation sequence files.
- :mod:`stats` - contains functions to calculate statistics on the observation sequence data.
- :mod:`matplots` - contains functions to plot the observation sequence data using 
  `Matplotlib <https://matplotlib.org/>`_, to produce similar output to the DART 
  `Matlab diagnostics <https://docs.dart.ucar.edu/en/latest/guide/matlab-observation-space.html>`_ .
- :mod:`plots` - contains functions to plot the observation sequence data using 
  `Plotly <https://plotly.com/>`_ to produce interactive plots


Calculating statistics
----------------------

The :mod:`stats` module contains functions to calculate statistics on the given DataFrame.
``stats.diag(obs_seq.df)`` modifies the DataFrame in place by adding the following columns:

- 'prior_sq_err' and 'posterior_sq_err': The square error for the 'prior' and 'posterior' phases.
- 'prior_bias' and 'posterior_bias': The bias for the 'prior' and 'posterior' phases.
- 'prior_totalvar' and 'posterior_totalvar': The total variance for the 'prior' and 'posterior' phases.


You may be interested in the statistics at various vertical levels. The :mod:`stats` module function
``bin_by_layer(obs_seq.df, levels)`` will add two additional columns for the binned vertical levels and 
their midpoints:

- 'vlevels': The categorized vertical levels. [bottom, top]
- 'midpoint': The midpoint of each vertical level bin.


