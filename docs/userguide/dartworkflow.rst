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
the changes made to the observation sequence effected the data assimilation outcome.

This guide will go through the following steps:

* Set up a DART experiment with the Lorenz 63 model
* Create an observation sequence file to be used in the assimilation
* Run the assimilation with the original observation sequence
* Modify the observation sequence using pyDARTdiags by changing the observation error variances
* Run the assimilation with the modified observation sequence
* Analyze and compare the results with pyDARTdiags

The instructions on this page are a condensed version from what can be found in the `DART documentation <https://dart.ucar.edu/documentation/>`__.
Specifically, the DART documentation contains:

* Instructions to download DART: `Downloading DART <https://docs.dart.ucar.edu/en/latest/guide/downloading-dart.html>`__.
* Instructions to compile DART: `Compiling DART <https://docs.dart.ucar.edu/en/latest/guide/compiling-dart.html>`__.
* A full guide to generating DART observation files and performing DART data assimilation with the Lorenz 63 model: `Using DART with the Lorenz 63 Model <https://dart.ucar.edu/documentation/using-dart-with-the-lorenz-63-model/>`__.
* A detailed description of the Lorenz 63 model and its relevance to data assimilation: `Lorenz 63 Model <https://dart.ucar.edu/documentation/models/lorenz-63-model/>`__.

The DART documentation also provides complete tutorials and comprehensive information on data
assimilation and setting up and running DART experiments DART with various models and configurations,
including complete tutorials.


Downloading DART
----------------

Checkout the latest release of DART:

.. code:: 

   git clone https://github.com/NCAR/DART.git

If you have forked the DART repository, replace ``NCAR`` with your Github username.


Compiling DART
--------------

To build DART executables you will need to:

#. Create an mkmf.template with appropriate compiler and library flags.

   mkmf.templates for different compilers/architectures can be found
   in the ``DART/build_templates`` directory and have names with
   extensions that identify the compiler, the architecture, or both. This
   is how you inform the build process of the specifics of your system.

   Copy the template that is most similar to your system into ``DART/build_templates/mkmf.template``.
   
   Then open ``DART/build_templates/mkmf.template`` and customize it as needed by
   editing the lines of code shown in the following example. 
   
   This example uses the template ``DART/build_templates/mkmf.template.intel.linux``.
   Note that only the relevant lines of the file are shown here. The
   first portion of the file is a large comment block that provides
   further advice on how to customize the *mkmf* template file if needed.

   .. code-block:: text
   
        MPIFC = mpif90
        MPILD = mpif90
        FC = ifort
        LD = ifort
        NETCDF = /usr/local
        INCS = -I$(NETCDF)/include
        LIBS = -L$(NETCDF)/lib -lnetcdf -lnetcdff
        FFLAGS = -O2 $(INCS)
        LDFLAGS = $(FFLAGS) $(LIBS)


+---------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| FC      | the Fortran compiler                                                                                                                                                                                                             |
+=========+==================================================================================================================================================================================================================================+
| LD      | the name of the loader; typically, the same as the Fortran compiler                                                                                                                                                              |
+---------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| MPIFC   | the MPI Fortran compiler; see the :doc:`DART MPI introduction <mpi_intro>` for more info                                                                                                                                         |
+---------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| MPILD   | the MPI loader; see the :doc:`DART MPI introduction <mpi_intro>` for more info                                                                                                                                                   |
+---------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| NETCDF  | the location of your root netCDF installation, which is assumed to contain netcdf.mod and typesizes.mod in the include subdirectory. Note that the value of the NETCDF variable will be used by the “INCS” and “LIBS” variables. |
+---------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| INCS    | the includes passed to the compiler during compilation. Note you may need to change this if your netCDF includes netcdf.mod and typesizes.mod are not in the standard location under the include subdirectory of NETCDF.         |
+---------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| LIBS    | the libraries passed to “FC” (or “MPIFC”) during compilation. Note you may need to change this if the netCDF libraries libnetcdf and libnetcdff are not in the standard location under the “lib” subdirectory of NETCDF.         |
+---------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| FFLAGS  | the Fortran flags passed to “FC” (or “MPIFC”) during compilation. There are often flags used for optimized code versus debugging code. See your particular compiler’s documentation for more information.                        |
+---------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| LDFLAGS | the linker flags passed to LD during compilation. See your particular linker’s documentation for more information.                                                                                                               |
+---------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

#. Choose which model you want to use with DART, and cd into that work directory. 

   For the lorenz_63 model, ``cd DART/models/lorenz_63/work``

#. Build the DART executables with ``./quickbuild.sh``.

   ``./quickbuild.sh nompi`` will build DART without MPI, for those who do not have MPI
   installed or prefer not to use it.

   If you are using gfortran as your Fortran compiler, use ``./quickbuild.sh mpif08``.

The DART executables are built in the ``work`` directory.
If the build is successful, you will see the following seven programs
in your lorenz_63 work directory.

+--------------------------------------------------------------------------------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Program                                                                                                                  | Purpose                                                                                                                                                                                                                                                                                                         |
+==========================================================================================================================+=================================================================================================================================================================================================================================================================================================================+
|`preprocess   <../assimilation_code/programs/preprocess/preprocess.html>`__                                               | creates custom source code for just the observations of interest                                                                                                                                                                                                                                                |
+--------------------------------------------------------------------------------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|`create_obs_sequence <../assimilation_code/programs/create_obs_sequence/create_obs_sequence.html>`__                      | specify a (set) of observation characteristics taken by a particular (set of) instruments                                                                                                                                                                                                                       |
+--------------------------------------------------------------------------------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|`create_fixed_network_seq <../assimilation_code/programs/create_fixed_network_seq/create_fixed_network_seq.html>`__       | specify the temporal attributes of the observation sets                                                                                                                                                                                                                                                         |
+--------------------------------------------------------------------------------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|`perfect_model_obs <../assimilation_code/programs/perfect_model_obs/perfect_model_obs.html>`__                            | spinup and generate “true state” for synthetic observation experiments                                                                                                                                                                                                                                          |
+--------------------------------------------------------------------------------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|`filter <../assimilation_code/programs/filter/filter.html>`__                                                             | perform data assimilation analysis                                                                                                                                                                                                                                                                              |
+--------------------------------------------------------------------------------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|`obs_diag <../assimilation_code/programs/obs_diag/threed_sphere/obs_diag.html>`__                                         | creates observation-space diagnostic files in netCDF format to support visualization and quantification.                                                                                                                                                                                                        |
+--------------------------------------------------------------------------------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|`obs_sequence_tool <../assimilation_code/programs/obs_sequence_tool/obs_sequence_tool.html>`__                            | manipulates observation sequence files. This tool is not generally required (particularly for low-order models) but can be used to combine observation sequences or convert from ASCII to binary or vice-versa. Since this is a rather specialized routine, we will not cover its use further in this document. |
+--------------------------------------------------------------------------------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+


Creating an Observation Sequence File
-------------------------------------


Running DART data assimilation with the Lorenz 63 Model
-------------------------------------------------------

To perform the actual data assimilation with DART, you will run the ``filter`` program.

The ``DART/models/lorenz_63/work/input.nml`` file is the DART namelist for the Lorenz 63 model, which is a
standard Fortran method for passing parameters from a text file into a program without
needing to recompile. There are many sections within this file that drive the behavior
of DART while using the Lorenz 63 model for assimilation.

Note that the filter section of the default Lorenz 63 ``input.nml`` namelist, which is included in
the DART repository and located in the ``DART/models/lorenz_63/work`` will already have all the
necessary namelist parameters correctly set for this assimilation experiment.

From the same ``DART/models/lorenz_63/work`` directory, run one of the following commands:

``./filter``  (for non-MPI version)
``mpirun -n 4 ./filter``  (for MPI version with 4 processes)


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

You can see various examples of editing observation
sequences in the :ref:`Manipulating Observation Sequences Gallery <examples-manipulating-obsq>`.
Manipulating Observation Sequences gallery.

You will follow the Change Observation Error Variance example (LINK HERE). This example will
provide you with a Python progran to to read in the observation sequence file, modify the
observation error variances, and write out a new observation sequence file with the altered data.

First, ensure you have pyDARTdiags installed in your Python environment. If you haven't
installed it yet, follow the instructions in the :ref:`installguide`.

Then, navigate to the directory that contains the example script ``plot_change_error_variance.py``
in the pyDARTdiags repository: ``pyDARTdiags/examples/01_manipulating/``. 

Follow these steps to edit the script to use the observation sequence file you created for the Lorenz 63
data assimilation experiment instead of the sample observation sequence file provided with pyDARTdiags:

#. Copy your observation sequence file created for the Lorenz 63 data assimilation experiment
   into the ``pyDARTdiags/data/`` directory.
#. Open the ``plot_change_error_variance.py`` script in a text editor.
#. Locate the section of the code where the observation sequence file is specified. It should look something like this:

   .. code-block:: python

       import os
        data_dir = os.path.join(os.getcwd(), "../..", "data")
        file_name = "obs_seq.final.ascii.small"
        data_file = os.path.join(data_dir, file_name)

#. Modify the ``file_name`` variable to the name of the observation sequence file you created for the Lorenz 63 data
   assimilation experiment.
   For example, if your observation sequence file is named ``obs_seq.out``, you would change the line to:
   .. code-block:: python
    
         file_name = os.path.join(data_dir, "obs_seq.out")

#. Save the changes to the script.

Now, run the modified script using Python:
.. code-block:: bash

   python3 plot_change_error_variance.py

This will create a new observation sequence file with the modified error variances in the
``pyDARTdiags/examples/01_manipulating/`` directory. The new file will have be the name of
the observation sequence file inputted with the you specified with ``.half_error_variance``
appended to the end.


Running DART data assimilation with the Updated Observation Sequence
--------------------------------------------------------------------

Now that you have created a new observation sequence file with modified error variances,
you can use this file to run a new DART data assimilation experiment with the Lorenz
63 model.

To perform the data assimilation with the updated observation sequence file, you will
need to modify the ``input.nml`` namelist file to point to the new observation sequence
file you just created.

Open the ``DART/models/lorenz_63/work/input.nml`` file in a text editor. Locate the filter
section of the namelist and edit the ``obs_sequence_in_name`` parameter. Set it to the path
of the new observation sequence file you created with pyDARTdiags. For example:
.. code-block:: fortran

    &filter_nml
      ...
      obs_sequence_in_name = 'path/to/your/obs_seq.out.half_error_variance',
      ...
    /

Save the changes to the ``input.nml`` file.


Analyzing DART Results with pyDARTdiags
---------------------------------------

You will now use the pyDARTdiags library to analyze the observation space results of your DART
assimilation experiment.

This will be done investigating the rank histograms of the assimilation results by following the
Rank Histogram Example (LINK HERE). This example will provide you with a Python program to read in
the output observation sequence files created by DART during the assimilation, and plot rank histograms
located in the :ref:`Observation Space Diagnostics Gallery <examples-obs-diags>`.