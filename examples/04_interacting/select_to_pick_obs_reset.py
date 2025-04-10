"""
Select Observations in Geographic Plot
======================================

This example demonstrates how to read and observation sequence
file, and plot the observations on a map, with the color
indicating the QC value. You can then select observations on
the map with the lasso or rectangle select features in the
item bar. 
"""

# Import packages
from dash import Dash, dcc, html, Input, Output, callback
import pandas as pd
import plotly.express as px
import json
import pydartdiags.obs_sequence.obs_sequence as obsq
import os
#from pydartdiags.interactive_plots import interactive_plots as ip

###########################################
# Read the obs_seq file into an obs_seq object.
# In this example, we use a small obs_seq file "obs_seq.final.ascii.medium"
# that comes with the pyDARTdiags package 
# in the data directory, so we use ``os`` to get the path to the file
data_dir = os.path.join(os.getcwd(), "../..", "data")
#data_file = os.path.join(data_dir, "obs_seq2006010106")
data_file = os.path.join(data_dir, "NCEP+ACARS.201303_6H.obs_seq2013030306_10000")
#data_file = os.path.join(data_dir, "obs_seq.final.ascii.medium")

obs_seq = obsq.obs_sequence(data_file)
obs_seq_selected = obsq.obs_sequence(data_file)

###########################################
# Take a look at which columns are in the dataframe
#obs_seq.df.columns

###########################################
# Plot the observations on a map.

# In this case, the colors of the points will indicate
# the DART quality control value and the hover data
# will show the observation number, the observation
# value, the type of observation, and the QC value

styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll',
        'color': 'black'
    },
    'txt': {
        'color': 'black'
    }
}

fig = px.scatter_geo(
    obs_seq.df,
    lat='latitude',
    lon='longitude',
#    color='DART_quality_control',
#    hover_data={'DART_quality_control':True,
    color='NCEP_QC_index',
    hover_data={'NCEP_QC_index':True,
                'type': True,
                'observation': True,
                'obs_num': True
    },
    width=1400,
    height=850,
#    modeBarButtonsToAdd: ['eraseshape']
)

fig.update_layout(clickmode='event+select')

#Initialize the Dash app
app = Dash()

# App layout
app.layout = [
    dcc.Markdown("""
        ## **Select observations to add them to a new obs sequence**

        Choose the lasso or rectangle tool in the graph's menu
        bar and then select points in the plot.

        Selection data accumulates if you perform multiple selections,
        and the currently selected observations will be shown below
        the plot.

        When you are finished selecting the desired observation, press
        the select button to create a new observation sequence file
        that contains only the selected observations.
    """, style=styles['txt']),
    
    dcc.Graph(id='select-obs', figure=fig),

    html.Button('Submit', id='submit', n_clicks=0),

    html.Pre(id='confirmation', style=styles['pre']),

    html.Button('Reset', id='reset_button'),

    html.Pre(id='reset-confirmation', style=styles['pre']),

    html.Pre(id='selected-data', style=styles['pre']),

    dcc.Store(id="store"),

    dcc.Store(id="do-reset", data=False)
]

customdata_list = []
unique_obs_types = []

@callback(
    Output('selected-data', 'children', allow_duplicate=True),
    Output('store', 'data', allow_duplicate=True),
    Input('select-obs', 'selectedData'),
    Input('do-reset', 'data'),
    prevent_initial_call=True
)
def display_selected_data(selectedData, do_reset=False):
    if do_reset: #Reset button was pressed
#        return  None, None  # Clear the selected data and store
#        selectedData = {}
        #selected_list = [point['customdata'] for point in selectedData['points']]
        unique_obs_types.clear()  # Clear the unique types list
        customdata_list.clear()  # Clear the customdata list
        return

    print('selectedData', selectedData)
    selected_list = [point['customdata'] for point in selectedData['points']]
    for item in selected_list:
        if item not in customdata_list:
            customdata_list.append(item) ##HERE FIX THIS 
    print('selected_list: ', selected_list)
    # Retrieve the last item in each customdata list (this is the obs number)
    obs_numbers = [data[-1] for data in customdata_list]
    obs_types = [data[1] for data in customdata_list]
#    print(obs_types)
    for item in obs_types:
        if item not in unique_obs_types:
            unique_obs_types.append(item)

    obs_numbers_json = json.dumps(obs_numbers, indent=2)
    obs_types_json = json.dumps(unique_obs_types, indent=2)
    print('obs_numbers: ', obs_numbers)
    return ('Total number of observations selected: ', len(obs_numbers),
            '\n\nTypes of observations selected: ', obs_types_json,
            '\n\nSelected observations (obs_num): ', obs_numbers_json), obs_numbers

@callback(
    Output('confirmation', 'children', allow_duplicate=True),
    Input('submit', 'n_clicks'),
    Input('store', 'data'),
    prevent_initial_call=True
)
def write_obs_seq(n_clicks, data):
    if n_clicks >= 1:
        # Create a new obs_seq with only the selected observations
        print('passed data: ', data)
        if data == None:
            return
        else:
            obs_seq_selected.df = obs_seq_selected.df[obs_seq_selected.df['obs_num'].isin(data)]
            obs_seq_selected.write_obs_seq('./obs_seq.final.'+str(len(data))+'_selected_obs')

            return 'New observation sequence created with the selected observations!'

@callback(
    Output('selected-data', 'children', allow_duplicate=True),
    Output('confirmation', 'children', allow_duplicate=True),
    Output('store', 'data', allow_duplicate=True),
    Output('submit', 'n_clicks'),
#    Output('reset_button', 'n_clicks'),
    Output('reset-confirmation', 'children'),
    Output('do-reset', 'data'),
    Input('reset_button', 'n_clicks'),
    prevent_initial_call=True
)
def reset_fig(n_clicks):
    if n_clicks >= 1:
        return None, None, [None], 0, 'Selected data reset', [True]

# Run the app
if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
