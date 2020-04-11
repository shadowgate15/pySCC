import datetime

import matplotlib as mpl
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.transforms as mtransforms
import numpy as np
import pandas as pd
from matplotlib.dates import SU
import re

from chart_formatter import DataFormatter, DatePositionFormatter, TopFormatter


class SCC:

    def __init__(self, data, colors=dict(), markers=dict(),
                 phase_lines=dict(),
                 figsize=(11, 9), ylim=(0.0005, 1000)):   # FEATURE GH-5 chart based on ratio not size in inches
        """

        :param data: DataFrame containing the data to be charted with a DateTimeIndex.
        :type data: pd.DataFrame

        :param colors: Column to color pairs for plotting.
        :type colors: dict

        :param phase_lines: Data to name for putting in phase_lines
        :type phase_lines: dict

        :param markers: Column to marker pairs for plotting.
        :type markers: dict

        :param figsize: Size of the figure
        :type figsize: tuple

        :param ylim: size of the limit on the y-axis.
        :type ylim: tuple
        """
        self.data = data
        self.colors = colors
        self.markers = markers
        self.phase_lines = phase_lines
        # setup figure and axes
        self.fig, self.ax_data = plt.subplots(figsize=figsize)
        self.ax_counting = self.ax_data.twinx()
        self.ax_top = self.ax_data.twiny()
        # figure attributes
        self.ylim = ylim

    @property
    def data(self):
        return self.__data

    @data.setter
    def data(self, df):
        # errors with df
        if not isinstance(df, pd.DataFrame):
            raise TypeError('SCC.data must be a pandas.DataFrame')
        elif not isinstance(df.index, pd.DatetimeIndex):
            raise TypeError('SCC.data.index must be a pandas.DataTimeIndex')
        elif df.eq(0).any().any():
            raise ValueError('SCC.data cannot contain zeros.')

        self.__data = df.resample('D').sum().replace(0.0, np.nan)


    @property
    def colors(self):
        return self.__colors

    @colors.setter
    def colors(self, value):
        """
        colors will be used to set the color per column. Default will be black.
        :param value: Column to color pairs for plotting.
        :type value: dict
        """
        diff = [column for column in self.data.columns if column not in value.keys()]
        for item in diff:
            value[item] = 'black'

        self.__colors = value

    @property
    def markers(self):
        return self.__markers

    @markers.setter
    def markers(self, value):
        """
        markers will be used to set the marker per column. Default will be a dot.

        Must be either 'accel' or 'decel'. Any other will raise ValueError.
        :param value: Column to marker pairs for plotting.
        :type value: dict
        """
        for k, v in value.items():
            if v == 'accel':
                value[k] = '.'
            elif v == 'decel':
                value[k] = 'x'
            else:
                raise ValueError('Column must be either a(n) (accel)eration target or (decel)eration target.')
        diff = [column for column in self.data.columns if column not in value.keys()]
        for item in diff:
            value[item] = '.'

        self.__markers = value

    def set_data(self, data, colors, markers):
        self.data = data
        self.colors = colors
        self.markers = markers

    def plot(self):
        # plot data
        for col in self.data:
            if col == 'counting':
                self.data.plot(y=col, ax=self.ax_counting,
                               color=self.colors[col], marker='_',
                               linestyle='None', legend=None)
            else:
                self.data.plot(y=col, ax=self.ax_data,
                               color=self.colors[col], marker=self.markers[col],
                               linestyle='-', linewidth='1')

        # TODO plot celeration line

        # TODO add phase change lines
        max = self.data.max().max()
        min = self.data.min().min()

        fontproperties = self.ax_data.xaxis.get_label().get_fontproperties()
        for date, label in self.phase_lines.items():
            # date = mdates.datestr2num(date)
            self.ax_data.annotate(label,
                                  xy=(date, min), xycoords='data',
                                  xytext=(date, max), textcoords='data', ha='left',
                                  arrowprops=dict(arrowstyle='-', connectionstyle='angle'))

        self.__format_fig()
        plt.show()

    def __format_fig(self):
        # set start date of chart
        start_date = self.data.index[0] - datetime.timedelta(days=self.data.index[0].weekday() + 1)
        ticklabelpad = mpl.rcParams['xtick.major.pad']

        # set overall variables
        self.ax_data.grid(b=True, which='both', axis='both')  # make grid visible
        self.ax_data.set(xlabel='SUCCESSIVE CALENDAR DAYS',
                         ylabel='COUNT PER MINUTE',
                         yscale='log',
                         ylim=self.ylim,
                         zorder=1.0)  # set left y axis

        # left y axis
        self.ax_data.yaxis.label.set_color('#3498db')
        self.ax_data.yaxis.set_major_locator(ticker.LogLocator(subs=(1.0, 0.5,)))  # set locator
        self.ax_data.yaxis.set_major_formatter(DataFormatter())  # set formatter
        self.ax_data.tick_params(axis='y',
                                 which='major',
                                 grid_linewidth=0.5,
                                 grid_color='#3498db',
                                 colors='#3498db')
        self.ax_data.tick_params(axis='y',
                                 which='minor',
                                 grid_linewidth=0.25,
                                 grid_color='#3498db',
                                 colors='#3498db')

        # bottom x axis
        self.ax_data.xaxis.label.set_color('#3498db')
        self.ax_data.xaxis.label.set_size('large')
        self.ax_data.set_xlim(np.datetime64(start_date),
                              np.datetime64(start_date + datetime.timedelta(days=140)))     # FEATURE GH-4 Scaling y-axis

        # FEATURE GH-6 different types of charts
        self.ax_data.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=SU))
        self.ax_data.xaxis.set_minor_locator(mdates.DayLocator())

        self.ax_data.xaxis.set_major_formatter(DatePositionFormatter())

        self.ax_data.tick_params(axis='x', which='major',
                                 labelsize='large',
                                 labelrotation=0.,
                                 grid_linewidth=0.5,
                                 grid_color='#3498db',
                                 colors='#3498db')
        self.ax_data.tick_params(axis='x',
                                 which='minor',
                                 grid_linewidth=0.25,
                                 grid_color='#3498db',
                                 colors='#3498db')

        for tick in self.ax_data.xaxis.get_major_ticks():
            plt.setp(tick.label, ha='center')

        # right y axis
        self.ax_counting.set(yscale='log',
                             ylim=self.ylim,
                             zorder=2.0)

        self.ax_counting.yaxis.set_major_locator(
            ticker.FixedLocator([6, 4, 3, 2, 1, 0.5, 0.2, 0.1, 0.05, 0.02, 0.01, 0.005, 0.002, 0.001]))
        self.ax_counting.yaxis.set_minor_locator(ticker.FixedLocator([(1 / 60),
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
        self.ax_counting.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: major_labels.get(x)))
        self.ax_counting.yaxis.set_minor_formatter(ticker.FuncFormatter(lambda x, pos: minor_labels.get(x)))

        self.ax_counting.tick_params(axis='y',
                                     which='major',
                                     labelsize='small',
                                     colors='#3498db')
        self.ax_counting.tick_params(axis='y',
                                     which='minor',
                                     labelsize='small',
                                     colors='#3498db')

        offset = mtransforms.ScaledTranslation(35 / 72., 0 / 72., self.fig.dpi_scale_trans)
        for element in self.ax_counting.yaxis.get_minorticklabels() + self.ax_counting.yaxis.get_minorticklines():
            element.set_transform(element.get_transform() + offset)

        fontproperties = self.ax_counting.yaxis.get_label().get_fontproperties()
        label = self.ax_counting.get_ymajorticklabels()[0]
        self.ax_counting.annotate('COUNTING TIMES',
                                  xy=(0., 0.), xycoords=label,  # 'axes fraction',
                                  xytext=(ticklabelpad, 30.), textcoords='offset points',
                                  color='#3498db', size='small',
                                  va='bottom', rotation=90.,
                                  fontproperties=fontproperties)

        # top x axis
        self.ax_top.set_zorder(3.0)
        self.ax_top.set_xlim(np.datetime64(start_date),
                             np.datetime64(start_date + datetime.timedelta(days=140)))

        self.ax_top.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=SU))
        self.ax_top.xaxis.set_minor_locator(mdates.DayLocator())

        self.ax_top.xaxis.set_major_formatter(TopFormatter())

        self.ax_top.tick_params(axis='x', which='major',
                                labelsize='large',
                                colors='#3498db')
        self.ax_top.tick_params(axis='x',
                                which='minor',
                                length=0.,
                                colors='#3498db')

        fontproperties = self.ax_top.xaxis.get_label().get_fontproperties()
        for pos, x in enumerate(self.ax_top.get_xticks()):
            if pos % 4 == 0:
                if pos == 4:
                    self.ax_top.annotate('SUCCESSIVE',
                                         xy=(x, 1), xycoords=('data', 'axes fraction'),
                                         xytext=(25, ticklabelpad + 10), textcoords='offset points',
                                         va='center', size='large', color='#3498db',
                                         fontproperties=fontproperties)
                elif pos == 8:
                    self.ax_top.annotate('CALENDAR',
                                         xy=(x, 1), xycoords=('data', 'axes fraction'),
                                         xytext=(25, ticklabelpad + 10), textcoords='offset points',
                                         va='center', size='large', color='#3498db',
                                         fontproperties=fontproperties)
                elif pos == 12:
                    self.ax_top.annotate('WEEKS',
                                         xy=(x, 1), xycoords=('data', 'axes fraction'),
                                         xytext=(25, ticklabelpad + 10), textcoords='offset points',
                                         va='center', size='large', color='#3498db',
                                         fontproperties=fontproperties)

                an = self.ax_top.annotate('',
                                          xy=(x, 1), xycoords=('data', 'axes fraction'),
                                          xytext=(ticklabelpad + 60, 40), textcoords='offset points',
                                          arrowprops=dict(arrowstyle='-', shrinkB=25,
                                                          color='#3498db',
                                                          connectionstyle="angle,angleA=0,angleB=90"), )
                self.ax_top.annotate(mdates.num2date(x).strftime('%m/%d/%Y'),
                                     xy=(1., 1.), xycoords=an,
                                     xytext=(-ticklabelpad, 1.), textcoords='offset points',
                                     ha='right', va='bottom', size='medium',
                                     fontproperties=fontproperties)

        # set frame color
        for ax, color in zip([self.ax_data, self.ax_counting, self.ax_top], ['#3498db', '#3498db', '#3498db', '#3498db']):
            plt.setp(ax.spines.values(), color=color)
            plt.setp([ax.get_xticklines(), ax.get_yticklines()], color=color)
