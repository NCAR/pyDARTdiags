# SPDX-License-Identifier: Apache-2.0
import pandas as pd
import numpy as np
from functools import wraps
from datetime import datetime, timedelta

# from pydartdiags.obs_sequence import obs_sequence as obsq


def apply_to_phases_in_place(func):
    """
    Decorator to apply a function to both 'prior' and 'posterior' phases
    and modify the DataFrame in place.

    The decorated function should accept 'phase' as its first argument.
    """

    @wraps(func)
    def wrapper(df, *args, **kwargs):
        for phase in ["prior", "posterior"]:
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
        for phase in ["prior", "posterior"]:
            if f"{phase}_ensemble_mean" in df.columns:
                result = func(df, phase, *args, **kwargs)
                results.append(result)

        if not results:
            return (
                pd.DataFrame()
            )  # Return an empty DataFrame if no results are generated

        # Dynamically determine merge keys based on common columns
        common_columns = set(results[0].columns)
        for result in results[1:]:
            common_columns &= set(result.columns)

        # Exclude phase-specific columns from the merge keys
        phase_specific_columns = {
            f"{phase}_sq_err",
            f"{phase}_bias",
            f"{phase}_totalvar",
            f"{phase}_rmse",
            f"{phase}_totalspread",
        }
        merge_keys = list(common_columns - phase_specific_columns)

        if len(results) == 2:
            return pd.merge(results[0], results[1], on=merge_keys)
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

        res_df = func(df, "prior", *args, **kwargs)
        if "posterior_ensemble_mean" in df.columns:
            posterior_df = func(df, "posterior", *args, **kwargs)
            res_df["posterior_rank"] = posterior_df["posterior_rank"]

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

        phase (str): The phase for which to calculate the statistics ('prior' or 'posterior')

    Returns:
        DataFrame containing columns for 'rank' and observation 'type'.
    """
    column = f"{phase}_ensemble_member"
    ensemble_values = df.filter(regex=column).to_numpy().copy()
    std_dev = np.sqrt(df["obs_err_var"]).to_numpy()
    obsvalue = df["observation"].to_numpy()
    obstype = df["type"].to_numpy()
    ens_size = ensemble_values.shape[1]
    mean = 0.0  # mean of the sampling noise
    rank = np.zeros(obsvalue.shape[0], dtype=int)

    for obs in range(ensemble_values.shape[0]):
        sampling_noise = np.random.normal(mean, std_dev[obs], ens_size)
        ensemble_values[obs] += sampling_noise
        ensemble_values[obs].sort()
        for i, ens in enumerate(ensemble_values[obs]):
            if obsvalue[obs] <= ens:
                rank[obs] = i + 1
                break

        if rank[obs] == 0:  # observation is larger than largest ensemble member
            rank[obs] = ens_size + 1

    result_df = pd.DataFrame({"type": obstype, f"{phase}_rank": rank})

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

        phase (str): The phase for which to calculate the statistics ('prior' or 'posterior')

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

    # input from the observation sequence
    spread_column = f"{phase}_ensemble_spread"
    mean_column = f"{phase}_ensemble_mean"

    # Calculated from the observation sequence
    sq_err_column = f"{phase}_sq_err"
    bias_column = f"{phase}_bias"
    totalvar_column = f"{phase}_totalvar"

    df[sq_err_column] = (df[mean_column] - df["observation"]) ** 2
    df[bias_column] = df[mean_column] - df["observation"]
    df[totalvar_column] = df["obs_err_var"] + df[spread_column] ** 2


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
    """
    pd.options.mode.copy_on_write = True
    df.loc[df["vert_unit"] == verticalUnit, "vlevels"] = pd.cut(
        df.loc[df["vert_unit"] == verticalUnit, "vertical"], levels
    )
    df.loc[:, "midpoint"] = df["vlevels"].apply(lambda x: x.mid)


def bin_by_time(df, time_value):
    """
    Bin observations by time and add 'time_bin' and 'time_bin_midpoint' columns to the DataFrame.
    The first bin starts 1 second before the minimum time value, so the minimum time is included in the
    first bin. The last bin is inclusive of the maximum time value.

    Args:
        df (pd.DataFrame): The input DataFrame containing a 'time' column.
        time_value (str): The width of each time bin (e.g., '3600S' for 1 hour).

    Returns:
        None: The function modifies the DataFrame in place by adding 'time_bin' and 'time_bin_midpoint' columns.
    """
    # Create time bins
    start = df["time"].min() - timedelta(seconds=1)
    end = df["time"].max()
    # Determine if the end time aligns with the bin boundary
    time_delta = pd.Timedelta(time_value)
    aligned_end = (pd.Timestamp(end) + time_delta).floor(time_value)

    time_bins = pd.date_range(
        start=start,
        end=aligned_end,
        freq=time_value,
    )

    df["time_bin"] = pd.cut(df["time"], bins=time_bins)

    # Calculate the midpoint of each time bin
    df["time_bin_midpoint"] = df["time_bin"].apply(
        lambda x: x.left + (x.right - x.left) / 2 if pd.notnull(x) else None
    )


@apply_to_phases_by_type_return_df
def grand_statistics(df, phase):

    # assuming diag_stats has been called
    grand = (
        df.groupby(["type"], observed=False)
        .agg(
            {
                f"{phase}_sq_err": mean_then_sqrt,
                f"{phase}_bias": "mean",
                f"{phase}_totalvar": mean_then_sqrt,
            }
        )
        .reset_index()
    )

    grand.rename(columns={f"{phase}_sq_err": f"{phase}_rmse"}, inplace=True)
    grand.rename(columns={f"{phase}_totalvar": f"{phase}_totalspread"}, inplace=True)

    return grand


@apply_to_phases_by_type_return_df
def layer_statistics(df, phase):

    # assuming diag_stats has been called
    layer_stats = (
        df.groupby(["midpoint", "type"], observed=False)
        .agg(
            {
                f"{phase}_sq_err": mean_then_sqrt,
                f"{phase}_bias": "mean",
                f"{phase}_totalvar": mean_then_sqrt,
                "vert_unit": "first",
                "vlevels": "first",
            }
        )
        .reset_index()
    )

    layer_stats.rename(columns={f"{phase}_sq_err": f"{phase}_rmse"}, inplace=True)
    layer_stats.rename(
        columns={f"{phase}_totalvar": f"{phase}_totalspread"}, inplace=True
    )

    return layer_stats


@apply_to_phases_by_type_return_df
def time_statistics(df, phase):
    """
    Calculate time-based statistics for a given phase and return a new DataFrame.

    Args:
        df (pandas.DataFrame): The input DataFrame containing observation data and ensemble statistics.
        phase (str): The phase for which to calculate the statistics ('prior' or 'posterior').

    Returns:
        pandas.DataFrame: A DataFrame containing time-based statistics for the specified phase.
    """
    # Assuming diag_stats has been called
    time_stats = (
        df.groupby(["time_bin_midpoint", "type"], observed=False)
        .agg(
            {
                f"{phase}_sq_err": mean_then_sqrt,
                f"{phase}_bias": "mean",
                f"{phase}_totalvar": mean_then_sqrt,
                "time_bin": "first",
                "time": "first",
            }
        )
        .reset_index()
    )

    time_stats.rename(columns={f"{phase}_sq_err": f"{phase}_rmse"}, inplace=True)
    time_stats.rename(
        columns={f"{phase}_totalvar": f"{phase}_totalspread"}, inplace=True
    )

    return time_stats


def possible_vs_used(df):
    """
    Calculates the count of possible vs. used observations by type.

    This function takes a DataFrame containing observation data, including a 'type' column for the observation
    type and an 'observation' column. The number of used observations ('used'), is the total number
    of assimilated observations (as determined by the `select_used_qcs` function).
    The result is a DataFrame with each observation type, the count of possible observations, and the count of
    used observations.

    Returns:
        pd.DataFrame: A DataFrame with three columns: 'type', 'possible', and 'used'. 'type' is the observation type,
        'possible' is the count of all observations of that type, and 'used' is the count of observations of that type
        that passed quality control checks.
    """
    possible = df.groupby("type")["observation"].count()
    possible.rename("possible", inplace=True)

    used_qcs = select_used_qcs(df).groupby("type")["observation"].count()
    used = used_qcs.reindex(possible.index, fill_value=0)
    used.rename("used", inplace=True)

    return pd.concat([possible, used], axis=1).reset_index()


def possible_vs_used_by_layer(df):
    """
    Calculates the count of possible vs. used observations by type and vertical level.
    """
    possible = df.groupby(["type", "midpoint"], observed=False)["type"].count()
    possible.rename("possible", inplace=True)

    used_qcs = (
        select_used_qcs(df)
        .groupby(["type", "midpoint"], observed=False)["type"]
        .count()
    )

    used = used_qcs.reindex(possible.index, fill_value=0)
    used.rename("used", inplace=True)

    return pd.concat([possible, used], axis=1).reset_index()


def select_used_qcs(df):
    """
    Select rows from the DataFrame where the observation was used.
    Includes observations for which the posterior forward observation operators failed.

    Returns:
        pandas.DataFrame: A DataFrame containing only the rows with a DART quality control flag 0 or 2.
    """
    return df[(df["DART_quality_control"] == 0) | (df["DART_quality_control"] == 2)]


def possible_vs_used_by_time(df):
    """
    Calculates the count of possible vs. used observations by type and time bin.

    Args:
        df (pd.DataFrame): The input DataFrame containing observation data. The DataFrame must include:
                           - 'type': The observation type.
                           - 'time_bin_midpoint': The midpoint of the time bin.
                           - 'observation': The observation values.
                           - 'DART_quality_control': The quality control flag.

    Returns:
        pd.DataFrame: A DataFrame with the following columns:
                      - 'time_bin_midpoint': The midpoint of the time bin.
                      - 'type': The observation type.
                      - 'possible': The count of all observations in the time bin.
                      - 'used': The count of observations in the time bin that passed quality control checks.
    """
    # Count all observations (possible) grouped by time_bin_midpoint and type
    possible = df.groupby(["time_bin_midpoint", "type"], observed=False)["type"].count()
    possible.rename("possible", inplace=True)

    # Count used observations (QC=0 or QC=2) grouped by time_bin_midpoint and type
    used_qcs = (
        select_used_qcs(df)
        .groupby(["time_bin_midpoint", "type"], observed=False)["type"]
        .count()
    )
    used = used_qcs.reindex(possible.index, fill_value=0)
    used.rename("used", inplace=True)

    # Combine possible and used into a single DataFrame
    return pd.concat([possible, used], axis=1).reset_index()
