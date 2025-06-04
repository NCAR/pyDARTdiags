"""
Finding Duplicates in a Observation Sequence
============================================

This example shows how to find duplicates in an observation sequence,
and how to remove them.

"""

###########################################
# Import the obs_sequence module
import os
import pydartdiags.obs_sequence.obs_sequence as obsq

###########################################
# Read in the observation sequence file. In this example we'll use a real obs_seq file,
# the NCEP+ACARS.201303_6H.obs_seq2013030306 file that comes with the pyDARTdiags package.
# This is 6 hours of observations from March 3, 2013.
data_dir = os.path.join(os.getcwd(), "../..", "data")
data_file = os.path.join(data_dir, "NCEP+ACARS.201303_6H.obs_seq2013030306")

obs_seq = obsq.ObsSequence(data_file)

###########################################
# How many observations are in the sequence?
num_obs = len(obs_seq.df)
print(f"Number of observations: {num_obs}")

###########################################
# How many of each type of observation are in the sequence?
obs_seq.df.groupby('type')['type'].count()

###########################################
# How many duplicates are there in the sequence? Lets pick the columns that we want to compare
# to determine if an observation is a duplicate. In this case we'll use latitude, longitude, vertical,
# time, observation, and type. We'll use the 'duplicated' method to find the duplicates.

columns_to_compare = ['latitude', 'longitude', 'vertical', 'time', 'observation', 'type']
num_dups = obs_seq.df.duplicated(subset=columns_to_compare).sum()
print(f"Number of duplicates: {num_dups}")

###########################################
# Lets see how many duplicates there are for each type of observation.
# We'll use the 'duplicated' method to find the duplicates.
for obs_type in sorted(obs_seq.types.values()):
    selected_rows = obs_seq.df[obs_seq.df['type'] == obs_type]
    print(f"duplicates in {obs_type}: ", selected_rows[columns_to_compare].duplicated().sum())

###########################################
# Let's look at the duplicates in the 'LAND_SFC_ALTIMETER' type.
# We're sorting by latitude to make it easier to see the duplicates.

selected_rows = obs_seq.df[obs_seq.df['type'] == 'LAND_SFC_ALTIMETER']
duplicate_mask = selected_rows[columns_to_compare].duplicated(keep=False)
duplicate_rows = selected_rows[duplicate_mask]

duplicate_rows.sort_values(by='latitude')

###########################################
# Lets remove all the duplicates from the dataFrame
obs_seq.df.drop_duplicates(subset=columns_to_compare, inplace=True)

###########################################
# The number of obs has been reduced by the number of duplicates
print(f"Original number of observations: {num_obs}")
print(f"Number of duplicate observations: {num_dups}")
print(f"Number of observations after removing duplicates: {len(obs_seq.df)}")
