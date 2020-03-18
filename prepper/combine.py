import pandas as pd


def combine_cr(raw_timesheets, raw_data):
    """
    data prepper for for CentralReach count only data

    :param raw_timesheets: timesheets from CR that contain the date range of interest and only direct therapy hours
    :type raw_timesheets: pd.Dataframe

    :param raw_data: raw_data from target - must be count only data
    :type raw_data: pd.Dataframe

    :return data: Dataframe indexed by date, columns: data (count/minute), counting_time, phase
    :rtype data: pd.Dataframe
    """

    # TODO assume zero for no data

    ##############
    # Timesheets #
    ##############

    # filter to only the rows we need
    timesheets = raw_timesheets[['DateOfService', 'TimeWorkedInMins']].rename(
        columns={'DateOfService': 'date', 'TimeWorkedInMins': 'counting_time'}
    )

    drop_time(timesheets)   # drop time from date column

    timesheets = timesheets.groupby(['date']).sum()     # combine all counting times by date

    timesheets.date = pd.to_datetime(timesheets.index,
                                     infer_datetime_format=True)    # convert to datetime
    timesheets.sort_index(inplace=True)
    # print(f'timesheets:\n{timesheets}')

    ################
    # Phase Change #
    ################

    # filter for phase change
    phase_change = raw_data[raw_data.Trial.isna()]
    phase_change.reset_index(inplace=True)
    phase_change = phase_change.iloc[0:phase_change[phase_change.Type == 'event'].index[0]]
    phase_change = phase_change[['Data Date', 'Break Event Name']].rename(
        columns={'Data Date': 'date', 'Break Event Name': 'phase'}
    )

    drop_time(phase_change)     # drop time from date column
    phase_change.set_index('date', inplace=True)    # set index to date
    phase_change.index = pd.to_datetime(phase_change.index,
                                        infer_datetime_format=True)     # convert to datetime
    phase_change.sort_index(inplace=True)
    # print(f'phase_change:\n{phase_change}')

    ####################
    # Convert Raw Data #
    ####################

    # filter for only data
    data = raw_data[raw_data.Trial == 'Summary'][['Data Date', 'Data']].rename(
        columns={'Data Date': 'date', 'Data': 'data_decel'}
    )

    drop_time(data)     # drop time from date column
    data = data.groupby(['date']).sum()     # combine data by date
    data.index = pd.to_datetime(data.index,
                                infer_datetime_format=True)     # convert to datetime
    data.sort_index(inplace=True)
    # print(f'data:\n{data}')

    ###############
    # Combine all #
    ###############

    # merge counting times and data
    data = data.merge(timesheets,
                      left_index=True,
                      right_index=True)
    # print(f'data & timesheets:\n{data}')

    # put in phase column
    idx = pd.date_range(data.index[0], data.index[-1])
    phase_change = phase_change.reindex(idx, method='pad', fill_value='intervention')

    data = data.merge(phase_change, how='right', left_index=True, right_index=True)
    # print(f'data+timesheets & phase_change:\n{data}')

    #############################
    # Convert data to count/min #
    #############################
    data['data_decel'] = data.apply(lambda x: x['data_decel']/x.counting_time, axis=1)
    data['counting'] = data.apply(lambda x: 1/x.counting_time, axis=1)

    return data.dropna()


def drop_time(df):
    df.date = df.date.str.split(" ", n=1, expand=True)[0]
    return df
