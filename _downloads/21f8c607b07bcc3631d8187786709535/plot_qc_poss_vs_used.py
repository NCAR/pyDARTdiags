"""
Possible vs. Used Observations
===============================

This example demonstrates how to read and observation sequence
file, and view the number of used versus possible observations
by type.

"""


###########################################
# Import the obs_sequence module
import pydartdiags.obs_sequence.obs_sequence as obsq
from pydartdiags.data import get_example_data

###########################################
# Chose an obs_seq file to read.
# This is a small obs_seq file "obs_seq.final.ascii.small".
data_file = get_example_data("obs_seq.final.ascii.small")

###########################################
# read the obs_seq file into an obs_seq object
obs_seq = obsq.ObsSequence(data_file)


###########################################
# Examine the dataframe
obs_seq.df.head()

###########################################
# Find number of used versus possible observations

obs_seq.possible_vs_used()