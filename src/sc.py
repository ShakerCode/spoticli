#!/usr/bin/python3

import spotipy
import argparse
from playback import *
from player import player, art
from search import search
from playlist import playlist_add
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth

# COLUMNS = os.get_terminal_size().columns # NOT USED FOR LIVE PLAYBACK DISPLAY

def get_args():
    parser = argparse.ArgumentParser(
        description="Enter arguments to perform various tasks"
    )
    subparsers = parser.add_subparsers()

    search_parser = subparsers.add_parser('search')
    search_group = search_parser.add_mutually_exclusive_group()
    search_group.add_argument('--artist', required=False, nargs='?', type=str, default=None, const='Drake')
    search_group.add_argument('--album', required=False, nargs='?', type=str, default=None, const='More Life')
    search_group.add_argument('--track', required=False, nargs='?', type=str, default=None, const='Passionfruit')
    search_parser.set_defaults(func=search)

    player_parser = subparsers.add_parser('player', description="Interactive player")
    player_parser.add_argument('-a', nargs='?', required=False, default=None, const=True, help="Show album image")
    player_parser.add_argument('--track', action='store_const', default=None, const=None)
    player_parser.set_defaults(func=player)

    playlist_parser = subparsers.add_parser('add', description="Add currently playing track to playlist")
    playlist_parser.add_argument('--track', type=str, nargs='?', default=None, help="Add a specific track")
    playlist_parser.set_defaults(func=playlist_add)

    art_parser = subparsers.add_parser('art', description="[ZOOM OUT FIRST FOR BETTER RESOLUTION] Display art for current track")
    art_parser.set_defaults(func=art)

    pause_parser = subparsers.add_parser('pause', description="Pause playback")
    pause_parser.set_defaults(func=lambda x: sp.pause_playback())

    play_parser = subparsers.add_parser('play', description="Start/resume  playback")
    play_parser.set_defaults(func=lambda x: sp.start_playback())

    volume_parser = subparsers.add_parser('vol', description="View/adjust volume")
    volume_parser.add_argument('amount', type=int, nargs='?', default=None, help="Specify volume amount")
    volume_parser.set_defaults(func=volume)

    skip_parser = subparsers.add_parser('skip', description="Skip to next track")
    skip_parser.set_defaults(func=lambda x: sp.next_track())

    prev_parser = subparsers.add_parser('prev', description="Go back to previous next track")
    prev_parser.set_defaults(func=lambda x: sp.previous_track())

    shuffle_parser = subparsers.add_parser('shuffle', description="Toggle shuffle state")
    shuffle_parser.set_defaults(func=toggle_shuffle)

    repeat_parser = subparsers.add_parser('repeat', description="Toggle repeat state")
    repeat_parser.set_defaults(func=toggle_repeat)

    return parser.parse_args()

def run():
    args = get_args()
    args.func(args, sp)
    
if  __name__=='__main__':
    scope = "user-read-playback-state,user-modify-playback-state,playlist-modify-public,playlist-modify-private,playlist-read-private"
    auth_manager = SpotifyClientCredentials()
    sp = spotipy.Spotify(client_credentials_manager=SpotifyOAuth(scope=scope))
    # sp = spotipy.Spotify(auth_manager=auth_manager)
    run()