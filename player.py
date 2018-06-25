import logging
import threading
import time

import vlc


logger = logging.getLogger(__name__)


class VlcPlayer(object):

    def __init__(self):
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()
        self.player.audio_set_volume(20)
        self.list_player = self.instance.media_list_player_new()
        self.media = None

    def _start(self):
        if self.list_player.play() != 0:
            logger.warning("what happen - this should be 0!!")

    def stop(self):
        self.list_player.stop()

    def play_url(self, url):
        self.player.set_media(self.media)
        media_list = self.instance.media_list_new([url])
        self.list_player.set_media_list(media_list)

        self._start()

    def play_weather_audio_from_yle(self):
        # https://feeds.yle.fi/areena/v1/series/1-1257538.rss?lang=fi&downloadable=true
        # http://developer.yle.fi/tutorial-playing-a-program/

        raise NotImplementedError(
            "YLE API does not yet support (weather) news. More info: "
            "https://developer.yle.fi/tutorial-not-available-content/index.html"
        )

    def play_jazz_radio(self):
        logger.debug("Nothing but jazz")
        # play_url("http://broadcast.infomaniak.ch/jazzradio-high.mp3.m3u")
        # play_url("http://94.23.252.141:8273/stream")
        self.play_url("http://us2.internet-radio.com:8208")
        time.sleep(3)

    def play_rock_radio(self):
        logger.debug("Nothing but ROOOCCCKKKK!!!")
        self.play_url("http://webradio.antennevorarlberg.at/classicrock.m3u")
        time.sleep(3)


if __name__ == "__main__":
    player = VlcPlayer()
    player.play_rock_radio()
    time.sleep(60)
