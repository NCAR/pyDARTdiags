
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