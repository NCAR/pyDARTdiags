.. _dartworkflow:

===========================
Using pyDARTdiags with DART
===========================

This page will introduce you to the Data Assimilation Research Testbed (DART) workflow
and demonstrate how to use pyDARTdiags to enhance your data assimilation projects.

This page will give you basic instructions to create an observation sequence file with DART,
use pyDARTdiags to perform some basic manipulations on the observation sequence, and set up
and run data assimilation with DART using the Lorenz 63 model, which is a simple ODE model
with only three variables. You will then analyze the results with pyDARTdiags and observe how
the changes made to the observation sequence affected the data assimilation outcome.

This guide will go through the following steps:

* Download DART
* Set up a DART experiment with the Lorenz 63 model
* Create an observation sequence file to be used in the assimilation
* Run the assimilation with the original observation sequence
* Modify the observation sequence using pyDARTdiags by changing the observation error variances
* Run the assimilation with the modified observation sequence
* Analyze and compare the results with pyDARTdiags

The instructions on this page are a condensed version from what can be found in the
`DART documentation <https://docs.dart.ucar.edu/en/latest/index.html>`__. The DART documentation
also provides complete tutorials and comprehensive information on ensemble data assimilation,
how DART works, and how to use DART with various models and configurations.


Downloading DART
----------------

Checkout the latest release of DART:

.. code:: 

   git clone https://github.com/NCAR/DART.git

If you have forked the DART repository, replace ``NCAR`` with your Github username.

See the `Downloading DART <https://docs.dart.ucar.edu/en/latest/guide/downloading-dart.html>`__
documentation page for more information.


Compiling DART
--------------

To build the DART executables for Lorenz 63, follow the steps detailed in the
`Compiling DART <https://docs.dart.ucar.edu/en/latest/guide/compiling-dart.html>`__
documentation page.

When you have completed this process, the DART executables will have been built
in the ``DART/models/lorenz_63/work`` directory.
If the build is successful, you will see seven executable programs
in your lorenz_63 work directory. You can find descriptions of each program
at the bottom of the Compiling DART documentation page linked above.


Creating an Observation Sequence File
-------------------------------------

To create an observation sequence file for the Lorenz 63 model, follow the instructions on
the `Creating an obs_seq file of synthetic observations <https://docs.dart.ucar.edu/en/latest/guide/creating-obs-seq-synthetic.html>`__
DART documentation page. This page will guide you through the process of generating an observation
sequence with synthetic observations for the Lorenz 63 model using DART Fortran programs.

The resulting observation sequence will be found in the ``DART/models/lorenz_63/work`` directory.
If you use the default value for the output file name (provided in the DART documentation), the
resulting observation sequence file will be named ``obs_seq.out``.


Running DART data assimilation with the Lorenz 63 Model
-------------------------------------------------------

To perform the actual data assimilation with DART, you will run the ``filter`` program.

The filter section of the default Lorenz 63 ``input.nml`` namelist, which is included in
the DART repository and located in the ``DART/models/lorenz_63/work``, will already have all the
necessary namelist parameters correctly set for this assimilation experiment.

However, if you used a name other than the default (obs_seq.out) when creating the observation
sequence file in the previous step, you will need take the following steps to edit the ``input.nml``
namelist file by changing the ``obs_sequence_in_name`` parameter in the filter namelist:

Open the ``DART/models/lorenz_63/work/input.nml`` file in a text editor. Locate the filter
section of the namelist and edit the ``obs_sequence_in_name`` parameter. Set it to the path
of the new observation sequence file you created. See the example below.
.. code-block:: fortran

    &filter_nml
       ...
       obs_sequence_in_name = 'obs_seq_with_non_default_name.out',
       ...
    /

Save the changes to the ``input.nml`` file.

From the same ``DART/models/lorenz_63/work`` directory, run one of the following commands:

``./filter``  (for non-MPI version)

``mpirun -n 4 ./filter``  (for MPI version with 4 processes)

For more information, you can refer to the
`Running the filter <https://docs.dart.ucar.edu/en/latest/guide/da-in-dart-with-lorenz-63.html#running-the-filter>`__
section of "Data assimilation in DART using the Lorenz 63 model" documentation page.


Manipulating Observation Sequences with pyDARTdiags
---------------------------------------------------

pyDARTdiags can be used to manipulate the observation sequence files used by DART. 

Once pyDARTdiags has ingested an observation sequence file, you can easily modify
various aspects of the observations using Pandas DataFrame methods. You can
filter, group, and aggregate the observation sequence data. For example, you
can filter the observation sequence data to only include observations of a
certain type, or filter by region by masking out lon-lat, or time period, or
remove columns that you do not need. You can also read in two observation
sequences and join them together, remove observations from an observation
sequence, or modify observation values or errors.

You can see examples of various ways to edit observation sequences in the
:ref:`Manipulating Observation Sequences Gallery <sphx_glr_examples_01_manipulating>`.

This section will guide you through the process of writing your own Python program thats uses
pyDARTdiags functions to read in the observation sequence file, modify the
observation error variances, and write out a new observation sequence file with the altered data.

First, ensure you have pyDARTdiags installed in your Python environment. If you haven't
installed it yet, follow the instructions in the :ref:`installguide`.

Create a new python file and open it in a text editor. Name the file
``change_error_variance.py``.

Add the following blocks of code to the file. You can copy and paste the code below, making
sure to adjust the path to your observation sequence file and file name as needed:

#. Import the necessary modules.
    .. code-block:: python

        import pydartdiags.obs_sequence.obs_sequence as obsq

#. Specify the path to and name of your observation sequence file.
    .. code-block:: python

        file_name = "/path_to_your_obs_sequence_file/name_of_your_obs_sequence_file"

#. Read the obs_seq file into an obs_seq object.
    .. code-block:: python

        obs_seq = obsq.ObsSequence(file_name)

#. Halve the observation error variances.
    .. code-block:: python

        obs_seq.df['error_variance'] = obs_seq.df['error_variance'] / 2.0

#. Write out the modified observation sequence to a new file.
    .. code-block:: python

        output_file = file_name + ".half_error_variance"
        obs_seq.write_obs_sequence(output_file)

        ########################## End of script ##############################

Save your Python script and run it.
.. code-block:: bash

    python3 plot_change_error_variance.py

This will create a new observation sequence file with the modified error variances in your
current directory. The new file will have be the name of the observation sequence file you
specified with ``.half_error_variance`` appended to the end.


Running DART data assimilation with the Updated Observation Sequence
--------------------------------------------------------------------

Now that you have created a new observation sequence file with modified error variances,
you can use this file to run a new DART data assimilation experiment with the Lorenz
63 model.

To perform the data assimilation with the updated observation sequence file, you will
need to modify the ``input.nml`` namelist file to use the new input observation sequence
file you just created. You will also need to specify a different output observation sequence
file name for the to avoid overwriting the previous assimilation results.

Open the ``DART/models/lorenz_63/work/input.nml`` file in a text editor. Locate the filter
section of the namelist and edit the ``obs_sequence_in_name`` and ``obs_sequence_out_name``
parameters. Set ``obs_sequence_in_name`` to the new observation sequence file you created
with pyDARTdiags and set ``obs_sequence_out_name`` to an analogous output file name. See
the example below.
.. code-block:: fortran

    &filter_nml
      ...
      obs_sequence_in_name = 'obs_seq.out.half_error_variance',
      obs_sequence_out_name = 'obs_seq.final.half_error_variance',
      ...
    /

Save the changes to the ``input.nml`` file.

Run the filter program again with the updated observation sequence:

``./filter``  (for non-MPI version)

``mpirun -n 4 ./filter`` (for MPI version with 4 processes)


Analyzing DART Results with pyDARTdiags
---------------------------------------

You have now completed two DART data assimilation experiments, each producing an
final observation sequence file, or ``obs_seq.final``. This file contains the actual
observations as assimilated as well as the ensemble forward-operator expected values
and any quality-control values.

You can now use the pyDARTdiags library to easily read in and analyze the observation
space results of your DART assimilation experiment. This will be done plotting the rank
histograms of the assimilation results.

pyDARTdiags includes a program to do this titled ``plot_rank_histogram.py``. To run this
program with the final observation sequence files from your Lorenz 63 assimilation experiments,
follow the instructions listed below:

#. Navigate to the directory ``pyDARTdiags/examples/03_diagnostics/``.
#. Open the ``plot_rank_histogram.py`` script in a text editor.
#. Read through the script to learn how to use pyDARTdiags to read in observation sequences,
   investigate them, and perform diagnostic plotting.
#. Locate the section of the code where the observation sequence file is specified as is shown
   in the code below.
   .. code-block:: python

       obs_seq = obsq.ObsSequence("obs_seq.final.ascii.medium")

   Modify the file name in the ``ObsSequence`` constructor to point to the final observation sequence
   file created by your first DART assimilation experiment (the one you originally created). For
   example, if your final observation sequence file is named ``obs_seq.final``, you would change the
   line to what is shown below.
   .. code-block:: python

       obs_seq = obsq.ObsSequence("obs_seq.final")

#. Locate the section where the observation type is specified, as shown below.
   .. code-block:: python

       obs_type = 'RAW_STATE_VARIABLE'

   Change the obs_type to 'RAW_STATE_VARIABLE'.

#. Save the changes to the script.
#. Run the modified script using Python.
   .. code-block:: bash

       python3 plot_rank_histogram.py

   This will generate and display the rank histogram for the specified observation type
   from your first DART assimilation experiment.
#. Save the rank histogram plot. 
#. Repeat steps 4-8, but this time modify the script to point to the final observation
   sequence file created by your second DART assimilation experiment (the one with the modified
   observation error variances). The obs_type will remain ``RAW_STATE_VARIABLE``. For example,
   if your final observation sequence file is named ``obs_seq.final.half_error_variance``, you
   would change the line to what is shown below.
   .. code-block:: python

       obs_seq = obsq.ObsSequence("obs_seq.final.half_error_variance")

#. Save the changes to the script.
#. Run the modified script using Python.
   .. code-block:: bash

       python3 plot_rank_histogram.py

   This will generate and display the rank histogram for the specified observation type
   from your second DART assimilation experiment where the input observation sequence had the 
   observation error variance halved.

#. Save the rank histogram plot.

You can now compare the two rank histogram plots to see how the change in observation error
variances affected the results of your data assimilation experiments. Look for differences
in the shape of the histograms, which supply information on the model bias.

The rank histogram for the initial experiment should be generally flatter and more evenly spread
across the ranks, indicating a more reliable forecast (the observed distribution is well represented
by the ensemble and all ensemble members represent equally likely scenarios).

By following this workflow, you have learned how pyDARTdiags can be easily integrated into your
DART data assimilation experiments, allowing you to effectively manipulate observation sequences
and analyze assimilation results. Please refer to the :ref:`userguide` and
:ref:`examples-index` sections of the documentation for more detailed information and additional
examples of using pyDARTdiags.