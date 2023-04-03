import spotipy
import curses
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth
from time import sleep

def toggle_playback(data, sp):
    sp.pause_playback() if data["is_playing"] else sp.start_playback()

def toggle_shuffle(args, sp):
    data = sp.current_playback()
    sp.shuffle(True) if data["shuffle_state"] == False else sp.shuffle(False)
    data = sp.current_playback()
    state = "on" if data["shuffle_state"] else "off"
    print(f"Shuffle turned {state}")

def toggle_repeat(args, sp):
    data = sp.current_playback()
    states = ['context', 'track', 'off']
    sp.repeat(states[(states.index(data["repeat_state"]) + 1) % len(states)])
    data = sp.current_playback()
    print("Repeat state: " + data["repeat_state"])

def volume(args, sp):
    if args.amount:
        sp.volume(args.amount)
    sleep(0.1) # necessary to retrieve current_playback in time on next line
    data = sp.current_playback()
    print(f"Volume: {data['device']['volume_percent']}")


def playback_controls(k, data, sp):
        if k == ord('q'):
            return -1
        if k == ord('p'):
            sp.pause_playback()
        if k == curses.KEY_SRIGHT:
            sp.next_track()
        if k == curses.KEY_SLEFT:
            sp.previous_track()
        if k == ord(' '):
            toggle_playback(data, sp)
        if k == curses.KEY_UP:
            sp.volume(min(100, data['device']['volume_percent'] + 10))
        if k == curses.KEY_DOWN:
            sp.volume(max(0, data['device']['volume_percent'] - 10))