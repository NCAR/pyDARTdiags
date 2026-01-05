
"""
Change Observation Error Variance
=================================

This example demonstrates how to change the error variance of
observations in an observation sequence and write a new
observation sequence file.

"""

###########################################
# Import the obs_sequence module
import pydartdiags.obs_sequence.obs_sequence as obsq

###########################################
# Chose an obs_seq file to read.
# In this example, we are using a small obs_seq file "obs_seq.final.small"
# that comes with the pyDARTdiags package 
# in the data directory, so we ``import os`` to get the path to the file.
#   
# NOTE that if you are runing this example as a part of the guide to Using
# pyDARTdiags with DART, you will follow the instructions there to modify this bit
# of code instead use the observation sequence file you created for Lorenz 63.

import os
data_dir = os.path.join(os.getcwd(), "../..", "data")
file_name = "obs_seq.final.ascii.small"
data_file = os.path.join(data_dir, file_name)

###########################################
# Read the obs_seq file into an obs_seq object.
obs_seq = obsq.ObsSequence(data_file)

###########################################
# Take a look at the observation sequence.
obs_seq.df.head()

###########################################
# To count of the number of observations by error variance, use the groupby method.
obs_seq.df.groupby('obs_err_var').size()

###########################################
# Let's change the error variance of these observations.
# Set the error variance for each observation to half its original value.
obs_seq.df['obs_err_var'] = obs_seq.df['obs_err_var'] / 2

###########################################
# Now let's check the number of observations by error variance again.
obs_seq.df.groupby('obs_err_var').size()

###########################################
# Write the new observation sequence to a file.
obs_seq.write_obs_seq(file_name + '.half_error_variance')