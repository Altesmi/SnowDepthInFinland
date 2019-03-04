import configparser
import logging
from datetime import datetime
from typing import List

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
class Measurement(object):
    time: datetime
    value: float


@dataclass
class StationData(object):
    identifier: int
    region: str
    measurements: List[Measurement]


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
def _make_api_request() -> models.Response:
    logger.info("Creating new weather request to FMI")
    apikey = _get_apikey()
    query = FMI_URL.format(apikey=apikey)
    params = {
        "request": "getFeature",
        "storedquery_id": "fmi::observations::weather::daily::timevaluepair",
        "parameters": "snow",
        "starttime": "2018-01-24T00:00:00Z",
        "endtime": "2018-02-24T00:00:00Z",
        "bbox": "20,60,30,70",
    }
    return request(url=query, params=params, method="get")


def _parse_weather_report(content: bytes):
    xml_tree = etree.XML(content)

    # Define namespaces
    namespaces = {
        "wfs": "http://www.opengis.net/wfs/2.0",
        "xsi": "http://www.w3.org/2001/XMLSchema-instance",
        "xlink": "http://www.w3.org/1999/xlink",
        "om": "http://www.opengis.net/om/2.0",
        "ompr": "http://inspire.ec.europa.eu/schemas/ompr/3.0",
        "omso": "http://inspire.ec.europa.eu/schemas/omso/3.0",
        "gml": "http://www.opengis.net/gml/3.2",
        "gmd": "http://www.isotc211.org/2005/gmd",
        "gco": "http://www.isotc211.org/2005/gco",
        "swe": "http://www.opengis.net/swe/2.0",
        "gmlcov": "http://www.opengis.net/gmlcov/1.0",
        "sam": "http://www.opengis.net/sampling/2.0",
        "sams": "http://www.opengis.net/samplingSpatial/2.0",
        "wml2": "http://www.opengis.net/waterml/2.0",
        "target": "http://xml.fmi.fi/namespace/om/atmosphericfeatures/1.0",
    }

    elements = {
        "observators": f".//{{{namespaces['omso']}}}PointTimeSeriesObservation",
        "observator_id": f".//{{{namespaces['gml']}}}identifier",
        "observator_region": f".//{{{namespaces['target']}}}region",
        "measurements": f".//{{{namespaces['wml2']}}}point",
        "measurement_time": f".//{{{namespaces['wml2']}}}time",
        "measurement_value": f".//{{{namespaces['wml2']}}}value",
    }

    stations = list()

    # Parse data
    for collection_point in xml_tree.iterfind(elements["observators"]):
        station = StationData(
            identifier=collection_point.findtext(elements["observator_id"]),
            region=collection_point.findtext(elements["observator_region"]),
            measurements=[]
        )
        for measurement_point in collection_point.iterfind(elements["measurements"]):
            data = Measurement(
                time=datetime.strptime(
                    measurement_point.findtext(elements["measurement_time"]),
                    "%Y-%m-%dT%H:%M:%SZ"
                ),
                value=float(measurement_point.findtext(elements["measurement_value"]))
            )
            station.measurements.append(data)
        stations.append(station)

    return stations


def snow_data():
    try:
        result = _make_api_request()
    except RequestException:
        logger.exception("Unexpected error connecting to FMI API, see log for details")
        raise ConnectionError("Unable to connect to FMI API")

    if result.ok:
        weather_data = _parse_weather_report(result.content)
    else:
        logger.error(result.content)
        raise ConnectionRefusedError("FMI API refused connection, see log for details")

    return weather_data


if __name__ == "__main__":
    snow_data()
