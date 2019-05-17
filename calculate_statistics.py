import numpy as np
import pandas as pd
from datetime import datetime


def calculate_snowdepth(filename):
    data = pd.read_csv(filename)

    ids = data['identifier'].unique()

    # initialize array
    return_df = pd.DataFrame(columns=['identifier', 'lat', 'lon', 'region', 'snow_weeks', 'snow_mean'])

    for identifier in ids:
        data_temp = data.loc[data['identifier'] == identifier]
        dt_obj = pd.Series([datetime.strptime(x, '%Y-%m-%d') for x in data_temp['time']], index=data_temp.index)
        data_temp.insert(5, 'datetime', dt_obj)
        snow_weeks = np.array([np.mean(data_temp.loc[[x.isocalendar()[1] == y for x in data_temp['datetime']]]['value'])
                               for y in np.arange(1, 52)])
        snow_all = np.array(data_temp['value'])
        return_df = return_df.append(pd.DataFrame({"identifier": [identifier],
                                        "lat": [data_temp.iloc[0].lat],
                                        "lon": [data_temp.iloc[0].lon],
                                        "region": [data_temp.iloc[0].region],
                                        "snow_weeks": [len(snow_weeks[snow_weeks > 10])],
                                        "snow_mean": [np.mean(snow_all[snow_all > 0])]}),
                                     ignore_index=True)
    return return_df


""" if __name__ == '__main__':
    a = calculate_snowdepth('raw_data/data_2000.csv')
    print(a) """
