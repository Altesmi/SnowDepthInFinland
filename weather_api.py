import configparser
import datetime
import time
from collections import OrderedDict
from collections import namedtuple
from time import mktime

import xmltodict
from requests import request

config = configparser.ConfigParser()
config.read('configs.ini')

weather = namedtuple("Weather", ("rain_amount_night low_temp_morning low_temp_day type"))

apikey = config["fmi"]["apikey"]


def fmi_forecast(time_stamp, location="helsinki"):
    if isinstance(time_stamp, time.struct_time):
        time_stamp = datetime.datetime.fromtimestamp(mktime(time_stamp))

    query = "http://data.fmi.fi/fmi-apikey/{apikey}/wfs".format(apikey=apikey)
    params = {
        "request": "getFeature",
        "storedquery_id": "fmi::forecast::hirlam::surface::point::multipointcoverage",
        "place": location
    }
    response = request(url=query, params=params, method="get")
    xml_dict = xmltodict.parse(response.text)
    points_string = xml_dict["wfs:FeatureCollection"]["wfs:member"]["omso:GridSeriesObservation"]["om:result"]["gmlcov:MultiPointCoverage"]["gml:domainSet"]["gmlcov:SimpleMultiPoint"]["gmlcov:positions"]
    data_string = xml_dict["wfs:FeatureCollection"]["wfs:member"]["omso:GridSeriesObservation"]["om:result"]["gmlcov:MultiPointCoverage"]["gml:rangeSet"]["gml:DataBlock"]["gml:doubleOrNilReasonTupleList"]
    field_names_dict = xml_dict["wfs:FeatureCollection"]["wfs:member"]["omso:GridSeriesObservation"]["om:result"]["gmlcov:MultiPointCoverage"]["gmlcov:rangeType"]["swe:DataRecord"]["swe:field"]
    points = points_string.split("\n")
    data = data_string.split("\n")

    field_names = list()
    for _fn in field_names_dict:
        field_names.append(_fn["@name"])

    morning_temp = None
    start_time = None
    coldest = 99999

    for point, _data in OrderedDict(zip(points, data)).items():
        this_time = point.strip().split()[2]
        dtm = datetime.datetime.fromtimestamp(int(this_time))


        true_data = dict(zip(field_names, _data.strip().split()))

        temp = true_data["Temperature"]
        rain1 = true_data["Precipitation1h"]
        rain2 = true_data["PrecipitationAmount"]

        if dtm > time_stamp and not morning_temp:
            morning_temp = float(temp)
            morning_time = dtm
            start_time = dtm
            rain_amount_night = float(rain2)

        if start_time:
            if start_time + datetime.timedelta(hours=18) > dtm:
                if coldest > float(temp):
                    coldest = float(temp)
                    coldest_time = dtm


    print("morning temp: ", morning_time.strftime('%Y-%m-%d %H:%M:%S'), morning_temp)
    print("coldest temp: ", coldest_time.strftime('%Y-%m-%d %H:%M:%S'), coldest)

    low_temp_morning = 0
    low_temp_day = 0
    rain_amount_night = 0
    return weather(
        low_temp_morning=morning_temp,
        low_temp_day=coldest,
        rain_amount_night=rain_amount_night,
        type="normal"
    )

if __name__ == "__main__":
    get_weather_from_ilmatieteenlaitos(datetime.datetime.today() + datetime.timedelta(hours=12))
