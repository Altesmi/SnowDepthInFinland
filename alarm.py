import logging
import time
from collections import namedtuple
from typing import List

from apscheduler.schedulers.blocking import BlockingScheduler

from player import play_jazz_radio
from player import play_rock_radio
from player import play_weather_audio_from_yle
from weather_api import fmi_forecast  # FMI forecast only works in north-east Europe

logger = logging.getLogger()
logging.basicConfig(level=logging.DEBUG)

Alarm = namedtuple("Alarm", "id original_time wake_up_time")


def calculate_wake_time(original_time, weather):
    return original_time


def alarm_events(weather) -> List[Alarm]:
    alarms = list()
    for event in list():
        alarms.append(Alarm(
            id=1337,
            original_time=time.localtime(),
            wake_up_time=calculate_wake_time(time.localtime(), weather)
        ))
    logger.warning("alarm_events function not yet built")
    return alarms


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


def alarm(old_events):
    now = time.localtime()
    logger.debug("running alarm check at {}".format(now))
    weather = weather_forecast(time_stamp=now)

    for event in alarm_events(weather):
        if event.wake_up_time >= now and event.id not in old_events:
            if weather.type == "interesting" or True:
                sound_alarm(alarm_type="weather")
            else:
                sound_alarm()
            old_events.append(event.id)


def user_actions():
    return input("Please enter your age: ")


def main():
    old_events = list()
    scheduler = BlockingScheduler()
    scheduler.add_job(alarm, 'interval', seconds=60, kwargs={"old_events": old_events})
    scheduler.start()
    time.sleep(1)  # makes sure that the user actions are printed after initial prints

    while True:
        user_actions()
        exit(1)


if __name__ == "__main__":
    main()
