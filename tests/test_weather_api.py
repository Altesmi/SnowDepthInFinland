import logging
from collections import OrderedDict
from datetime import datetime

import pytest
import requests_mock
from mock import mock
from requests_mock import NoMockAddress

import weather_api


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


@mock.patch('weather_api.FMI_URL', "http://www.foobar.com/{apikey}")
def test__make_api_request_random_url_fail(mock_requests_fmi, mock_get_apikey):
    """ Make sure that tests will fail for random url """
    with pytest.raises(NoMockAddress):
        result = weather_api._make_api_request(location="Helsinki")


def test__make_api_request(mock_requests_fmi, mock_get_apikey):
    result = weather_api._make_api_request(location="Helsinki")
    assert result.ok
    assert result.content.startswith(b'<?xml version="1.0" encoding="UTF-8"?>\r\n<wfs:FeatureCollection')


def test__parse_weather_report(example_file_as_binary):
    res = weather_api._parse_weather_report(example_file_as_binary)
    assert isinstance(res, OrderedDict) or isinstance(res, dict)
    for ts, datum in res.items():
        # Only check first line from example_result_from_fmi.xml
        assert int(ts.timestamp()) == 1529758800
        assert int(datum.temp) == 15
        break
    assert len(res) == 36


def test___parse_api_error_response(mock_requests_fmi_error, mock_get_apikey, mocker):

    result = weather_api._make_api_request(location="Foobar")
    assert result.text.startswith('<?xml version="1.0" encoding="UTF-8"?>\r\n<ExceptionReport')
    assert not result.ok

    mocker.spy(weather_api.logger, 'error')
    weather_api._parse_api_error_response(result)
    weather_api.logger.error.assert_called_with("No locations found for the place with the requested language!")
