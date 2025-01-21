import pandas as pd
import numpy as np
from functools import wraps
#from pydartdiags.obs_sequence import obs_sequence as obsq

def apply_to_phases_in_place(func):
    """
    Decorator to apply a function to both 'prior' and 'posterior' phases
    and modify the DataFrame in place.

    The decorated function should accept 'phase' as its first argument.
    """
    @wraps(func)
    def wrapper(df, *args, **kwargs):
        for phase in ['prior', 'posterior']:
            if f"{phase}_ensemble_spread" in df.columns:
                func(df, phase, *args, **kwargs)
        return df
    return wrapper

def apply_to_phases_by_type_return_df(func):
    """
    Decorator to apply a function to both 'prior' and 'posterior' phases and return a new DataFrame.

    The decorated function should accept 'phase' as its first argument and return a DataFrame.
    """
    @wraps(func)
    def wrapper(df, *args, **kwargs):
        results = []
        for phase in ['prior', 'posterior']:
            if f"{phase}_ensemble_mean" in df.columns:
                result = func(df, phase, *args, **kwargs)
                results.append(result)

        if 'midpoint' in result.columns:
            if len(results) == 2:
                return pd.merge(results[0],results[1], 
                             on=['midpoint', 'vlevels', 'type', 'vert_unit'])
            else:
                return results[0]
        else:
            if (len(results) == 2):
                return pd.merge(results[0],results[1], on='type')
            else:
                return results[0]
    return wrapper

def apply_to_phases_by_obs(func):
    """
    Decorator to apply a function to both 'prior' and 'posterior' phases and return a new DataFrame.

    The decorated function should accept 'phase' as its first argument and return a DataFrame.
    """
    @wraps(func)
    def wrapper(df, *args, **kwargs):
        
        res_df = func(df, 'prior', *args, **kwargs)
        if 'posterior_ensemble_mean' in df.columns:
            posterior_df = func(df, 'posterior', *args, **kwargs)
            res_df['posterior_rank'] = posterior_df['posterior_rank']

        return res_df

    return wrapper

@apply_to_phases_by_obs
def calculate_rank(df, phase):
    """
    Calculate the rank of observations within an ensemble.

    This function takes a DataFrame containing ensemble predictions and observed values,
    adds sampling noise to the ensemble predictions, and calculates the rank of the observed
    value within the perturbed ensemble for each observation. The rank indicates the position
    of the observed value within the sorted ensemble values, with 1 being the lowest. If the
    observed value is larger than the largest ensemble member, its rank is set to the ensemble
    size plus one.

    Parameters:
        df (pd.DataFrame): A DataFrame with columns for rank, and observation type. 
        
    Returns:
        DataFrame containing columns for 'rank' and 'obstype'.
    """
    column = f"{phase}_ensemble_member"
    ensemble_values = df.filter(regex=column).to_numpy().copy()
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
        'type': obstype,  
        f"{phase}_rank": rank 
    })

    return result_df

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

@apply_to_phases_in_place  
def diag_stats(df, phase): 
    """
    Calculate diagnostic statistics for a given phase and add them to the DataFrame.
 
    Args:
        df (pandas.DataFrame): The input DataFrame containing observation data and ensemble statistics. 
                               The DataFrame must include the following columns:
                               - 'observation': The actual observation values.
                               - 'obs_err_var': The variance of the observation error.
                               - 'prior_ensemble_mean' and/or 'posterior_ensemble_mean': The mean of the ensemble.
                               - 'prior_ensemble_spread' and/or 'posterior_ensemble_spread': The spread of the ensemble.
   
        phase (str): The phase for which to calculate the statistics ('prior' or 'posterior').
                               
    Returns:
        None: The function modifies the DataFrame in place by adding the following columns:
            - 'prior_sq_err' and/or 'posterior_sq_err': The square error for the 'prior' and 'posterior' phases.
            - 'prior_bias' and/or 'posterior_bias': The bias for the 'prior' and 'posterior' phases.
            - 'prior_totalvar' and/or 'posterior_totalvar': The total variance for the 'prior' and 'posterior' phases.

    Notes:
        - Spread is the standard deviation of the ensemble.
        - The function modifies the input DataFrame by adding new columns for the calculated statistics.
    """
    pd.options.mode.copy_on_write = True
    #if f"{phase}_ensemble_spread" in df.columns:
 
    # input from the observation sequence
    spread_column = f"{phase}_ensemble_spread"
    mean_column = f"{phase}_ensemble_mean"

    # Calulated from the observation sequence
    sq_err_column = f"{phase}_sq_err"
    bias_column = f"{phase}_bias"
    totalvar_column = f"{phase}_totalvar"

    df[sq_err_column] = (df[mean_column] - df['observation'])**2
    df[bias_column] = df[mean_column] - df['observation']
    df[totalvar_column] = df['obs_err_var'] + df[spread_column]**2

def bin_by_layer(df, levels, verticalUnit="pressure (Pa)"):
    """
    Bin observations by vertical layers and add 'vlevels' and 'midpoint' columns to the DataFrame.

    This function bins the observations in the DataFrame based on the specified vertical levels and adds two new columns:
    'vlevels', which represents the categorized vertical levels, and 'midpoint', which represents the midpoint of each
    vertical level bin. Only observations (row) with the specified vertical unit are binned.

    Args:
        df (pandas.DataFrame): The input DataFrame containing observation data. The DataFrame must include the following columns:
                               - 'vertical': The vertical coordinate values of the observations.
                               - 'vert_unit': The unit of the vertical coordinate values.
        levels (list): A list of bin edges for the vertical levels.
        verticalUnit (str, optional): The unit of the vertical axis (e.g., 'pressure (Pa)'). Default is 'pressure (Pa)'.

    Returns:
        pandas.DataFrame: The input DataFrame with additional columns for the binned vertical levels and their midpoints:
                          - 'vlevels': The categorized vertical levels.
                          - 'midpoint': The midpoint of each vertical level bin.

    Notes: 
        - The function modifies the input DataFrame by adding 'vlevels' and 'midpoint' columns.
        - The 'midpoint' values are calculated as half the midpoint of each vertical level bin.
        - Pressure units (Pa) are converted to hPa for the 'midpoint' values.
    """
    pd.options.mode.copy_on_write = True
    df.loc[df['vert_unit'] == verticalUnit, 'vlevels'] = pd.cut(df.loc[df['vert_unit'] == verticalUnit, 'vertical'], levels)
    if verticalUnit == "pressure (Pa)":
        df.loc[:,'midpoint'] = df['vlevels'].apply(lambda x: x.mid ) # HK todo units HPa - change now or in plotting?
        df.loc[:,'vlevels'] = df['vlevels'].apply(lambda x: x ) # HK todo units HPa - change now or in plotting?
    else:
        df.loc[:,'midpoint'] = df['vlevels'].apply(lambda x: x.mid)    

@apply_to_phases_by_type_return_df
def grand_statistics(df, phase):
 
    # assiming diag_stats has been called 
    grand = df.groupby(['type'], observed=False).agg({
        f"{phase}_sq_err": mean_then_sqrt,
        f"{phase}_bias": 'mean',
        f"{phase}_totalvar": mean_then_sqrt     
    }).reset_index()

    grand.rename(columns={f"{phase}_sq_err": f"{phase}_rmse"}, inplace=True)
    grand.rename(columns={f"{phase}_totalvar": f"{phase}_totalspread"}, inplace=True)  

    return grand

@apply_to_phases_by_type_return_df
def layer_statistics(df, phase):

    # assiming diag_stats has been called 
    layer_stats = df.groupby(['midpoint','type'], observed=False).agg({
        f"{phase}_sq_err": mean_then_sqrt,
        f"{phase}_bias": 'mean',
        f"{phase}_totalvar": mean_then_sqrt,
        'vert_unit': 'first' ,
        'vlevels': 'first',
    }).reset_index()

    layer_stats.rename(columns={f"{phase}_sq_err": f"{phase}_rmse"}, inplace=True)
    layer_stats.rename(columns={f"{phase}_totalvar": f"{phase}_totalspread"}, inplace=True)  

    return layer_stats

def possible_vs_used(df):
    """
    Calculates the count of possible vs. used observations by type.

    This function takes a DataFrame containing observation data, including a 'type' column for the observation
    type and an 'observation' column. The number of used observations ('used'), is the total number
    minus the observations that failed quality control checks (as determined by the `select_failed_qcs` function).
    The result is a DataFrame with each observation type, the count of possible observations, and the count of
    used observations.

    Returns:
        pd.DataFrame: A DataFrame with three columns: 'type', 'possible', and 'used'. 'type' is the observation type,
        'possible' is the count of all observations of that type, and 'used' is the count of observations of that type
        that passed quality control checks.
    """
    possible = df.groupby('type')['observation'].count()
    possible.rename('possible', inplace=True)
    
    failed_qcs = select_failed_qcs(df).groupby('type')['observation'].count()
    used = possible - failed_qcs.reindex(possible.index, fill_value=0)
    used.rename('used', inplace=True)
    
    return pd.concat([possible, used], axis=1).reset_index()

def possible_vs_used_by_layer(df):
    """
    Calculates the count of possible vs. used observations by type and vertical level.
    """
    possible = df.groupby(['type', 'midpoint'], observed=False)['type'].count()
    possible.rename('possible', inplace=True)
    
    failed_qcs = select_failed_qcs(df).groupby(['type', 'midpoint'], observed=False)['type'].count()
    used = possible - failed_qcs.reindex(possible.index, fill_value=0)
    used.rename('used', inplace=True)
    
    return pd.concat([possible, used], axis=1).reset_index()

def select_failed_qcs(df):
        """
        Select rows from the DataFrame where the DART quality control flag is greater than 0.

        Returns:
            pandas.DataFrame: A DataFrame containing only the rows with a DART quality control flag greater than 0.
        """
        return df[df['DART_quality_control'] > 0]
