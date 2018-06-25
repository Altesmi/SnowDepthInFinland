from datetime import datetime
from functools import lru_cache
from typing import List, Dict, Optional, Tuple

from weather_api import WeatherPoint


def filter_by_dates(weather_data, start_time, end_time) -> List[WeatherPoint]:
    start_time = start_time or datetime.strptime("1900", "%Y")
    end_time = end_time or datetime.strptime("2100", "%Y")
    new_data = [datum for ts,  datum in weather_data.items() if start_time <= ts <= end_time]
    return new_data


def temperature_range(
        weather_data: Dict[datetime, WeatherPoint],
        start_time: Optional[datetime]=None,
        end_time: Optional[datetime]=None) -> Tuple[Optional[float], Optional[float]]:

    subset = filter_by_dates(weather_data, start_time, end_time)
    subset_without_nones = [x.temp for x in subset if x.temp]
    if not subset_without_nones:
        return None, None
    min_temp = min(subset_without_nones)
    max_temp = max(subset_without_nones)
    return min_temp, max_temp
