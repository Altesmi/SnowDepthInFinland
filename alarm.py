import logging
import time
from collections import namedtuple
from typing import List

from player import play_jazz_radio
from player import play_rock_radio
from player import play_weather_audio_from_yle
from weather_api import fmi_forecast  # FMI forecast only works in north-east Europe

logger = logging.getLogger()
logging.basicConfig(level=logging.DEBUG)

Alarm = namedtuple("Alarm", "id original_time wake_up_time")


def calculate_wake_time(alarm_list, weather):
    pass


def alarm_events(weather) -> List[Alarm]:
    for event in list():
        wake_up_time = calculate_wake_time(event.time, weather)
    logger.warning("alarm_events function not yet built")
    return [Alarm(id=1337, original_time=time.localtime(), wake_up_time=time.localtime())]


def weather_forecast(time_stamp):
    return fmi_forecast(time_stamp=time_stamp, location="Helsinki")


def sound_alarm(alarm_type="jazz"):
    logger.info("Start playing music")

    if alarm_type == "jazz":
        play_jazz_radio()

    elif alarm_type == "rock":
        play_rock_radio()

    elif alarm_type == "weather":
        play_weather_audio_from_yle()
        play_jazz_radio()

    else:
        play_jazz_radio()


def main():
    old_events = list()
    while True:
        now = time.localtime()
        weather = weather_forecast(time_stamp=now)

        for event in alarm_events(weather):
            if event.wake_up_time >= now and event.id not in old_events:
                if weather.type == "interesting" or True:
                    sound_alarm(alarm_type="weather")
                else:
                    sound_alarm()
                old_events.append(event.id)

        time.sleep(60)


if __name__ == "__main__":
    main()
