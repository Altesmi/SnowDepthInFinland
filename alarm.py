import logging
import time
from collections import namedtuple
from typing import List

import vlc

from weather_api import fmi_forecast  # FMI forecast only works in north-east Europe

logger = logging.getLogger()
logging.basicConfig(level=logging.DEBUG)

Alarm = namedtuple("Alarm", "id original_time wake_up_time")


def calculate_wake_time(alarm_list, weather):
    pass


def alarm_events(weather) -> List[Alarm]:  # TODO
    for event in list():
        wake_up_time = calculate_wake_time(event.time, weather)
    logger.warning("alarm_events function not yet built")
    return [Alarm(id=1337, original_time=time.localtime(), wake_up_time=time.localtime())]


def weather_forecast(time_stamp):
    return fmi_forecast(time_stamp=time_stamp, location="Helsinki")


def sound_alarm():
    logger.info("Start playing music")
    i = vlc.Instance()
    p = i.media_player_new(uri='http://94.23.252.14:8273/stream')
    a = p.play()
    if a != 0:
        logger.warning("what happen - this should be 0!!")


def main():
    old_events = list()
    while True:
        now = time.localtime()
        weather = weather_forecast(time_stamp=now)

        for event in alarm_events(weather):
            if event.wake_up_time >= now and event.id not in old_events:
                sound_alarm()
                old_events.append(event.id)

        time.sleep(60)


if __name__ == "__main__":
    main()
