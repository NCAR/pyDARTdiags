"""
Select observations to remove them from the observation sequence
================================================================

This example demonstrates how to read an observation sequence
file and launch a Dash app to plot the observations on a map.

You can then select observations on the map and create a
new observation sequence file that excludes the selected
observations. Further instructions on usage are provided in the
Dash app interface.

.. image:: ../../../docs/images/remove_obs_image.png

The following program select_to_remove_obs.py uses functions
already provided in the pyDARTdiags source code to simplify
the implementation of the Dash app.
"""

###########################################
# Import the obs_sequence and interactive_plots module.
from pydartdiags.interactive_plots import interactive_plots as ip
import pydartdiags.obs_sequence.obs_sequence as obsq

###########################################
# Choose the first obs_seq file to read.
# In this example, we use a small obs_seq file "obs_seq.final.ascii.medium"
# that comes with the pyDARTdiags package in the data directory, so we
# ``import os`` to get the path to the file.
import os
data_dir = os.path.join(os.getcwd(), "../..", "data")
data_file = os.path.join(data_dir, "obs_seq.final.ascii.medium")

###########################################
# Read the obs_seq file into an obs_seq object. Repeat this for a
# second obs_seq object to be manipulated through map selection.
obs_seq = obsq.ObsSequence(data_file)
obs_seq_selected = obsq.ObsSequence(data_file)

###########################################
# Examine the dataframe.
obs_seq.df.head()

###########################################
# Create the interactive Dash app.
fig = ip.geo_plot(obs_seq)
app = ip.exclude_selected_obs_dash_app(fig, obs_seq_selected)

###########################################
# Run the app.
if __name__ == "__main__":
    app.run(debug=True, use_reloader=True)

###########################################
# Launch the Dash app by running the Python program in your terminal
# using the ``python3 select_to_remove_obs.py`` command.
