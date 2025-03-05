"""
Adding External Forward Operators to an Observation
===================================================

External, or "precomputed" forward operators are forward operators
that are not calculated during ``filter``, DART's assimilation program. 
They are calculated externally, written to an observation sequence file,
and read in by ``filter``.  

This example shows how to add an external forward operator to an observation.
We'll be using observations for the Lorenz 96 tracer model, which is a toy
model used to test assimilation algorithms.  We are going to create some 
RAW_TRACER_CONCENTRATION forward operators.

"""

###########################################
# Import the obs_sequence module, and numpy
import os
import pydartdiags.obs_sequence.obs_sequence as obsq
import numpy as np

###########################################
# Read in the observation sequence file. In this example we'll use the
# obs_seq.out.tracer file that comes with the pyDARTdiags package.
# This file only has two observations. 
data_dir = os.path.join(os.getcwd(), "../..", "data")
data_file = os.path.join(data_dir, "obs_seq.out.tracer")
obs_seq = obsq.obs_sequence(data_file)

###########################################
obs_seq.df


###########################################
# The external forward operator is stored in the 'external_FO' column.
# Currently, the 'external_FO' column is empty.
obs_seq.df.iloc[0]['external_FO']


###########################################
# Let's add a forward operator to the RAW_TRACER_CONCENTRATION observation.
# For this example, we're going to use random numbers to create our ensemble
# of forward operators. For a scientific experiment, you would use appropriate 
# forward operator results from your model. 
# We want 80 ensemble members, so we'll create 80 random numbers, and we want tracer
# concentrations, so we'll force the numbers to be positive.
n = 80
random_numbers = np.abs(np.random.normal(loc=0.75, scale=0.1, size=n)).tolist()

###########################################
# DART observation sequence files have a specific format. DART expects the list
# of forward operators to have 'external_FO' followed by the number of ensemble
# members, followed by the 'key' for the forward operator. The 'key' is not 
# used by DART, so we will just put 1 for the value. 
random_numbers.insert(0, f'external_FO {n} 1')

###########################################
# Now we can add the forward operator to the 'external_FO' column for row 0
obs_seq.df.at[0,'external_FO'].extend(random_numbers)

###########################################
# Now the 'external_FO' column has the forward operator.
obs_seq.df.iloc[0]['external_FO']

###########################################
# Let's write the observation sequence file with the new forward operator.
obs_seq.write_obs_seq('obs_seq.out.tracer_with_external_FO')
