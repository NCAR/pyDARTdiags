"""
Remove Observations
===================

This example demonstrates how to remove observations from an
observation sequence and write a new observation sequence file.

"""

###########################################
# Import the obs_sequence module
import pydartdiags.obs_sequence.obs_sequence as obsq

###########################################
# Chose an obs_seq file to read.
# In this example, we are using a small obs_seq file "obs_seq.final.medium"
# that comes with the pyDARTdiags package 
# in the data directory, so we ``import os`` to get the path to the file.
import os
data_dir = os.path.join(os.getcwd(), "../..", "data")
data_file = os.path.join(data_dir, "obs_seq.final.ascii.medium")

###########################################
# Read the obs_seq file into an obs_seq object.
obs_seq = obsq.obs_sequence(data_file)

###########################################
# Take a look at the observation sequence.
obs_seq.df.head()

###########################################
# To count of the number of observations by type, use the groupby method.
obs_seq.df.groupby('type').size()

###########################################
# Let's remove the 'GPSRO_REFRACTIVITY' observations.
# Remove rows where ``'type' == 'GPSRO_REFRACTIVITY'``
obs_seq.df = obs_seq.df[obs_seq.df['type'] != 'GPSRO_REFRACTIVITY']

###########################################
# Now let's check the number of observations by type again.
# For only the 'GPSRO_REFRACTIVITY' observations:
gpsro_count = (obs_seq.df['type'] == 'GPSRO_REFRACTIVITY').sum()
print(f"Number of observations with type 'GPSRO_REFRACTIVITY': {gpsro_count}")

###########################################
# Count the observations by type again. You'll see that the 'GPSRO_REFRACTIVITY' 
# observations have been removed from the dataFrame
obs_seq.df.groupby('type').size()

###########################################
# Write the new observation sequence to a file.
obs_seq.write_obs_seq('obs_seq.final.ascii.medium.no_gpsro')

###########################################
# The new file will not have the 'GPSRO_REFRACTIVITY' observations.