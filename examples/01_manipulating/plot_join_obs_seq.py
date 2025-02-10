"""
Join Observation Sequences
==============================

This example demonstrates how to read in two observation sequences 
and join them together.

"""

###########################################
# Import the obs_sequence module.
import pydartdiags.obs_sequence.obs_sequence as obsq

###########################################
# Chose the first obs_seq file to read.
# In this example, we are using a small obs_seq file "obs_seq.final.1000"
# that comes with the pyDARTdiags package 
# in the data directory, so we ``import os`` to get the path to the file.
import os
data_dir = os.path.join(os.getcwd(), "../..", "data")
data_file1 = os.path.join(data_dir, "obs_seq.final.1000")

###########################################
# Read the obs_seq file into an obs_seq object.
obs_seq1 = obsq.obs_sequence(data_file1)

print('obs_seq1 has assimilation info:', obs_seq1.has_assimilation_info())
print('obs_seq1 has posterior:', obs_seq1.has_posterior())

###########################################
# Chose the second obs_seq file to read.

data_file2 = os.path.join(data_dir, "obs_seq.final.ascii.small")
obs_seq2 = obsq.obs_sequence(data_file2)

print('obs_seq2 has assimilation info:', obs_seq2.has_assimilation_info())
print('obs_seq2 has posterior:', obs_seq2.has_posterior())

###########################################
# obs_seq1 has posterior information, but obs_seq2 does not.
# So we will remove the posterior columns from obs_seq1 DataFrame, using the pandas
# `drop` method before joining the two obs_seq objects together.

obs_seq1.df.drop(columns=obs_seq1.df.filter(like='posterior').columns, inplace=True)
print('obs_seq1 has posterior:', obs_seq1.has_posterior())

###########################################
# Now, let's join the two obs_seq objects together using the join method.
# :meth:`obs_sequence.obs_sequence.join` is a class method, so it is called
# on the obs_sequence class, which
# we've imported as obsq. The method takes a list of obs_seq objects to join.

obs_seq_mega = obsq.obs_sequence.join([obs_seq1, obs_seq2])

print(f'length of obs_seq1: {len(obs_seq1.df)}'), print(f'length of obs_seq2: {len(obs_seq2.df)}')
print(f'length of obs_seq_mega: {len(obs_seq_mega.df)}')

obs_seq_mega.df.head()

###########################################
# Now, the obs_seq_mega object has the observations from both obs_seq1 and obs_seq2.
# with the prior columns from both obs_seq DataFrames.
obs_seq_mega.df.columns


###########################################
# You can pass a list of columns to the join method to only join the columns you want.
# For example, if you only want to join the 'prior_mean' and 'prior_spread' columns, 
# and discard the rest of the columns from the obs_seq objects,
# you can do so like this:

obs_seq_no_members = obsq.obs_sequence.join([obs_seq1, obs_seq2], 
                                            ['prior_ensemble_mean', 
                                             'prior_ensemble_spread'])

###########################################
# Note, the join method will still include the required columns for the obs_seq object to function properly.
obs_seq_no_members.df.columns

