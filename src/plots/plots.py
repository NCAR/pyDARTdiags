
import numpy as np
import plotly.express as px
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

#def plot_rank_histogram(rank, ens_size):
#    fig = px.histogram(rank, nbins=ens_size, title='Rank Histogram', labels={'value':'Rank'})
#    


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
    - df (pd.DataFrame): A DataFrame with columns for mean, standard deviation, observed values,
      ensemble size, and observation type. The DataFrame should have one row per observation.

    Returns:
    - tuple: A tuple containing the rank array, ensemble size, and a result DataFrame. The result
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

def plot_profile(df, levels):

    pd.options.mode.copy_on_write = True
    if df['vertical'].isnull().values.any(): # what about horizontal observations?
        raise ValueError("Missing values in 'vertical' column.")
    else:
        df.loc[:,'plevels'] = pd.cut(df['vertical'], levels)
        df.loc[:,'hPa'] = df['plevels'].apply(lambda x: x.mid)

    df_profile = rmse_bias(df)
    fig = px.line(df_profile, y='hPa', x='rmse', title='RMSE by Level', markers=True, color='type', width=800, height=800)
    fig.update_yaxes(autorange="reversed")
    fig.show()
    return df_profile, fig
    
    
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
    """
    return np.sqrt(np.mean(x))

def rmse_bias(df):
    rmse_bias_df = df.groupby(['hPa', 'type']).agg({'sq_err':mean_then_sqrt, 'bias':'mean'}).reset_index()
    rmse_bias_df.rename(columns={'sq_err':'rmse'}, inplace=True)
    
    return rmse_bias_df


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
        obs_type_agg = obs_type_df.groupby('plevels').agg({'sq_err':mean_then_sqrt, 'bias':'mean'}).reset_index()
        obs_type_agg.rename(columns={'sq_err':'rmse'}, inplace=True)
        return obs_type_agg

