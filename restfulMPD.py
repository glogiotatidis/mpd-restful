#!/usr/bin/env python
from mpd import ConnectionError, MPDClient
from bottle import request, route, run
from decouple import config

_client = None


def client(function):
    def _get_client():
        global _client
        try:
            _client.ping()
        except (AttributeError, ConnectionError):
            _client = MPDClient()
            mpd_host = config('MPD_HOST', default='localhost')
            mpd_port = config('MPD_PORT', default=6600)
            _client.connect(mpd_host, mpd_port)
        function(_client)
    return _get_client


@route('/')
def home():
    return 'Hello'


@route('/start', method='POST')
@route('/play', method='POST')
@client
def play(client):
    client.play()
    return 'OK'


@route('/pause', method='POST')
@client
def pause(client):
    if client.status()['state'] == 'play':
        client.pause(1)
    else:
        client.pause(0)
    return 'OK'


@route('/stop', method='POST')
@client
def stop(client):
    client.stop()
    return 'OK'


@route('/load', method='POST')
@client
def load(client):
    clear = request.query.get('clear')
    if clear and clear.lower() == 'true':
        client.clear()
    playlist = request.query.get('playlist')
    client.load(playlist)
    play = request.query.get('play')
    if play and play.lower() == 'true':
        client.play()
    return 'OK'


@route('/volume', method='POST')
@client
def volume(client):
    v = request.query.get('volume')
    if v[0] in ('+', '-'):
        v = int(v)
        current_volume = int(client.status().get('volume', 50))
        v += current_volume
    client.setvol(v)


if __name__ == "__main__":
    host = config('HOST', default='0.0.0.0')
    port = config('PORT', default=8000)
    run(host=host, port=port, reloader=True)
