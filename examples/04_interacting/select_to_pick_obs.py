"""
Select observations to add them to a new obs sequence
=====================================================

This example demonstrates how to read an observation sequence
file, and plot the observations on a map, with the color
indicating the QC value. 

You can then select observations on the map to add them to a
new observation sequence file.

- Choose the lasso or rectangle tool in the graph's menu bar and
then select points in the plot.

- Selection data accumulates if you perform multiple selections,
and the currently selected observations will be shown below the plot.

- When you are finished selecting your desired observations, press the
  submit button to create a new observation sequence file that contains
  only the selected observations. This will be saved in the current
  directory (pyDARTdiags/examples/04_interacting).
"""

# Import packages
from pydartdiags.interactive_plots import interactive_plots as ip
import pandas as pd
import pydartdiags.obs_sequence.obs_sequence as obsq
import os

###########################################
# Read the obs_seq file into an obs_seq object.

# In this example, we use a small obs_seq file "obs_seq.final.ascii.medium"
# that comes with the pyDARTdiags package in the data directory, so we use
# ``os`` to get the path to the file
data_dir = os.path.join(os.getcwd(), "../..", "data")
data_file = os.path.join(data_dir, "obs_seq.final.ascii.medium")
obs_seq = obsq.obs_sequence(data_file)

# We also create a copy of this obs_seq file to be mainuplated
# through map selection
obs_seq_selected = obsq.obs_sequence(data_file)

###########################################
# Examine the dataframe.
obs_seq.df.head()

###########################################
# Create and run the interactive Dash app
# that creates new obs sequence file with
# observations selcted on geogrpahic plot
fig = ip.geo_plot(obs_seq)
app = ip.include_only_selected_obs_dash_app(fig, obs_seq_selected)

# Run the app
if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
