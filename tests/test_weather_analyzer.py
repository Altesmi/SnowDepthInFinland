from datetime import datetime

import pytest

import weather_analyzer
import weather_api


@pytest.fixture
def weather_data(mock_requests_fmi, mock_get_apikey):
    return weather_api.fmi_forecast('foobar')


def test_temperature_range(weather_data):

    assert (9.03, 17.52) == weather_analyzer.temperature_range(
        weather_data=weather_data), 'full range'

    assert (9.03, 17.52) == weather_analyzer.temperature_range(
        weather_data=weather_data,
        start_time=datetime(2018, 6, 24, 4, 0)),  'limit start time (true min first)'

    assert (9.12, 17.52) == weather_analyzer.temperature_range(
        weather_data=weather_data,
        start_time=datetime(2018, 6, 24, 4, 1)),  'limit start time (true min before)'

    assert (9.03, 15.15) == weather_analyzer.temperature_range(
        weather_data=weather_data,
        end_time=datetime(2018, 6, 24, 4, 0)),  'limit end time, true max after'

    assert (9.03, 17.52) == weather_analyzer.temperature_range(
        weather_data=weather_data,
        end_time=datetime(2019, 6, 24, 4, 0)),  'limit end time, true max before'

    assert (9.12, 9.12) == weather_analyzer.temperature_range(
        weather_data=weather_data,
        start_time=datetime(2018, 6, 24, 5, 0),
        end_time=datetime(2018, 6, 24, 5, 2)), 'start and end time'


def test_temperature_range_errors(weather_data):

    assert (None, None) == weather_analyzer.temperature_range(
        weather_data=weather_data,
        start_time=datetime(2019, 6, 24, 5, 0),
        end_time=datetime(2018, 6, 24, 5, 2)), 'start after end'

    with pytest.raises(AttributeError):
        weather_analyzer.temperature_range(
            weather_data=None,
            start_time=datetime(2019, 6, 24, 5, 0),
            end_time=datetime(2018, 6, 24, 5, 2))

    assert (None, None) == weather_analyzer.temperature_range(
        weather_data=dict(),
        start_time=datetime(2019, 6, 24, 5, 0),
        end_time=datetime(2018, 6, 24, 5, 2)),  'weather data = empty dict'

