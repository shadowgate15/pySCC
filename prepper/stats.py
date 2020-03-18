import pandas as pd
import numpy as np
import re
from scipy import stats as sci_stats
from sklearn.linear_model import LinearRegression


def stats(data, inplace=False):
    """
    create all within condition statistics and between condition statistics and
     return in a single DataFrame

    :param data: intial data that stats need to be made for
    :type data: pd.DataFrame

    :param inplace: whether to do the transformation on original DataFrame or return DataFrame
    :type inplace: bool

    :return data: final DataFrame with all stats
    :rtype data: pd.DataFrame
    """
    # work with copy of DataFrame?
    if not inplace:
        data = data.copy()

    data = data.groupby('phase').apply(within_condition_stats)

    ###########################
    # Between Condition Stats #
    ###########################

    # filter columns to iterate over only columns containing cel_value
    r = re.compile('cel_value_*')
    for col in filter(r.match, data.columns):
        set = re.sub('cel_value_', '', col)
        for previous, current in zip(pd.unique(data[col])[::1], pd.unique(data[col])[1::1]):
            if previous is np.nan or current is np.nan:
                continue
            # preparing data
            previous_sign = previous[:1]
            current_sign = current[:1]
            previous_value = float(previous[1:])
            current_value = float(current[1:])

            # check for direction and calculate multiplier
            if previous_sign == current_sign:
                if previous_value == current_value:
                    data.loc[
                        data[col] == current, f'cel_multiplier_{set}'] = f'\xF7{previous_value/current_value:.2f}'
                else:
                    data.loc[
                        data[col] == current, f'cel_multiplier_{set}'] = f'\xD7{current_value / previous_value:.2f}'
            else:
                val = previous_value * current_value
                if previous_value == '\xF7':
                    data.loc[
                        data[col] == current, f'cel_multiplier_{set}'] = f'\xD7{val:.2f}'
                else:
                    data.loc[
                        data[col] == current, f'cel_multiplier_{set}'] = f'\xF7{val:.2f}'

    # return DataFrame?
    if not inplace:
        return data


def within_condition_stats(data):
    ##########################
    # Within Condition Stats #
    ##########################

    # filter columns to iterate over only columns containing data
    r = re.compile('data_*')
    for col in filter(r.match, data.columns):
        set = re.sub('data_', '', col)

        ###
        # calculate celeration line
        ###

        # z-score to remove outliers
        z = abs(sci_stats.zscore(np.log10(data[col].values)))

        # prepare data for linear regression
        Y = data[col].values[z < 3]
        Y = np.log10(Y.reshape(-1, 1))
        X = np.arange(start=0, stop=len(Y), step=1).reshape(-1, 1)

        # linear regression
        regressor = LinearRegression()
        regressor.fit(X, Y)

        predict = regressor.predict(X)

        diff = Y - predict

        # get celeration line that matches data
        X = np.arange(start=0, stop=len(data[col]), step=1).reshape(-1, 1)
        celeration = regressor.predict(X)

        ###
        # calculate bounce lines
        ###

        # get up bounce line
        up_bounce = predict + np.amax(diff)

        # get down bounce line
        down_bounce = predict + np.amin(diff)

        ###
        # calculate cel_val
        ###
        slope = 10 ** (7 * abs(regressor.coef_[0][0]))
        if celeration[0] < celeration[-1]:
            cel_val = f'\xD7{slope:.2f}'
        else:
            cel_val = f'\xF7{slope:.2f}'

        ###
        # calculate bounce_val
        ###
        bounce_val = f'\xD7{(up_bounce[0][0] / down_bounce[0][0]):.2f}'

        ###
        # convert to coordinates that match data
        ###
        celeration = 10 ** celeration
        up_bounce = 10 ** up_bounce
        down_bounce = 10 ** down_bounce

        data[f'celeration_{set}'] = celeration
        data[f'cel_value_{set}'] = cel_val
        data[f'up_bounce_{set}'] = up_bounce
        data[f'down_bounce_{set}'] = down_bounce
        data[f'bounce_value_{set}'] = bounce_val

    return data
