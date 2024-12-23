
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def plot_rank_histogram(df):  
    """
    Plots a rank histogram colored by observation type.

    All histogram bars are initalized to be hidden and can be toggled visible in the plot's legend
    """
    _, _, df_hist = calculate_rank(df)
    fig = px.histogram(df_hist, x='rank', color='obstype', title='Histogram Colored by obstype')
    for trace in fig.data:
        trace.visible = 'legendonly'
    fig.show()


def calculate_rank(df):
    """
    Calculate the rank of observations within an ensemble.

    This function takes a DataFrame containing ensemble predictions and observed values,
    adds sampling noise to the ensemble predictions, and calculates the rank of the observed
    value within the perturbed ensemble for each observation. The rank indicates the position
    of the observed value within the sorted ensemble values, with 1 being the lowest. If the
    observed value is larger than the largest ensemble member, its rank is set to the ensemble
    size plus one.

    Parameters:
        df (pd.DataFrame): A DataFrame with columns for mean, standard deviation, observed values,
                           ensemble size, and observation type. The DataFrame should have one row per observation.

    Returns:
        tuple: A tuple containing the rank array, ensemble size, and a result DataFrame. The result
        DataFrame contains columns for 'rank' and 'obstype'.
    """
    ensemble_values = df.filter(regex='prior_ensemble_member').to_numpy().copy()
    std_dev = np.sqrt(df['obs_err_var']).to_numpy()
    obsvalue = df['observation'].to_numpy()
    obstype = df['type'].to_numpy()
    ens_size = ensemble_values.shape[1]
    mean = 0.0 # mean of the sampling noise
    rank = np.zeros(obsvalue.shape[0], dtype=int)
    
    for obs in range(ensemble_values.shape[0]):
        sampling_noise = np.random.normal(mean, std_dev[obs], ens_size)
        ensemble_values[obs] += sampling_noise
        ensemble_values[obs].sort()
        for i, ens in enumerate(ensemble_values[obs]):
            if obsvalue[obs] <= ens:
                rank[obs] = i + 1
                break

        if rank[obs] == 0: # observation is larger than largest ensemble member
            rank[obs] = ens_size + 1

    result_df = pd.DataFrame({
        'rank': rank,
        'obstype': obstype
    })

    return (rank, ens_size, result_df)

def plot_profile(df, levels, verticalUnit = "pressure (Pa)"):
    """
    Plots RMSE, bias, and total spread profiles for different observation types across specified vertical levels.

    This function takes a DataFrame containing observational data and model predictions, categorizes
    the data into specified vertical levels, and calculates the RMSE, bias and total spread for each level and
    observation type. It then plots three line charts: one for RMSE, one for bias, one for total spread, as functions
    of vertical level. The vertical levels are plotted on the y-axis in reversed order to represent
    the vertical profile in the atmosphere correctly if the vertical units are pressure.

    Parameters:
        df (pd.DataFrame): The input DataFrame containing at least the 'vertical' column for vertical levels,
        the vert_unit column, and other columns required by the `rmse_bias` function for calculating RMSE and 
        Bias.
        levels (array-like): The bin edges for categorizing the 'vertical' column values into the desired 
        vertical levels.
        verticalUnit (string) (optional): The vertical unit to be used. Only observations in df which have this
        string in the vert_unit column will be plotted. Defaults to 'pressure (Pa)'.

    Returns:
        tuple: A tuple containing the DataFrame with RMSE, bias and total spread calculations,
        The DataFrame includes a 'vlevels' column representing the categorized vertical levels
        and 'midpoint' column representing the midpoint of each vertical level bin. And the three figures.

    Raises:
        ValueError: If there are missing values in the 'vertical' column of the input DataFrame.
        ValueError: If none of the input obs have 'verticalUnit' in the 'vert_unit' column of the input DataFrame.

    Note:
        - The function modifies the input DataFrame by adding 'vlevels' and 'midpoint' columns.
        - The 'midpoint' values are calculated as half the midpoint of each vertical level bin, which may need
          adjustment based on the specific requirements for vertical level representation.
        - The plots are generated using Plotly Express and are displayed inline. The y-axis of the plots is
          reversed to align with standard atmospheric pressure level representation if the vertical units
          are atmospheric pressure.
    """

    pd.options.mode.copy_on_write = True
    if df['vertical'].isnull().values.any(): # what about horizontal observations?
        raise ValueError("Missing values in 'vertical' column.")
    elif verticalUnit not in df['vert_unit'].values:
        raise ValueError("No obs with expected vertical unit '"+verticalUnit+"'.")
    else:
        df = df[df["vert_unit"].isin({verticalUnit})] # Subset to only rows with the correct vertical unit
        df.loc[:,'vlevels'] = pd.cut(df['vertical'], levels)
        if verticalUnit == "pressure (Pa)":
            df.loc[:,'midpoint'] = df['vlevels'].apply(lambda x: x.mid / 100.) # HK todo units
        else:
            df.loc[:,'midpoint'] = df['vlevels'].apply(lambda x: x.mid)

    # Calculations
    df_profile_prior = rmse_bias_totalspread(df, phase='prior')
    df_profile_posterior = None
    if 'posterior_ensemble_mean' in df.columns:
        df_profile_posterior = rmse_bias_totalspread(df, phase='posterior')

    # Merge prior and posterior dataframes
    if df_profile_posterior is not None:
        df_profile = pd.merge(df_profile_prior, df_profile_posterior, on=['midpoint', 'type'], suffixes=('_prior', '_posterior'))
        fig_rmse = plot_profile_prior_post(df_profile, 'rmse', verticalUnit)
        fig_rmse.show()
        fig_bias = plot_profile_prior_post(df_profile, 'bias', verticalUnit)
        fig_bias.show()
        fig_ts = plot_profile_prior_post(df_profile, 'totalspread', verticalUnit)
        fig_ts.show()
    else:
        df_profile = df_profile_prior
        fig_rmse = plot_profile_prior(df_profile, 'rmse', verticalUnit)
        fig_rmse.show()
        fig_bias = plot_profile_prior(df_profile, 'bias', verticalUnit)
        fig_bias.show()
        fig_ts = plot_profile_prior(df_profile, 'totalspread', verticalUnit)
        fig_ts.show()   

    return df_profile, fig_rmse, fig_ts, fig_bias
    
def plot_profile_prior_post(df_profile, stat, verticalUnit):
    """
    Plots prior and posterior statistics by vertical level for different observation types.

    Parameters:
        df_profile (pd.DataFrame): DataFrame containing the prior and posterior statistics.
        stat (str): The statistic to plot (e.g., 'rmse', 'bias', 'totalspread').
        verticalUnit (str): The unit of the vertical axis (e.g., 'pressure (Pa)').

    Returns:
        plotly.graph_objects.Figure: The generated Plotly figure.
    """
    # Reshape DataFrame to long format for easier plotting
    df_long = pd.melt(
        df_profile,
        id_vars=["midpoint", "type"],
        value_vars=["prior_"+stat, "posterior_"+stat],
        var_name=stat+"_type",
        value_name=stat+"_value"
    )

    # Define a color mapping for observation each type
    unique_types = df_long["type"].unique()
    colors = px.colors.qualitative.Plotly
    color_mapping = {type_: colors[i % len(colors)] for i, type_ in enumerate(unique_types)}

    # Create a mapping for line styles based on stat
    line_styles = {"prior_"+stat: "solid", "posterior_"+stat: "dash"}

    # Create the figure
    fig_stat = go.Figure()

    # Loop through each type and type to add traces
    for t in df_long["type"].unique():
        for stat_type, dash_style in line_styles.items():
            # Filter the DataFrame for this type and stat
            df_filtered = df_long[(df_long[stat+"_type"] == stat_type) & (df_long["type"] == t)]
            
            # Add a trace
            fig_stat.add_trace(go.Scatter(
                x=df_filtered[stat+"_value"],
                y=df_filtered["midpoint"],
                mode='lines+markers',
                name='prior '+t if stat_type == "prior_"+stat else 'post ',  # Show legend for "prior_stat OBS TYPE" only
                line=dict(dash=dash_style, color=color_mapping[t]),  # Same color for all traces in group
                marker=dict(size=8, color=color_mapping[t]),
                legendgroup=t  # Group traces by type
            ))

        # Update layout
        fig_stat.update_layout(
            title= stat+' by Level',
            xaxis_title=stat,
            yaxis_title=verticalUnit,
            width=800,
            height=800,
            template="plotly_white"
        )

    if verticalUnit == "pressure (Pa)":
        fig_stat.update_yaxes(autorange="reversed")

    return fig_stat


def plot_profile_prior(df_profile, stat, verticalUnit):
    """
    Plots prior statistics by vertical level for different observation types.

    Parameters:
        df_profile (pd.DataFrame): DataFrame containing the prior statistics.
        stat (str): The statistic to plot (e.g., 'rmse', 'bias', 'totalspread').
        verticalUnit (str): The unit of the vertical axis (e.g., 'pressure (Pa)').

    Returns:
        plotly.graph_objects.Figure: The generated Plotly figure.
    """
    # Reshape DataFrame to long format for easier plotting - not needed for prior only, but
    #   leaving it in for consistency with the plot_profile_prior_post function for now
    df_long = pd.melt(
        df_profile,
        id_vars=["midpoint", "type"],
        value_vars=["prior_"+stat],
        var_name=stat+"_type",
        value_name=stat+"_value"
    )

    # Define a color mapping for observation each type
    unique_types = df_long["type"].unique()
    colors = px.colors.qualitative.Plotly
    color_mapping = {type_: colors[i % len(colors)] for i, type_ in enumerate(unique_types)}

    # Create the figure
    fig_stat = go.Figure()

    # Loop through each type to add traces
    for t in df_long["type"].unique():
        # Filter the DataFrame for this type and stat
        df_filtered = df_long[(df_long["type"] == t)]
        
        # Add a trace
        fig_stat.add_trace(go.Scatter(
            x=df_filtered[stat+"_value"],
            y=df_filtered["midpoint"],
            mode='lines+markers',
            name='prior ' + t,
            line=dict(color=color_mapping[t]),  # Same color for all traces in group
            marker=dict(size=8, color=color_mapping[t]),
            legendgroup=t  # Group traces by type
        ))

    # Update layout
    fig_stat.update_layout(
        title=stat + ' by Level',
        xaxis_title=stat,
        yaxis_title=verticalUnit,
        width=800,
        height=800,
        template="plotly_white"
    )

    if verticalUnit == "pressure (Pa)":
        fig_stat.update_yaxes(autorange="reversed")
        
    return fig_stat

    
def mean_then_sqrt(x):
    """
    Calculates the mean of an array-like object and then takes the square root of the result.

    Parameters:
        arr (array-like): An array-like object (such as a list or a pandas Series). 
                          The elements should be numeric.

    Returns:
        float: The square root of the mean of the input array.

    Raises:
        TypeError: If the input is not an array-like object containing numeric values.
         ValueError: If the input array is empty.
    """
        
    return np.sqrt(np.mean(x))

def rmse_bias_totalspread(df, phase='prior'): 
    if phase == 'prior':
        sq_err_column = 'prior_sq_err'
        bias_column = 'prior_bias'
        rmse_column = 'prior_rmse'
        spread_column = 'prior_ensemble_spread'
        totalspread_column = 'prior_totalspread'
    elif phase == 'posterior':
        sq_err_column = 'posterior_sq_err'
        bias_column = 'posterior_bias'
        rmse_column = 'posterior_rmse'
        spread_column = 'posterior_ensemble_spread'
        totalspread_column = 'posterior_totalspread'
    else:
        raise ValueError("Invalid phase. Must be 'prior' or 'posterior'.")

    rmse_bias_ts_df = df.groupby(['midpoint', 'type'], observed=False).agg({
        sq_err_column: mean_then_sqrt,
        bias_column: 'mean',
        spread_column: mean_then_sqrt,
        'obs_err_var': mean_then_sqrt     
    }).reset_index()

    # Add column for totalspread
    rmse_bias_ts_df[totalspread_column] = np.sqrt(rmse_bias_ts_df[spread_column] + rmse_bias_ts_df['obs_err_var'])

    # Rename square error to root mean square error
    rmse_bias_ts_df.rename(columns={sq_err_column: rmse_column}, inplace=True)
    
    return rmse_bias_ts_df

def rmse_bias_by_obs_type(df, obs_type):
    """
    Calculate the RMSE and bias for a given observation type.

    Parameters:
        df (DataFrame): A pandas DataFrame.
        obs_type (str): The observation type for which to calculate the RMSE and bias.

    Returns:
        DataFrame: A DataFrame containing the RMSE and bias for the given observation type.

    Raises:
        ValueError: If the observation type is not present in the DataFrame.
    """
    if obs_type not in df['type'].unique():
        raise ValueError(f"Observation type '{obs_type}' not found in DataFrame.")
    else:
        obs_type_df = df[df['type'] == obs_type]
        obs_type_agg = obs_type_df.groupby('vlevels', observed=False).agg({'sq_err':mean_then_sqrt, 'bias':'mean'}).reset_index()
        obs_type_agg.rename(columns={'sq_err':'rmse'}, inplace=True)
        return obs_type_agg

