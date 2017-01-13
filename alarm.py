import logging
import time
from collections import namedtuple
from typing import List

import vlc

from weather_api import foobar

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


def weather_forecast(location):
    return foobar()


def sound_alarm():
    logger.info("Start playing music")
    i = vlc.Instance()
    p = i.media_player_new(uri='http://94.23.252.14:8273/stream')
    a = p.play()


def main():
    old_events = list()
    while True:
        weather = weather_forecast(location="Helsinki")
        now = time.localtime()

        for event in alarm_events(weather):
            if event.wake_up_time >= now and event.id not in old_events:
                sound_alarm()
                old_events.append(event.id)

        time.sleep(60)


if __name__ == "__main__":
    main()
