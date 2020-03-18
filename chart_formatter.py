from matplotlib import ticker, dates
import datetime
from matplotlib.dates import num2date, SEC_PER_DAY

import numpy as np


class DateFormatter(ticker.Formatter):

    def __init__(self, start_date):
        self.start_date = start_date

    def __call__(self, x, pos=None):
        day = (num2date(x).date() - self.start_date).total_seconds() / SEC_PER_DAY
        if day % 14 == 0:
            return int(day)
        return None

    def format_data(self, value):
        return num2date(value).strftime('%Y-%m-%d')


class DatePositionFormatter(ticker.Formatter):

    def __call__(self, x, pos=None):
        if pos % 2 == 0:
            return pos * 7
        return None

    def format_data(self, value):
        return num2date(value).strftime('%Y-%m-%d')


class DataFormatter(ticker.Formatter):

    def __call__(self, x, pos=None):

        if x % 1 == 0:
            return f'{x:.0f}'
        elif x == 0.0005:
            return f'{0:.0f}'
        return x

    def format_data(self, value):
        return f'{value:0.3f}'


class TopFormatter(ticker.Formatter):

    def __call__(self, x, pos=None):
        if pos % 4 == 0:
            return pos
        return None

    def format_data(self, value):
        return num2date(value).strftime('%Y-%m-%d')
