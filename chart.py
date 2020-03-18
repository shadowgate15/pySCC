import datetime

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.dates as mdates
import matplotlib.transforms as mtransforms
from matplotlib.dates import SU
from chart_formatter import DataFormatter, DatePositionFormatter, TopFormatter
import numpy as np
import pandas as pd


def plot(data, cel_visible=True, bounce_visible=False):
    start_date = data.index[0] - datetime.timedelta(days=data.index[0].weekday() + 1)
    ticklabelpad = mpl.rcParams['xtick.major.pad']

    fig, ax_data = plt.subplots(figsize=(11, 9))
    ax_counting = ax_data.twinx()

    # plot data
    g = data.groupby([data.index, 'phase'])
    g['data_decel'].sum().unstack().plot(ax=ax_data, linestyle='None',
                                         marker='x', color='red')

    if cel_visible or bounce_visible:
        g = data.groupby('phase')
        cel = ((pd.concat([g.head(1), g.tail(1)]))
               .sort_index()
               .groupby('phase'))
    # plot celeration
    if cel_visible:
        cel.plot(y='celeration_decel', ax=ax_data,
                 color='black', alpha=0.75)
    # plot bounce
    if bounce_visible:
        cel.plot(y=['up_bounce_decel', 'down_bounce_decel'], ax=ax_data,
                 color='black', alpha=0.5)

    data.plot(y='counting', ax=ax_counting,
              color='black', marker='_',
              linestyle='None', legend=None)

    # TODO add phase line annotations to graph

    ax_data.grid(b=True, which='both', axis='both')  # make grid visible
    ax_data.set(xlabel='SUCCESSIVE CALENDAR DAYS',
                ylabel='COUNT PER MINUTE',
                yscale='log',
                ylim=(0.0005, 1000),
                zorder=1.0,
                )  # set left y axis

    # left y axis
    ax_data.yaxis.label.set_color('#3498db')
    ax_data.yaxis.set_major_locator(ticker.LogLocator(subs=(1.0, 0.5,)))  # set locator
    ax_data.yaxis.set_major_formatter(DataFormatter())  # set formatter
    ax_data.tick_params(axis='y',
                        which='major',
                        grid_linewidth=0.5,
                        grid_color='#3498db',
                        colors='#3498db')
    ax_data.tick_params(axis='y',
                        which='minor',
                        grid_linewidth=0.25,
                        grid_color='#3498db',
                        colors='#3498db')
    i = 0
    for tick in ax_data.yaxis.get_major_ticks():
        if i % 2 != 0:
            tick.label.set_size('small')
        i += 1

    # bottom x axis
    ax_data.xaxis.label.set_color('#3498db')
    ax_data.xaxis.label.set_size('large')
    ax_data.set_xlim(np.datetime64(start_date),
                     np.datetime64(start_date + datetime.timedelta(days=140)))

    ax_data.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=SU))
    ax_data.xaxis.set_minor_locator(mdates.DayLocator())

    ax_data.xaxis.set_major_formatter(DatePositionFormatter())

    ax_data.tick_params(axis='x', which='major',
                        labelsize='large',
                        labelrotation=0.,
                        grid_linewidth=0.5,
                        grid_color='#3498db',
                        colors='#3498db')
    ax_data.tick_params(axis='x',
                        which='minor',
                        grid_linewidth=0.25,
                        grid_color='#3498db',
                        colors='#3498db')

    for tick in ax_data.xaxis.get_major_ticks():
        plt.setp(tick.label, ha='center')

    # right y axis
    ax_counting.set(yscale='log',
                    ylim=(0.0005, 1000),
                    zorder=2.0)

    ax_counting.yaxis.set_major_locator(
        ticker.FixedLocator([6, 4, 3, 2, 1, 0.5, 0.2, 0.1, 0.05, 0.02, 0.01, 0.005, 0.002, 0.001]))
    ax_counting.yaxis.set_minor_locator(ticker.FixedLocator([(1 / 60),
                                                             (1 / (60 * 2)),
                                                             (1 / (60 * 4)),
                                                             (1 / (60 * 8)),
                                                             (1 / (60 * 16)),
                                                             (1 / (60 * 24))]))

    major_labels = {6: '10" sec',
                    4: '15"',
                    3: '20"',
                    2: '30"',
                    1: "1' min",
                    0.5: "2'",
                    0.2: "5'",
                    0.1: "10'",
                    0.05: "20'",
                    0.02: "50'",
                    0.01: "100'",
                    0.005: "200'",
                    0.002: "500'",
                    0.001: "1000'"}
    minor_labels = {(1 / 60): '1\xB0 hr',
                    (1 / (60 * 2)): '2\xB0',
                    (1 / (60 * 4)): '4\xB0',
                    (1 / (60 * 8)): '8\xB0',
                    (1 / (60 * 16)): '16\xB0',
                    (1 / (60 * 24)): '24\xB0'}
    ax_counting.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: major_labels.get(x)))
    ax_counting.yaxis.set_minor_formatter(ticker.FuncFormatter(lambda x, pos: minor_labels.get(x)))

    ax_counting.tick_params(axis='y',
                            which='major',
                            labelsize='small',
                            colors='#3498db')
    ax_counting.tick_params(axis='y',
                            which='minor',
                            labelsize='small',
                            colors='#3498db')

    offset = mtransforms.ScaledTranslation(35 / 72., 0 / 72., fig.dpi_scale_trans)
    for element in ax_counting.yaxis.get_minorticklabels() + ax_counting.yaxis.get_minorticklines():
        element.set_transform(element.get_transform() + offset)

    fontproperties = ax_counting.yaxis.get_label().get_fontproperties()
    label = ax_counting.get_ymajorticklabels()[0]
    ax_counting.annotate('COUNTING TIMES',
                         xy=(0., 0.), xycoords=label,  # 'axes fraction',
                         xytext=(ticklabelpad, 30.), textcoords='offset points',
                         color='#3498db', size='small',
                         va='bottom', rotation=90.,
                         fontproperties=fontproperties)

    # top x axis
    ax_top = ax_data.twiny()
    ax_top.set_zorder(3.0)
    ax_top.set_xlim(np.datetime64(start_date),
                    np.datetime64(start_date + datetime.timedelta(days=140)))

    ax_top.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=SU))
    ax_top.xaxis.set_minor_locator(mdates.DayLocator())

    ax_top.xaxis.set_major_formatter(TopFormatter())

    ax_top.tick_params(axis='x', which='major',
                       labelsize='large',
                       colors='#3498db')
    ax_top.tick_params(axis='x',
                       which='minor',
                       length=0.,
                       colors='#3498db')

    fontproperties = ax_top.xaxis.get_label().get_fontproperties()
    for pos, x in enumerate(ax_top.get_xticks()):
        if pos % 4 == 0:
            if pos == 4:
                ax_top.annotate('SUCCESSIVE',
                                xy=(x, 1), xycoords=('data', 'axes fraction'),
                                xytext=(25, ticklabelpad + 10), textcoords='offset points',
                                va='center', size='large', color='#3498db',
                                fontproperties=fontproperties)
            elif pos == 8:
                ax_top.annotate('CALENDAR',
                                xy=(x, 1), xycoords=('data', 'axes fraction'),
                                xytext=(25, ticklabelpad + 10), textcoords='offset points',
                                va='center', size='large', color='#3498db',
                                fontproperties=fontproperties)
            elif pos == 12:
                ax_top.annotate('WEEKS',
                                xy=(x, 1), xycoords=('data', 'axes fraction'),
                                xytext=(25, ticklabelpad + 10), textcoords='offset points',
                                va='center', size='large', color='#3498db',
                                fontproperties=fontproperties)

            an = ax_top.annotate('',
                                 xy=(x, 1), xycoords=('data', 'axes fraction'),
                                 xytext=(ticklabelpad + 60, 40), textcoords='offset points',
                                 arrowprops=dict(arrowstyle='-', shrinkB=25,
                                                 color='#3498db',
                                                 connectionstyle="angle,angleA=0,angleB=90"), )
            ax_top.annotate(mdates.num2date(x).strftime('%m/%d/%Y'),
                            xy=(1., 1.), xycoords=an,
                            xytext=(-ticklabelpad, 1.), textcoords='offset points',
                            ha='right', va='bottom', size='medium',
                            fontproperties=fontproperties)

    # set frame color
    for ax, color in zip([ax_data, ax_counting, ax_top], ['#3498db', '#3498db', '#3498db', '#3498db']):
        plt.setp(ax.spines.values(), color=color)
        plt.setp([ax.get_xticklines(), ax.get_yticklines()], color=color)

    plt.show()
