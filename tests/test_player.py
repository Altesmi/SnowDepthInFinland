import player


def test_play_weather_audio_from_yle():
    player.play_weather_audio_from_yle()


def test_play_url():
    player.play_url("http://us2.internet-radio.com:8208")
