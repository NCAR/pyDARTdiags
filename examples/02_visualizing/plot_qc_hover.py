"""
Geographic Plot of Observations to look at QC
==============================================

This example demonstrates how to read an observation sequence
file and plot the observations on a map, with the color
indicating the QC value.


"""



###########################################
# Import the modules
import os
import plotly.express as px
import pydartdiags.obs_sequence.obs_sequence as obsq

# sphinx_gallery_thumbnail_path = '_static/geo_thumb.png'


###########################################
# Read the obs_seq file into an obs_seq object.
# In this example, we use a small obs_seq file "obs_seq.final.ascii.medium"
# that comes with the pyDARTdiags package 
# in the data directory, so we use ``os`` to get the path to the file
data_dir = os.path.join(os.getcwd(), "../..", "data")
data_file = os.path.join(data_dir, "obs_seq.final.ascii.medium")

obs_seq = obsq.obs_sequence(data_file)


###########################################
# Take a look at which columns are in the dataframe
obs_seq.df.columns

###########################################
# Plot the observations on a map.
# In this case, the colors of the points
# will indicate the DART quality control value
# and the hover data will show the observation number,
# the observation value, the type of observation, and the QC value

fig = px.scatter_geo(
    obs_seq.df,
    lat='latitude',
    lon='longitude',
    color='DART_quality_control',
    hover_data={'DART_quality_control':True,
                'type': True,
                'observation': True,
                'obs_num': True
    },
    title='Geographic Plot of Latitude and Longitude'
)

fig.update_layout(
    width=950,  # Set the width of the plot
)
fig
