# Functions to plot fits generated by functions in calcs.py

import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import statistics
from gelkineticsfit.calcs import one_phase_decay, get_average_init_rate, linear
matplotlib.rcParams.update({'errorbar.capsize': 2})

def plot_frac_folded_and_fits(data_dict: dict, fitting_dict: dict):
    """
    OLD
    Takes a data_dict generated with parse_percentage_folded_csv and a fitting_dict
    generated with get_fit_params_dict. Plots the raw kinetics from the data_dict
    as scatter and plots the fits as lines"""

    colors = iter([plt.cm.tab10(i) for i in range(20)])

    for (reaction_name, kinetics_df), \
        (reaction_name2, fit_dict), \
        color \
        in zip(data_dict.items(), fitting_dict.items(), colors):
        # plot average folded ratio
        x = kinetics_df.iloc[:, 0]
        y = kinetics_df.iloc[:, 1]
        plt.plot(x, y, marker="o", ls="none", c=color, label=reaction_name)
        # plot fitting
        maxx, minx = max(x), min(x)
        xnew = np.linspace(minx, maxx, 100) # interpolate the fit equation over 100 points
        popt = fit_dict["popt"]
        plt.plot(xnew, one_phase_decay(np.array(xnew), *popt), c=color)
    
    plt.xlabel("Time (s)")
    plt.ylabel("Fraction Folded")
    plt.legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')
    plt.show()

def plot_avdata_avfitting_as_scatter(
    avdata_dict: dict, 
    avfitting_dict: dict,
    error_bars: str="",
    y_limits: list=[0,1],
    fig_size: list=[5,6],
    colors: list=[plt.cm.tab20(i) for i in range(20)], 
    tight_layout: bool=False,
    save: str=""
    ) -> dict:
    
    """
    Takes average fraction folded data and associated one_phase_exponential fits for a number 
    of experimental conditions as contained in an avdata_dict (calcs.av_by_cond_in_data_dict) and
    an avfitting_dict (calcs.get_fit_params_from_avdata_dict). Plots points as scatter and fit as
    lines for each condition, with error bars (user specified from columns in avdata_dict, default
    range). If tight_layout=True then figsize will include the legend and figure. If false
    then figsize only refers to the graph and the legend is extra
    """

    fig, ax = plt.subplots(figsize=(fig_size[0],fig_size[1]))
    fig.tight_layout() # confused why I need this twice

    for (condition, averaged_df), (condition2, fit_dict), color \
    in zip(avdata_dict.items(), avfitting_dict.items(), colors):
        x = averaged_df.iloc[:, 0]
        y = averaged_df.iloc[:, 1]
        if error_bars not in averaged_df.columns:
            print("error_bars either not specified or argument is not a column in avdata_dict")
            print("plotting without error bars")
            ax.plot(x, y, marker="o", ls="none", c=color, label=condition)
        else:
            yerr = averaged_df[error_bars]/2 # divide by two as half above and half below scatter point
            ax.errorbar(x, y, yerr, marker="o", ls="none", c=color, label=condition, capsize=3)
        # plot fitting
        maxx, minx = max(x), min(x)
        xnew = np.linspace(minx, maxx, 100) # interpolate the fit equation over 100 points
        popt = fit_dict["popt"]
        ax.plot(xnew, one_phase_decay(np.array(xnew), *popt), c=color)

    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Fraction Folded")
    ax.legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')
    ax.set_ylim(y_limits[0], y_limits[1])
    ax.set_frame_on(True)
    
    if tight_layout:
        fig.tight_layout()

    if save != "": # has user provided a savename
        print(f"Saving as {save}")
        if tight_layout:
            fig.savefig(save, dpi=600, transparent=True)
        else:
            fig.savefig(
                save, 
                dpi=600, 
                transparent=True, 
                bbox_inches='tight' # ensures legend isn't cut off
            )
    
    plt.show()  


def plot_init_rate_fit(init_rate_dict):
    """Plots the linear fit vs data used to calculate it from init_rate_dict generated
    using calculate_init_rate."""
    
    colors = iter([plt.cm.tab10(i) for i in range(20)])
    
    for (reaction_name, fit_dict), color in zip(init_rate_dict.items(), colors):
        x = fit_dict["x"]
        y = fit_dict["y"]
        plt.plot(x,y, marker=".", c=color, label=reaction_name, ls="none")
        # plot fitting
        maxx, minx = max(x), min(x)
        xnew = np.linspace(minx, maxx, 100) # interpolate the fit equation over 100 points
        popt = fit_dict["popt"]
        plt.plot(xnew, linear(np.array(xnew), *popt), c=color)

    plt.legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')
    plt.show()

def make_plot_dict(norm_init_rate_dict):
    """Used during plot_norm_init_rates() func. Removes the reaction_name level from a 
    norm_init_rate_dict. 
    Returns: 
    plot_dict = {
        "<condition>" : np.array([norm_init_rate1, norm_init_rate2]),
        etc.
    }"""

    plot_dict = {}
    for condition, reactions_dict in norm_init_rate_dict.items():
        norm_init_rates = []
        for reaction, norm_init_rate in reactions_dict.items():
            norm_init_rates.append(norm_init_rate) # get all the init rates
        norm_init_rates_array = np.array(norm_init_rates)
        plot_dict[condition] = norm_init_rates_array

    return plot_dict

def plot_norm_init_rates(
    norm_init_rate_dict: dict, 
    y_limits: list=[0,200],
    fig_size: list=[5,6],
    colors: list=[plt.cm.tab20(i) for i in range(20)], 
    save: str=""
    ):
    """plot normalised initial rates as a barchart with individual data points scattered on top.
    Takes initial rates from a norm_init_rate_dict generated by init_rates_as_percent_control()"""

    # Remove the reaction_name level from the dict
    # want "<condition>" : np.array([norm_init_rate1, norm_init_rate2])
    plot_dict = make_plot_dict(norm_init_rate_dict)

    # Plotting
    labels = []
    for names in plot_dict.keys():
        labels.append(names)

    x = range(len(plot_dict.keys()))

    # From inkscape inspection of the original graph
    #colors = ['#000000ff', '#ff0000ff', '#009900fe', '#d4aa00ff', '#0000ffff', '#ff40d9ff', '#9039e6d5', '#777777fa']
    # colors = [plt.cm.tab20(i) for i in range(20)]
    # now defined in func args
    # Create the plot
    # Font settings to match figure
    font = {
            'family' : 'Arial',
            'weight' : 'normal',
            'size' : 7.560
            }
    plt.rc('font', **font)
    
    # Turn off full bounding box
    bounding_box = {
                    'bottom':True,
                    'left':True,
                    'right':False,
                    'top':False
                    }
    plt.rc('axes.spines', **bounding_box)
    
    plt.rcParams['figure.autolayout'] = True
    
    
    fig, ax = plt.subplots(figsize=(fig_size[0],fig_size[1]))
    #fig, ax = plt.subplots()
    plt.tight_layout()

    # Janky sns.swarmplot
    # Create list and fill with values to plot against each other
    # Need num x coords to match num y coords
    x_list_GLOBAL = []
    y_list_GLOBAL = []
    for i, rates in zip(range(len(plot_dict.keys())), plot_dict.values()):
        x_list_GLOBAL += [x[i]]*len(rates)
        y_list_GLOBAL += list(rates)

    ax = sns.swarmplot(x=x_list_GLOBAL, y=y_list_GLOBAL, color='grey', size=2, marker='o')

    #ax = sns.swarmplot(x=x_list_GLOBAL, y=y_list_GLOBAL, color='grey', edgecolor='grey', size=2, marker='o', linewidth=1)


    # matplotlib bar chart
    bar_heights = [statistics.mean(rates) for rates in plot_dict.values()]

    ax.bar(x,
        height=bar_heights,
        #width=w,    # bar width
        linewidth=0.8,
        tick_label=labels,
        color=colors,  # face color transparent
        edgecolor='black',
        zorder=0
        )

    plt.ylabel("Normalised initial folding rate \n (% of mean WT BAM)")
    plt.xticks(rotation='vertical')
    plt.ylim(y_limits[0], y_limits[1])

    plt.figure(num=1, figsize=(2.313,2.313))

    if save != "":
        print(f"Saving as {save}")
        plt.savefig(save, dpi=600, transparent=True)
    plt.show()

