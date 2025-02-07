# SPDX-License-Identifier: Apache-2.0
from pydartdiags.stats import stats
import matplotlib.pyplot as plt

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
    qc0 = obs_seq.select_by_dart_qc(0)  # filter only qc=0

    # filter by type
    qc0 = qc0[qc0["type"] == type]
    all_df = obs_seq.df[obs_seq.df["type"] == type]

    # grand statistics
    grand = stats.grand_statistics(qc0)

    # add level bins to the dataframe
    stats.bin_by_layer(all_df, levels)  # have to count used vs possible
    stats.bin_by_layer(qc0, levels)

    # aggregate by layer
    df_pvu = stats.possible_vs_used_by_layer(all_df)  # possible vs used
    df = stats.layer_statistics(qc0)  # bias, rmse, totalspread for plotting

    fig, ax1 = plt.subplots()

    # convert to hPa HK @todo only for Pressure (Pa)
    df["midpoint"] = df["midpoint"].astype(float)
    df["midpoint"] = df["midpoint"] / 100.0

    df_pvu["midpoint"] = df_pvu["midpoint"].astype(float)
    df_pvu["midpoint"] = df_pvu["midpoint"] / 100.0

    # Add horizontal stripes alternating between gray and white to represent the vertical levels
    left = df["vlevels"].apply(lambda x: x.left / 100.0)  # todo convert to HPa
    right = df["vlevels"].apply(lambda x: x.right / 100.0)
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

    ax1.invert_yaxis()
    ax1.set_title(type)
    datalabel = "bias," + " " + "rmse," + " " + "totalspread"
    ax1.set_xlabel(datalabel)

    lines1, labels1 = ax1.get_legend_handles_labels()
    ax1.legend(lines1, labels1, loc="upper left", bbox_to_anchor=(1.05, 1))

    ax1.text(
        0.5, -0.15, obs_seq.file, ha="center", va="center", transform=ax1.transAxes
    )

    # Add a text box with information below the legend
    textstr = "Grand statistics:\n"
    if bias:
        textstr += f"- prior_bias: {bias_prior:.7f}\n"
    if rmse:
        textstr += f"- rmse_prior: {rmse_prior:.7f}\n"
    if totalspread:
        textstr += f"- totalspread_prior: {totalspread_prior:.7f}\n"
    if "posterior_bias" in df.columns:
        if bias:
            textstr += f"- posterior_bias: {bias_posterior:.7f}\n"
        if rmse:
            textstr += f"- rmse_posterior: {rmse_posterior:.7f}\n"
        if totalspread:
            textstr += f"- totalspread_posterior: {totalspread_posterior:.7f}\n"

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

    plt.show()

    return fig


def plot_rank_histogram(obs_seq, levels, type, ens_size):

    qc0 = obs_seq.select_by_dart_qc(0)  # filter only qc=0
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
