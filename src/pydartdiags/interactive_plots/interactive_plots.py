from dash import Dash, dcc, html, Input, Output, callback
import pandas as pd
import plotly.express as px
import json

dash_styles = { 
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll',
        'color': 'black'
    },
    'txt': {
        'color': 'black'
    } 
}

def geo_plot(obs_seq):

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
        width=1400,
        height=850,
    )

    fig.update_layout(clickmode='event+select')
    # If the obs_seq has more than 10,000 observations, do not show hover info
    # to reduce strain on the Dash app
    if len(obs_seq.df) > 10000:
        fig.update_traces(hoverinfo='skip', hovertemplate=None)

    return fig

# Creates Dash app to create a new obs_seq file including only
# the selected obs
def include_only_selected_obs_dash_app(fig, obs_seq_selected):

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

            To reset the Dash app, simply refresh the page.
        """, style=dash_styles['txt']),

        dcc.Graph(id='select-obs', figure=fig),

        html.Button('Submit', id='submit-val', n_clicks=0),

        html.Pre(id='confirmation', style=dash_styles['pre']),

        html.Pre(id='selected-data', style=dash_styles['pre']),

        dcc.Store(id="store")
    ]

    customdata_list = []
    unique_obs_types = []

    @callback(
        Output('selected-data', 'children'),
        Output('store', 'data'),
        Input('select-obs', 'selectedData'),
        prevent_initial_call=True
    )
    def get_selected_data(selectedData):
        selected_list = [point['customdata'] for point in selectedData['points']]
        for item in selected_list:
            if item not in customdata_list:
                customdata_list.append(item)

        # Retrieve the observation number and type from customdata_list
        obs_numbers = [data[-1] for data in customdata_list]
        obs_types = [data[1] for data in customdata_list]

        # Create list where selected obs types are only included once
        for item in obs_types:
            if item not in unique_obs_types:
                unique_obs_types.append(item)

        # Dump lists to json
        obs_numbers_json = json.dumps(obs_numbers, indent=2)
        obs_types_json = json.dumps(unique_obs_types, indent=2)

        # Display info on the selected data in the Dash app
        return ('Total number of observations selected: ', len(obs_numbers),
                '\n\nTypes of observations selected: ', obs_types_json,
                '\n\nSelected observations (obs_num): ', obs_numbers_json), obs_numbers

    @callback(
        Output('confirmation', 'children'),
        Input('submit-val', 'n_clicks'),
        Input('store', 'data'),
        prevent_initial_call=True
    )
    def update_output(n_clicks, data):
        if n_clicks >=1:

            # Update the obs_seq_selected dataframe to only include the selected observations
            obs_seq_selected.df = obs_seq_selected.df[obs_seq_selected.df['obs_num'].isin(data)]

            # Write the updated  observation sequence to a file
            obs_seq_selected.write_obs_seq('./obs_seq.final.'+str(len(data))+'_selected_obs')

            # Display confirmation message in Dash app
            return 'New observation sequence created with the '+str(len(data))+' selected observations.'

    return app

# Builds a Dash app to create a new obs_seq file excluding
# the selected obs
def exclude_selected_obs_dash_app(fig, obs_seq_selected):

    #Initialize the Dash app
    app = Dash()

    # App layout
    app.layout = [
        dcc.Markdown("""
            ## **Select observations to remove them from the obs sequence**

            Choose the lasso or rectangle tool in the graph's menu
            bar and then select points in the plot.

            Selection data accumulates if you perform multiple selections,
            and the currently selected observations will be shown below
            the plot.

            When you are finished selecting the desired observation, press
            the select button to create a new observation sequence file
            that excludes the selected observations.

            To reset the Dash app, simply refresh the page.
        """, style=dash_styles['txt']),

        dcc.Graph(id='select-obs', figure=fig),

        html.Button('Submit', id='submit-val', n_clicks=0),

        html.Pre(id='confirmation', style=dash_styles['pre']),

        html.Pre(id='selected-data', style=dash_styles['pre']),

        dcc.Store(id="store")
    ]

    customdata_list = []
    unique_obs_types = []

    @callback(
        Output('selected-data', 'children'),
        Output('store', 'data'),
        Input('select-obs', 'selectedData'),
        prevent_initial_call=True
    )
    def get_selected_data(selectedData):
        selected_list = [point['customdata'] for point in selectedData['points']]
        for item in selected_list:
            if item not in customdata_list:
                customdata_list.append(item)

        # Retrieve the observation number and type from customdata_list
        obs_numbers = [data[-1] for data in customdata_list]
        obs_types = [data[1] for data in customdata_list]

        # Create list where selected obs types are only included once
        for item in obs_types:
            if item not in unique_obs_types:
                unique_obs_types.append(item)

        # Dump lists to json
        obs_numbers_json = json.dumps(obs_numbers, indent=2)
        obs_types_json = json.dumps(unique_obs_types, indent=2)

        # Display info on the selected data in the Dash app
        return ('Total number of observations selected: ', len(obs_numbers),
                '\n\nTypes of observations selected: ', obs_types_json,
                '\n\nSelected observations (obs_num): ', obs_numbers_json), obs_numbers

    @callback(
        Output('confirmation', 'children'),
        Input('submit-val', 'n_clicks'),
        Input('store', 'data'),
        prevent_initial_call=True
    )
    def update_output(n_clicks, data):
        if n_clicks >=1:

            # Update the obs_seq_selected dataframe to only include the selected observations
            obs_seq_selected.df = obs_seq_selected.df[~obs_seq_selected.df['obs_num'].isin(data)]

            # Write the updated  observation sequence to a file
            obs_seq_selected.write_obs_seq('./obs_seq.final.excluding_'+str(len(data))+'_selected_obs')

            # Display confirmation message in Dash app
            return 'New observation sequence created with the '+str(len(data))+' selected observations removed.'

    return app
