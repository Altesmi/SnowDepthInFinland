import logging
import re

import pytest
from requests_mock import ANY  # Notice that fixture name has naming conflict with library name

import weather_api

logger = logging.getLogger(__name__)


@pytest.fixture
def example_file_as_binary():
    with open("example_result_from_fmi.xml", 'rb') as infile:
        res = infile.read()
    return res


@pytest.fixture
def example_error_as_binary():
    with open("example_error_result_from_fmi.xml", 'rb') as infile:
        res = infile.read()
    return res


@pytest.fixture
def mock_requests_fmi(requests_mock, example_file_as_binary):
    mock_result = example_file_as_binary
    url_pattern = re.compile("http://data.fmi.fi/fmi-apikey/.*/wfs?.*")
    requests_mock.register_uri("GET", url_pattern, content=mock_result)


@pytest.fixture
def mock_requests_fmi_error(requests_mock, example_error_as_binary):
    mock_result = example_error_as_binary
    url_pattern = re.compile("http://data.fmi.fi/fmi-apikey/.*/wfs?.*")
    requests_mock.register_uri("GET", url_pattern, content=mock_result, status_code=404)


@pytest.fixture
def mock_get_apikey(monkeypatch):
    def mock_apikey():
        return "00000000-0000-0000-0000-000000000000"
    monkeypatch.setattr(weather_api, '_get_apikey', mock_apikey)
