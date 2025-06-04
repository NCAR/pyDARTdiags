"""
Plot Profiles
=============

This example demonstrates how to plot profiles of 
RMSE, bias, and totalspread. For an explanation of the statistics calculations see
the :ref:`statistics` guide.
"""

###########################################
# Import the obs_sequence module
# and the matplots module for plotting.
import pydartdiags.obs_sequence.obs_sequence as obsq
from pydartdiags.matplots import matplots as mp

###########################################
# Chose an obs_seq file to read.
# In this example, we are using a small obs_seq file "obs_seq.final.1000"
# that comes with the pyDARTdiags package 
# in the data directory, so we ``import os`` to get the path to the file.
import os
data_dir = os.path.join(os.getcwd(), "../..", "data")
data_file = os.path.join(data_dir, "obs_seq.final.1000")

###########################################
# Read the obs_seq file into an obs_seq object.
obs_seq = obsq.ObsSequence(data_file)

###########################################
# Chose an observation type.
# The observation types are stored in the 'type' column.
# To see which observation types are in the dataframe, use the unique method:
obs_seq.df['type'].unique()

###########################################
# For this example, we are going to look at the profile for 
# ACARS_TEMPERATURE observations.
type = 'ACARS_TEMPERATURE'
hPalevels = [0.0, 100.0,  150.0, 200.0, 250.0, 300.0, 400.0, 500.0, 700, 850, 925, 1000]  # hPa
levels = [i * 100 for i in hPalevels]

fig = mp.plot_profile(obs_seq, levels, type, bias=True, rmse=True, totalspread=True)

###########################################
# To plot only the bias, set rmse=False and totalspread=False.
fig = mp.plot_profile(obs_seq, levels, type, bias=True, rmse=False, totalspread=False)