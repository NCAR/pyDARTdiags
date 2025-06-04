"""
Grand Statistics
================

This example demonstrates how to compute grand statistics for
an observation sequence. For an explanation of the statistics calculations see
the :ref:`statistics` guide.

"""

###########################################
# Import the obs_sequence module 
# and the statistics module.
import pydartdiags.obs_sequence.obs_sequence as obsq
from pydartdiags.stats import stats
###########################################
# Chose an obs_seq file to read.
# This is a small obs_seq file "obs_seq.final.ascii.medium"
# that comes with the pyDARTdiags package 
# in the data directory, so we ``import os`` to get the path to the file
import os
data_dir = os.path.join(os.getcwd(), "../..", "data")
data_file = os.path.join(data_dir, "obs_seq.final.ascii.medium")


###########################################
# Read the obs_seq file into an obs_seq object.
obs_seq = obsq.ObsSequence(data_file)

# Select observations that were used in the assimilation.
used_obs = obs_seq.select_used_qcs()

###########################################
# `used_obs` is a dataframe with only the observations with QC value of 0.
#
# The columns of the dataframe are the same as the original obs_seq dataframe.
used_obs.columns

###########################################
# Now we calculate the statistics required for DART diagnostics.

stats.diag_stats(used_obs)

###########################################
# The statistics are calculated for each row in the dataframe, 
# and the results are stored in new columns.

used_obs.columns

###########################################
# The help function can be used to find out more about the diag_stats function
# including what statistics are calculated.
help(stats.diag_stats)


###########################################
# Summarize the grand statistics, which are the statistics aggregated over all the observations
# for each type of observation.
stats.grand_statistics(used_obs)
