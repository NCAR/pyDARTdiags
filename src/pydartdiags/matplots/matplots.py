# SPDX-License-Identifier: Apache-2.0
from pydartdiags.stats import stats
import matplotlib.pyplot as plt
import textwrap
import pandas as pd

# HK @todo color scheme class
dacolors = ["green", "magenta", "orange", "red"]


def plot_profile(obs_seq, levels, type, bias=True, rmse=True, totalspread=True):
    """
    plot_profile on the levels for prior and  posterior if present
       - bias
       - rmse
       - totalspread

    Args:
        obs_seq, levels, type, bias=True, rmse=True, totalspread=True

    Example:

        type = 'RADIOSONDE_U_WIND_COMPONENT'
        hPalevels = [0.0, 100.0,  150.0, 200.0, 250.0, 300.0, 400.0, 500.0, 700, 850, 925, 1000]
        levels = [i * 100 for i in hPalevels]

        plot_profile(obs_seq, levels, type, bias=True, rmse=True, totalspread=True)

    """

    # calculate stats and add to dataframe
    stats.diag_stats(obs_seq.df)
    qc0 = stats.select_used_qcs(obs_seq.df)  # filter only qc=0, qc=2

    # filter by type
    qc0 = qc0[qc0["type"] == type]
    if qc0.empty:
        print(f"No rows found for type: {type}")
        return None

    all_df = obs_seq.df[obs_seq.df["type"] == type]  # for possible vs used

    if all_df["vert_unit"].nunique() > 1:
        print(
            f"Multiple vertical units found in the data: {all_df['vert_unit'].unique()} for type: {type}"
        )
        return None

    vert_unit = all_df.iloc[0]["vert_unit"]
    if vert_unit == "pressure (Pa)":
        conversion = 0.01  # from Pa to hPa
    else:
        conversion = 1.0  # no conversion needed

    # grand statistics
    grand = stats.grand_statistics(qc0)

    # add level bins to the dataframe
    stats.bin_by_layer(all_df, levels, verticalUnit=vert_unit)
    stats.bin_by_layer(qc0, levels, verticalUnit=vert_unit)

    # aggregate by layer
    df_pvu = stats.possible_vs_used_by_layer(all_df)  # possible vs used
    df = stats.layer_statistics(qc0)  # bias, rmse, totalspread for plotting

    # using rmse because mean_sqrt vs mean for bias (get a column with 0 obs)
    if "prior_rmse" not in df.columns:
        print(f"All layers empty for type: {type}")
        return None

    fig, ax1 = plt.subplots(figsize=(8, 8))

    # convert to hPa HK @todo only for Pressure (Pa)
    df["midpoint"] = df["midpoint"].astype(float)
    df["midpoint"] = df["midpoint"] * conversion

    df_pvu["midpoint"] = df_pvu["midpoint"].astype(float)
    df_pvu["midpoint"] = df_pvu["midpoint"] * conversion

    # Add horizontal stripes alternating between gray and white to represent the vertical levels
    left = df["vlevels"].apply(lambda x: x.left * conversion)  # todo convert to HPa
    right = df["vlevels"].apply(lambda x: x.right * conversion)
    for i in range(len(left)):
        color = "gray" if i % 2 == 0 else "white"
        ax1.axhspan(left.iloc[i], right.iloc[i], color=color, alpha=0.3)

    # Plot the 'bias' data on the first y-axis
    if bias:
        ax1.plot(
            df["prior_bias"],
            df["midpoint"],
            color=dacolors[0],
            marker=".",
            linestyle="-",
            label="prior bias",
        )
        bias_prior = grand.loc[0, "prior_bias"]
        if "posterior_bias" in df.columns:
            ax1.plot(
                df["posterior_bias"],
                df["midpoint"],
                color=dacolors[0],
                marker=".",
                linestyle="--",
                label="posterior bias",
            )
            bias_posterior = grand.loc[0, "posterior_bias"]
    if rmse:
        ax1.plot(
            df["prior_rmse"],
            df["midpoint"],
            color=dacolors[1],
            marker=".",
            linestyle="-",
            label="prior RMSE",
        )
        rmse_prior = grand.loc[0, "prior_rmse"]
        if "posterior_rmse" in df.columns:
            ax1.plot(
                df["posterior_rmse"],
                df["midpoint"],
                color=dacolors[1],
                marker=".",
                linestyle="--",
                label="posterior RMSE",
            )
            rmse_posterior = grand.loc[0, "posterior_rmse"]
    if totalspread:
        ax1.plot(
            df["prior_totalspread"],
            df["midpoint"],
            color=dacolors[2],
            marker=".",
            linestyle="-",
            label="prior totalspread",
        )
        totalspread_prior = grand.loc[0, "prior_totalspread"]
        if "posterior_totalspread" in df.columns:
            totalspread_posterior = grand.loc[0, "posterior_totalspread"]
            ax1.plot(
                df["posterior_totalspread"],
                df["midpoint"],
                color=dacolors[2],
                marker=".",
                linestyle="--",
                label="posterior totalspread",
            )

    ax1.set_ylabel("hPa")
    ax1.tick_params(axis="y")
    ax1.set_yticks(df["midpoint"])
    # ax1.set_yticklabels(df['midpoint'])

    ax3 = ax1.twiny()
    ax3.set_xlabel("# obs (o=possible; +=assimilated)", color=dacolors[-1])
    ax3.tick_params(axis="x", colors=dacolors[-1])
    ax3.plot(
        df_pvu["possible"],
        df_pvu["midpoint"],
        color=dacolors[-1],
        marker="o",
        linestyle="",
        markerfacecolor="none",
        label="possible",
    )
    ax3.plot(
        df_pvu["used"],
        df_pvu["midpoint"],
        color=dacolors[-1],
        marker="+",
        linestyle="",
        label="possible",
    )
    ax3.set_xlim(left=0)

    if vert_unit == "pressure (Pa)":
        ax1.invert_yaxis()
    ax1.set_title(type)
    # Build the datalabel string
    datalabel = []
    if bias:
        datalabel.append("bias")
    if rmse:
        datalabel.append("rmse")
    if totalspread:
        datalabel.append("totalspread")
    ax1.set_xlabel(", ".join(datalabel))

    lines1, labels1 = ax1.get_legend_handles_labels()
    ax1.legend(lines1, labels1, loc="upper left", bbox_to_anchor=(1.05, 1))

    ax1.text(
        0.6, -0.08, obs_seq.file, ha="center", va="center", transform=ax1.transAxes
    )

    # Add a text box with information below the legend
    textstr = "Grand statistics:\n"
    if bias:
        textstr += f"prior_bias: {bias_prior:.7f}\n"
    if rmse:
        textstr += f"rmse_prior: {rmse_prior:.7f}\n"
    if totalspread:
        textstr += f"totalspread_prior: {totalspread_prior:.7f}\n"
    if "posterior_bias" in df.columns:
        if bias:
            textstr += f"posterior_bias: {bias_posterior:.7f}\n"
        if rmse:
            textstr += f"rmse_posterior: {rmse_posterior:.7f}\n"
        if totalspread:
            textstr += f"totalspread_posterior: {totalspread_posterior:.7f}\n"

    props = dict(boxstyle="round", facecolor="wheat", alpha=0.5)
    ax1.text(
        1.05,
        0.5,
        textstr,
        transform=ax1.transAxes,
        fontsize=10,
        verticalalignment="top",
        bbox=props,
    )

    plt.tight_layout()
    plt.show()

    return fig


def plot_rank_histogram(obs_seq, levels, type, ens_size):

    qc0 = stats.select_used_qcs(obs_seq.df)  # filter only qc=0, qc=2
    qc0 = qc0[qc0["type"] == type]  # filter by type
    stats.bin_by_layer(qc0, levels)  # bin by level

    midpoints = qc0["midpoint"].unique()

    for level in sorted(midpoints):

        df = qc0[qc0["midpoint"] == level]

        df = stats.calculate_rank(qc0)

        if "posterior_rank" in df.columns:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
        else:
            fig, ax1 = plt.subplots()

        # Plot the prior rank histogram
        bins = list(range(1, ens_size + 2))
        ax1.hist(
            df["prior_rank"], bins=bins, color="blue", alpha=0.5, label="prior rank"
        )
        ax1.set_title("Prior Rank Histogram")
        ax1.set_xlabel("Observation Rank (among ensemble members)")
        ax1.set_ylabel("Count")

        # Plot the posterior rank histogram if it exists
        if "posterior_rank" in df.columns:
            ax2.hist(
                df["posterior_rank"],
                bins=bins,
                color="green",
                alpha=0.5,
                label="posterior rank",
            )
            ax2.set_title("Posterior Rank Histogram")
            ax2.set_xlabel("Observation Rank (among ensemble members)")
            ax2.set_ylabel("Count")

        fig.suptitle(f"{type} at Level {level}", fontsize=14)

        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        plt.show()

    return fig


def plot_evolution(obs_seq, type, time_bins, stat, levels=None, columns=None):
    """
    Plot the time evolution of the requested statistics.

    Args:
        obs_seq: The observation sequence object.
        type (str): The type of observation to filter by.
        levels (list, optional): The levels to bin by. If None, plot every row.
        stat (str): The statistic to plot. Default is "prior_rmse".

    Returns:
        None
    """
    # Calculate stats and add to dataframe
    stats.diag_stats(obs_seq.df)
    qc0 = stats.select_used_qcs(obs_seq.df)  # filter only qc=0, qc=2
    qc0 = qc0[qc0["type"] == type]  # filter by type

    if levels:
        stats.bin_by_layer(qc0, levels)  # bin by level
        midpoints = qc0["midpoint"].unique()

        print(qc0.columns)

        for level in sorted(midpoints):
            df = qc0[qc0["midpoint"] == level]

            # bin by time
            df["time_bin"] = pd.cut(df["time"], bins=time_bins)
            # aggregate by time bin
            if stat == "rmse":
                if "posterior_rmse" in df.columns:
                    df = df.groupby("time_bin").agg(
                        prior_rmse=("prior_rmse", "mean"),
                        posterior_rmse=("posterior_rmse", "mean"),
                    )
                else:
                    df = df.groupby("time_bin").agg(
                        prior_rmse=("prior_rmse", "mean"),
                    )
            elif stat == "bias":
                if "posterior_bias" in df.columns:
                    df = df.groupby("time_bin").agg(
                        prior_bias=("prior_bias", mean_then_sqrt),
                        posterior_bias=("posterior_bias", mean_then_sqrt),
                    )
                else:
                    df = df.groupby("time_bin").agg(
                        prior_bias=("prior_bias", mean_then_sqrt),
                    )
            elif stat == "totalspread":
                if "posterior_totalspread" in df.columns:
                    df = df.groupby("time_bin").agg(
                        prior_totalspread=("prior_totalspread", "mean"),
                        posterior_totalspread=("posterior_totalspread", "mean"),
                    )
                else:
                    df = df.groupby("time_bin").agg(
                        prior_totalspread=("prior_totalspread", "mean"),
                    )

            # Plot the time evolution of requested stats
            fig, ax1 = plt.subplots()
            if "prior_" + stat in df.columns:
                ax1.plot(df["time"], df["prior_" + stat], label=stat)
            if "posterior_" + stat in df.columns:
                ax1.plot(df["time"], df["posterior_" + stat], label=f"posterior {stat}")
            if columns is not None:
                for col in columns:
                    ax1.plot(df["time"], df[col], label=col)
            ax1.legend()
            ax1.set_title(f"{type} at level {level}")
            ax1.set_xlabel("time")
            ax1.set_ylabel(stat)
            plt.show()
    else:

        # bin by time
        print(time_bins)
        qc0["time_bin"] = pd.cut(qc0["time"], bins=time_bins)
        stats.time_statistics(qc0)
        df = qc0

        # aggregate by time bin
        if stat == "rmse":
            if "posterior_rmse" in df.columns:
                df = df.groupby("time_bin").agg(
                    prior_rmse=("prior_rmse", "mean"),
                    posterior_rmse=("posterior_rmse", "mean"),
                )
            else:
                df = df.groupby("time_bin").agg(
                    prior_rmse=("prior_rmse", "mean"),
                )
        elif stat == "bias":
            if "posterior_bias" in df.columns:
                df = df.groupby("time_bin").agg(
                    prior_bias=("prior_bias", mean_then_sqrt),
                    posterior_bias=("posterior_bias", mean_then_sqrt),
                )
            else:
                df = df.groupby("time_bin").agg(
                    prior_bias=("prior_bias", mean_then_sqrt),
                )
        elif stat == "totalspread":
            if "posterior_totalspread" in df.columns:
                df = df.groupby("time_bin").agg(
                    prior_totalspread=("prior_totalspread", "mean"),
                    posterior_totalspread=("posterior_totalspread", "mean"),
                )
            else:
                df = df.groupby("time_bin").agg(
                    prior_totalspread=("prior_totalspread", "mean"),
                )

        # Plot the time evolution of requested stats
        fig, ax1 = plt.subplots()
        if "prior_" + stat in df.columns:
            ax1.plot(df["time_bin"], df["prior_" + stat], label=stat)
        if "posterior_" + stat in df.columns:
            ax1.plot(df["time_bin"], df["posterior_" + stat], label=f"posterior {stat}")
        if columns is not None:
            for col in columns:
                ax1.plot(df["time_bin"], df[col], label=col)
        ax1.legend()
        ax1.set_title(f"{type}")
        ax1.set_xlabel("time")
        ax1.set_ylabel(stat)
        plt.show()
