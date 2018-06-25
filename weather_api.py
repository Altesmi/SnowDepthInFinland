import configparser
import logging
from collections import OrderedDict
from datetime import datetime
from typing import Iterable, Dict

from dataclasses import dataclass
from lxml import etree
from requests import request, models
from requests.exceptions import RequestException

from timed_cache import timed_cache

CONFIG_FILE = 'configs.ini'
FMI_URL = "http://data.fmi.fi/fmi-apikey/{apikey}/wfs"
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


@dataclass
class WeatherPoint(object):
    lat: float
    lon: float
    time: datetime

    temp: float
    pressure: float
    humidity: float
    dew_point: float

    precipitation_1h: float
    precipitation_total: float

    wind_dir: float
    wind_speed: float


def _get_apikey() -> str:
    config_reader = configparser.ConfigParser()
    config_reader.read(CONFIG_FILE)
    apikey = config_reader["fmi"]["apikey"]

    if not apikey or not isinstance(apikey, str):
        raise ValueError(f"Unable to read fmi/apikey from: "
                         f"{CONFIG_FILE}")

    apikey = apikey.strip()
    if len(apikey) != 36:
        raise ValueError(f"Invalid format for fmi/apikey in: "
                         f"{CONFIG_FILE} (expecting 36 chars)")
    return apikey


@timed_cache(minutes=60)
def _make_api_request(location: str) -> models.Response:

    logger.info("Creating new weather request to FMI")
    apikey = _get_apikey()
    query = FMI_URL.format(apikey=apikey)
    params = {
        "request": "getFeature",
        "storedquery_id": "fmi::forecast::hirlam::surface::point::multipointcoverage",
        "place": location
    }
    return request(url=query, params=params, method="get")


def _parse_weather_report(content: bytes) -> Dict[datetime, WeatherPoint]:  # FIXME later:
    # OrderedDict typing would cause problems: https://tinyurl.com/y6wwtre7

    xml_tree = etree.XML(content)

    # Define namespaces
    ns_positions = ".//{http://www.opengis.net/gmlcov/1.0}positions"
    ns_data = ".//{http://www.opengis.net/gml/3.2}doubleOrNilReasonTupleList"
    ns_datafields = ".//{http://www.opengis.net/swe/2.0}field"

    # Parse data
    positions_raw: str = xml_tree.findtext(ns_positions)
    weather_data_raw: str = xml_tree.findtext(ns_data)
    field_details: Iterable = xml_tree.findall(ns_datafields)

    # Combine data and labels to dicts, weather data
    field_labels = [x.get('name') for x in field_details]
    weather_data = list()
    for row in weather_data_raw.splitlines():
        weather_data.append(dict(zip(field_labels, row.split())))

    # Combine data and labels to dicts, location(s)
    point_labels = ("lat", "lon", "timestamp")
    positions = list()
    for row in positions_raw.splitlines():
        positions.append(dict(zip(point_labels, row.split())))

    # Convert data to WeatherPoint dataclasses
    result_weather = OrderedDict()
    for point, datum in zip(positions, weather_data):
        if not point and not datum:  # skip empty rows
            continue

        this_timestamp = datetime.fromtimestamp(int(point["timestamp"]))
        weather_point = WeatherPoint(
            lat=float(point["lat"]),
            lon=float(point["lon"]),
            time=this_timestamp,
            temp=float(datum["Temperature"]),
            pressure=float(datum["Pressure"]),
            humidity=float(datum["Humidity"]),
            dew_point=float(datum["DewPoint"]),
            precipitation_1h=float(datum["Precipitation1h"]),
            precipitation_total=float(datum["PrecipitationAmount"]),
            wind_dir=float(datum["WindDirection"]),
            wind_speed=float(datum["WindSpeedMS"]),
        )

        result_weather[this_timestamp] = weather_point

    return result_weather


def _parse_api_error_response(result: models.Response) -> None:
    logger.error(f"API connection failed.")
    logger.error(f"Code: {result.status_code}, reason: {result.reason}")
    logger.error("Check DEBUG for full response.")
    logger.debug(result.text)

    xml_tree = etree.XML(result.content)
    error_message = xml_tree.findtext(".//{http://www.opengis.net/ows/1.1}ExceptionText")
    logger.error(error_message)


def fmi_forecast(location: str) -> Dict[datetime, WeatherPoint]:
    try:
        result = _make_api_request(location)
    except RequestException:
        logger.exception("Unexpected error connecting to FMI API, see log for details")
        raise ConnectionError("Unable to connect to FMI API")

    if result.ok:
        weather_data = _parse_weather_report(result.content)
    else:
        _parse_api_error_response(result)
        raise ConnectionRefusedError("FMI API refused connection, see log for details")

    return weather_data


if __name__ == "__main__":
    fmi_forecast(location="Tampere")
