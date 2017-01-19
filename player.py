import logging
import time

import vlc
import xmltodict
from requests import request

logger = logging.getLogger(__name__)


def play_url(url):
    i = vlc.Instance()
    p = i.media_player_new(uri=url)
    a = p.play()
    if a != 0:
        logger.warning("what happen - this should be 0!!")

def play_weather_audio_from_yle():
    # https://feeds.yle.fi/areena/v1/series/1-1257538.rss?lang=fi&downloadable=true
    # http://developer.yle.fi/tutorial-playing-a-program/
    feed = request(url="https://feeds.yle.fi/areena/v1/series/1-1257538.rss?lang=fi&downloadable=true", method="get")
    feed_dict = xmltodict.parse(feed.text)

    weather_link = feed_dict["rss"]["channel"]["item"][0]["link"]
    print(weather_link)
    return
    player = vlc.MediaPlayer(weather_link)
    player.play()
    time.sleep(30)

def play_jazz_radio():
    logger.debug("Nothing but jazz")
    # play_url("http://broadcast.infomaniak.ch/jazzradio-high.mp3.m3u")
    # play_url("http://94.23.252.141:8273/stream")
    play_url("http://us2.internet-radio.com:8208")
    time.sleep(3)

def play_rock_radio():
    logger.debug("Nothing but ROOOCCCKKKK!!!")
    play_url("http://webradio.antennevorarlberg.at/classicrock.m3u")
    time.sleep(3)
