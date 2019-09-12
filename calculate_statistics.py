import numpy as np
import pandas as pd
from datetime import datetime
import configparser
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
import re
import os

CONFIG_FILE = 'configs.ini'

def clean_tags(string_to_clean):
  tags_regexp = re.compile('<.*?>')
  str_tags_removed = re.sub(tags_regexp, '', string_to_clean)
  return str_tags_removed

def load_regions():
    """ Loads region polygons from Finland
        data source: https://github.com/teelmo/geodata """
    config_reader = configparser.ConfigParser()
    config_reader.read(CONFIG_FILE)
    data = pd.read_csv(config_reader["regionData"]["source"])
    polygons = []
    for row in zip(data.Maakunta, data.Maaku_ni1, data.geometry):
        geometry = clean_tags(row[2])
        points_list = [points.split(',') for points in geometry.split(' ')]
        polygons.append([row[0], row[1], Polygon([[float(point) for point in points] for points in points_list])])
    return polygons


def calculate_region_id(regions, coordinates):
    """
    This functions maps the real regions identifiers to region_id used in the data
    input:
    regions = regions loaded with load_regions() function
    coordinates = coordinates of the station in (lon, lat)

    output:
    0 = not in any area below
    1 = Lappi, pohjois-pohjanmaa
    2 = pohjois-pohjanmaa keski-pohjanmaa, pohjanmaa, etela-pohjanmaa
    3 = kainuu, pohjois-karjala, pohjois-savo
    4 = etela-savo, keski-suomi, paijat-hame
    5 = etela-karjala, kymenlaakso, uusisuomi, varsinaissuomi, satakunta
    """

    point = Point(coordinates)
    return_map_area = 0

    regions_to_map_areas = [[19, 17], [16, 15, 14], [18, 11, 12],[10, 13, 7], [9, 8, 1, 2, 4]]

    for region in regions:
        if region[2].contains(point):
            for index, map_area in enumerate(regions_to_map_areas):
                if map_area.count(region[0]) == 1:
                    return_map_area = index+1

    return return_map_area


def calculate_snowdepth(filename):
    data = pd.read_csv(filename)

    ids = data['identifier'].unique()

    # initialize array
    return_df = pd.DataFrame(columns=['identifier', 'lat', 'lon', 'region', 'region_id', 'snow_weeks', 'snow_mean'])
    # load region data

    regions = load_regions()
    for identifier in ids:
        data_temp = data.loc[data['identifier'] == identifier]
        dt_obj = pd.Series([datetime.strptime(x, '%Y-%m-%d') for x in data_temp['time']], index=data_temp.index)
        data_temp.insert(5, 'datetime', dt_obj)
        snow_weeks = np.array([np.mean(data_temp.loc[[x.isocalendar()[1] == y for x in data_temp['datetime']]]['value'])
                               for y in np.arange(1, 52)])
        snow_all = np.array(data_temp['value'])
        region_id = calculate_region_id(regions, [data_temp.iloc[0].lon, data_temp.iloc[0].lat])
        return_df = return_df.append(pd.DataFrame({"identifier": [identifier],
                                        "lat": [data_temp.iloc[0].lat],
                                        "lon": [data_temp.iloc[0].lon],
                                        "region": [data_temp.iloc[0].region],
                                        "region_id": [region_id],
                                        "snow_weeks": [len(snow_weeks[snow_weeks > 10])],
                                        "snow_mean": [np.mean(snow_all[snow_all > 0])]}),
                                     ignore_index=True)
    return return_df

def create_statistics_data(dirname, outputdirname):
    """Creates the statistics data using raw data from dirname"""

    filenames = os.listdir(dirname)

    for filename in filenames:
        data = calculate_snowdepth(dirname + filename)
        data.to_csv(outputdirname+filename)

def create_region_id_median_time_series():
    years = np.arange(1958, 2019)
    snow_median_by_region = pd.DataFrame(columns=['year', 'region_id', 'snow_weeks_median'])

    for year in years:
        filename = 'test_data/data_' + str(year) + '.csv'
        data = pd.read_csv(filename)
        for r_id in np.arange(1, 6):
            chosen_data = data.loc[data['region_id'] == r_id]
            snow_weeks_median = np.median(chosen_data['snow_weeks'])
            snow_median_by_region = snow_median_by_region.append(
                pd.DataFrame({"year": year, "region_id": r_id, "snow_weeks_median": snow_weeks_median},
                             index=[0]),
                ignore_index=True)
    snow_median_by_region.to_csv('snow_median_by_region.csv')








""" if __name__ == '__main__':
    a = calculate_snowdepth('raw_data/data_2000.csv')
    print(a) """
