from pydartdiags.obs_sequence import obs_sequence as obsq
from pydartdiags.stats import stats
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


dacolors = ['green', 'magenta', 'orange', 'red']

def plot_profile(obs_seq, levels, type, bias=True, rmse=True, totalspread=True):
    """
    plot: (prior, posterior)
       - bias
       - rmse
       - totalspread

    Args:
        obs_seq, levels, type, bias, rmse, totalspread 

    Example:

        type = 'RADIOSONDE_U_WIND_COMPONENT'
        hPalevels = [0.0, 100.0,  150.0, 200.0, 250.0, 300.0, 400.0, 500.0, 700, 850, 925, 1000]  # Pa?
        levels = [i * 100 for i in hPalevels]

        plot_profile(obs_seq, levels, type, bias=True, rmse=True, totalspread=True)

    """

    # calcualate stats and add to dataframe
    stats.diag_stats(obs_seq.df) 
    qc0 = obs_seq.select_by_dart_qc(0) # filter only qc=0

    # filter by type
    qc0 = qc0[qc0['type'] == type] 
    all_df = obs_seq.df[obs_seq.df['type'] == type]

    # add level bins to the dataframe
    #hPalevels = [0.0, 100.0,  150.0, 200.0, 250.0, 300.0, 400.0, 500.0, 700, 850, 925, 1000]  # Pa?
    #levels = [i * 100 for i in hPalevels]
    stats.bin_by_layer(all_df, levels) # have to count used vs possible
    stats.bin_by_layer(qc0, levels)

    # aggreate by layer
    df_pvu = stats.possible_vs_used_by_layer(all_df) # possible vs used
    df = stats.layer_statistics(qc0) # bias, rmse, totalspread for plotting

    fig, ax1 = plt.subplots()

    # convert to hPa
    df['midpoint'] = df['midpoint'].astype(float)
    df['midpoint'] = df['midpoint'] / 100.

    df_pvu['midpoint'] = df_pvu['midpoint'].astype(float)
    df_pvu['midpoint'] = df_pvu['midpoint'] / 100.

    # Add horizontal stripes alternating between gray and white to represent the vertical levels
    left = df['vlevels'].apply(lambda x: x.left / 100.) # todo convert to HPa
    right = df['vlevels'].apply(lambda x: x.right / 100.)
    for i in range(len(left)):
        color = 'gray' if i % 2 == 0 else 'white'
        ax1.axhspan(left.iloc[i], right.iloc[i], color=color, alpha=0.3)

    # Plot the 'bias' data on the first y-axis
    if bias:
        ax1.plot(df['prior_bias'], df['midpoint'], color=dacolors[0], marker='.', linestyle = '-', label='prior bias')
        if 'posterior_bias' in df.columns:
            ax1.plot(df['posterior_bias'], df['midpoint'], color=dacolors[0], marker='.', linestyle = '--', label='posterior bias')
    
    if rmse:
        ax1.plot(df['prior_rmse'], df['midpoint'], color=dacolors[1], marker='.', linestyle = '-', label='prior RMSE')
        if 'posterior_rmse' in df.columns:
         ax1.plot(df['posterior_rmse'], df['midpoint'], color=dacolors[1], marker='.', linestyle = '--', label='posterior RMSE')
    
    if totalspread:
        ax1.plot(df['prior_totalspread'], df['midpoint'], color=dacolors[2], marker='.', linestyle = '-', label='prior totalspread')
        if 'totalspread' in df.columns:
            ax1.plot(df['posterior_totalspread'], df['midpoint'], color=dacolors[2], marker='.', linestyle = '--', label='posterior totalspread')


    ax1.set_ylabel('hPa')
    ax1.tick_params(axis='y')
    ax1.set_yticks(df['midpoint'])
    #ax1.set_yticklabels(df['midpoint'])

    ax3 = ax1.twiny()
    ax3.set_xlabel('# obs (o=possible; +=assimilated)', color=dacolors[-1])
    ax3.plot(df_pvu['possible'], df_pvu['midpoint'], color=dacolors[-1], marker='o', linestyle='', markerfacecolor='none', label='possible')
    ax3.plot(df_pvu['used'], df_pvu['midpoint'], color=dacolors[-1], marker='+', linestyle='', label='possible')
    ax3.set_xlim(left=0)


    ax1.invert_yaxis()
    ax1.set_title(type)
    datalabel = "bias," + " " + "rmse," + " " + "totalspread"
    ax1.set_xlabel(datalabel)

    lines1, labels1 = ax1.get_legend_handles_labels()
    ax1.legend(lines1 , labels1, loc='upper left', bbox_to_anchor=(1.05, 1))

    ax1.text(0.5, -0.15, obs_seq.file, ha='center', va='center', transform=ax1.transAxes)

    # Show the plot
    plt.show()

    return fig