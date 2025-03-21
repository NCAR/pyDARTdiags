# SPDX-License-Identifier: Apache-2.0
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from pydartdiags.stats import stats


def plot_rank_histogram(df, phase, ens_size):
    """
    Plots a rank histogram colored by observation type.

    All histogram bars are initialized to be hidden and can be toggled visible in the plot's legend
    """
    fig = px.histogram(
        df,
        x=f"{phase}_rank",
        color="type",
        title="Histogram Colored by obs type",
        nbins=ens_size,
    )
    fig.update_xaxes(range=[1, ens_size + 1])
    for trace in fig.data:
        trace.visible = "legendonly"
    fig.show()


def plot_profile(df_in, verticalUnit):
    """Assumes diag_stats has been run on the dataframe and the resulting dataframe is passed in"""

    df = stats.layer_statistics(df_in)
    if "posterior_rmse" in df.columns:
        fig_rmse = plot_profile_prior_post(df, "rmse", verticalUnit)
        fig_rmse.show()
        fig_bias = plot_profile_prior_post(df, "bias", verticalUnit)
        fig_bias.show()
        fig_ts = plot_profile_prior_post(df, "totalspread", verticalUnit)
        fig_ts.show()
    else:
        fig_rmse = plot_profile_prior(df, "rmse", verticalUnit)
        fig_rmse.show()
        fig_bias = plot_profile_prior(df, "bias", verticalUnit)
        fig_bias.show()
        fig_ts = plot_profile_prior(df, "totalspread", verticalUnit)
        fig_ts.show()

    return fig_rmse, fig_ts, fig_bias


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
    # Filter the DataFrame to include only rows with the required verticalUnit
    df_filtered = df_profile[df_profile["vert_unit"] == verticalUnit]

    # Reshape DataFrame to long format for easier plotting
    df_long = pd.melt(
        df_profile,
        id_vars=["midpoint", "type"],
        value_vars=["prior_" + stat, "posterior_" + stat],
        var_name=stat + "_type",
        value_name=stat + "_value",
    )

    # Define a color mapping for observation each type
    unique_types = df_long["type"].unique()
    colors = px.colors.qualitative.Plotly
    color_mapping = {
        type_: colors[i % len(colors)] for i, type_ in enumerate(unique_types)
    }

    # Create a mapping for line styles based on stat
    line_styles = {"prior_" + stat: "solid", "posterior_" + stat: "dash"}

    # Create the figure
    fig_stat = go.Figure()

    # Loop through each type and type to add traces
    for t in df_long["type"].unique():
        for stat_type, dash_style in line_styles.items():
            # Filter the DataFrame for this type and stat
            df_filtered = df_long[
                (df_long[stat + "_type"] == stat_type) & (df_long["type"] == t)
            ]

            # Add a trace
            fig_stat.add_trace(
                go.Scatter(
                    x=df_filtered[stat + "_value"],
                    y=df_filtered["midpoint"],
                    mode="lines+markers",
                    name=(
                        "prior " + t if stat_type == "prior_" + stat else "post "
                    ),  # Show legend for "prior_stat OBS TYPE" only
                    line=dict(
                        dash=dash_style, color=color_mapping[t]
                    ),  # Same color for all traces in group
                    marker=dict(size=8, color=color_mapping[t]),
                    legendgroup=t,  # Group traces by type
                )
            )

        # Update layout
        fig_stat.update_layout(
            title=stat + " by Level",
            xaxis_title=stat,
            yaxis_title=verticalUnit,
            width=800,
            height=800,
            template="plotly_white",
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
        value_vars=["prior_" + stat],
        var_name=stat + "_type",
        value_name=stat + "_value",
    )

    # Define a color mapping for observation each type
    unique_types = df_long["type"].unique()
    colors = px.colors.qualitative.Plotly
    color_mapping = {
        type_: colors[i % len(colors)] for i, type_ in enumerate(unique_types)
    }

    # Create the figure
    fig_stat = go.Figure()

    # Loop through each type to add traces
    for t in df_long["type"].unique():
        # Filter the DataFrame for this type and stat
        df_filtered = df_long[(df_long["type"] == t)]

        # Add a trace
        fig_stat.add_trace(
            go.Scatter(
                x=df_filtered[stat + "_value"],
                y=df_filtered["midpoint"],
                mode="lines+markers",
                name="prior " + t,
                line=dict(color=color_mapping[t]),  # Same color for all traces in group
                marker=dict(size=8, color=color_mapping[t]),
                legendgroup=t,  # Group traces by type
            )
        )

    # Update layout
    fig_stat.update_layout(
        title=stat + " by Level",
        xaxis_title=stat,
        yaxis_title=verticalUnit,
        width=800,
        height=800,
        template="plotly_white",
    )

    if verticalUnit == "pressure (Pa)":
        fig_stat.update_yaxes(autorange="reversed")

    return fig_stat
