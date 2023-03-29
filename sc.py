#!/usr/bin/python3

import spotipy
import argparse
import os
import sys
import curses
from pprint import pprint
from ascii import ascii_convertor
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth
from time import sleep

COLUMNS = os.get_terminal_size().columns # NOT USED FOR LIVE PLAYBACK DISPLAY

def get_args():
    parser = argparse.ArgumentParser(
        description="Enter arguments to perform various tasks"
    )
    subparsers = parser.add_subparsers()

    display_parser = subparsers.add_parser('display')
    display_group = display_parser.add_mutually_exclusive_group()
    display_group.add_argument('--artist', required=False, nargs='?', type=str, default=None, const='Drake')
    display_group.add_argument('--album', required=False, nargs='?', type=str, default=None, const='More Life')
    display_group.add_argument('--track', required=False, nargs='?', type=str, default=None, const='Passionfruit')
    display_parser.set_defaults(func=display_stats)

    player_parser = subparsers.add_parser('player', description="Interactive player")
    player_parser.add_argument('-a', nargs='?', required=False, default=None, const=True, help="Show album image")
    player_parser.set_defaults(func=player)

    playlist_parser = subparsers.add_parser('add', description="Add currently playing track to playlist")
    playlist_parser.add_argument('--track', type=str, nargs='?', default=None, help="Add a specific track")
    playlist_parser.set_defaults(func=playlist_add)

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

def get_data(name, searchType):
    try:
        res = sp.search(q=f"{searchType}:{name}", limit=1, type=searchType)
        cat = searchType + "s"
        id = res[cat]["items"][0]["id"]
        if(searchType == "artist"):
            return sp.artist(id)
        elif(searchType == "album"):
            return sp.album(id)
        elif(searchType == "track"):
            return sp.track(id)
    except:
        print(f"Could not find given {searchType}")
        exit()

def get_image(imageUrl, scale_factor=0.75, width=os.get_terminal_size().columns):
    image = ""
    try:
        imageUrl = imageUrl
        image = ascii_convertor(imageUrl, scale_factor, width)
    except:
        image = ""
    return image

def format_ms(length_ms):
    min, sec = divmod(int(length_ms) / 1000, 60)
    min, sec = int(min), int(sec)
    return f"{min}", f"{sec:02}"

def clearConsole(n=1):
    LINE_UP = '\033[1A'
    LINE_CLEAR = '\x1b[2K'
    for i in range(n):
        print(LINE_UP, end=LINE_CLEAR)

def progress_bar(progress, prog_ms, dur_ms):
    prog_min, prog_sec = format_ms(prog_ms)
    total_min, total_sec = format_ms(dur_ms)
    prog_str = f"{prog_min:}:{prog_sec}"
    total_str = f"{total_min:}:{total_sec}"

    completed = int(progress * os.get_terminal_size().columns)
    remaining = int(os.get_terminal_size().columns - completed)
    return "|"*completed + "-"*remaining, prog_str, total_str

def toggle_playback(data):
    sp.pause_playback() if data["is_playing"] else sp.start_playback()

def toggle_shuffle(args):
    data = sp.current_playback()
    sp.shuffle(True) if data["shuffle_state"] == False else sp.shuffle(False)
    data = sp.current_playback()
    state = "on" if data["shuffle_state"] else "off"
    print(f"Shuffle turned {state}")

def toggle_repeat(args):
    data = sp.current_playback()
    states = ['context', 'track', 'off']
    sp.repeat(states[(states.index(data["repeat_state"]) + 1) % len(states)])
    data = sp.current_playback()
    print("Repeat state: " + data["repeat_state"])

def volume(args):
    if args.amount:
        sp.volume(args.amount)
    sleep(0.1) # necessary to retrieve current_playback in time on next line
    data = sp.current_playback()
    print(f"Volume: {data['device']['volume_percent']}")

def display_stats(args): # displays relevant info about artist
    data = dict()
    tab, nl = "\t", "\n"
    if args.artist:
        data = get_data(args.artist, "artist")
        name, followers, popularity, genres = data["name"], data["followers"]["total"], data["popularity"], str(data["genres"])
        image = get_image(data["images"][0]["url"])
        print(f"="*COLUMNS)
        print(image)
        print(f"Artist: {name}")
        print(f"Followers: {followers}")
        print(f"Popularity: {popularity}")
        print(f"Genres: {genres}")
        print(f"="*COLUMNS)

    elif args.album:
        data = get_data(args.album, "album")
        name, artist, total_tracks, release_date, genres, popularity = data["name"], data["artists"][0]["name"], data["total_tracks"], data["release_date"], str(data["genres"]), data["popularity"]
        image = get_image(data["images"][0]["url"], scale_factor=0.5)
        track_list = data["tracks"]["items"]
        print(f"="*COLUMNS)
        print(image)
        print(f"Album: {name}")
        print(f"Artist: {artist}")
        print(f"Genres: {genres}")
        print(f"Popularity: {popularity}")
        print(f"Total tracks: {total_tracks}{nl}")
        print(f"Track List:{'':<45}Duration")
        for track in track_list:
            min, sec = format_ms(track["duration_ms"])
            track_number = track["track_number"]
            track_name = track["name"]
            print(f"{track_number}.{tab}{track_name:<50}{min}:{sec}")
        print(f"{nl}Released: {release_date}")
        print(f"="*COLUMNS)

    elif args.track:
        data = get_data(args.track, "track")
        name, artist, popularity, album = data["name"], data["artists"][0]["name"], data["popularity"], data["album"]["name"]
        image = get_image(data["album"]["images"][0]["url"])
        min, sec = format_ms(data["duration_ms"])
        print(f"="*COLUMNS)
        print(image)
        print(f"Track: {name}")
        print(f"Artist: {artist}")
        print(f"Album: {album}")
        print(f"Popularity: {popularity}")
        print(f"Track length: {min}:{sec}")
        print(f"="*COLUMNS)

def playlist_print(stdscr, curIdx, menu, trackName, trackArtist, trackAlbum):
    stdscr.erase()
    height, width = stdscr.getmaxyx()

    stdscr.addstr(0, 0, "Adding")
    stdscr.addstr(1, 0, "\t" + f"Track: {trackName}")
    stdscr.addstr(2, 0, "\t" + f"Artist: {trackArtist}")
    stdscr.addstr(3, 0, "\t" + f"Album: {trackAlbum}")
    stdscr.addstr(4, 0, "to...")

    for i, (key, val) in enumerate(menu.items()):
        x = width // 10
        y = i + 7
        if i == curIdx:
            stdscr.attron(curses.color_pair(1))
            stdscr.addstr(y, x, key)
            stdscr.attroff(curses.color_pair(1))
        else:
            stdscr.addstr(y, x, key)
    stdscr.addstr(len(menu) + 8, x, "Press Enter to select...")
    stdscr.addstr(len(menu) + 9, x, "Press q to quit...")
    stdscr.refresh()

def playlist_selector(stdscr, args):
    curses.use_default_colors()
    data = sp.current_playback()
    me = sp.current_user()
    playlists = sp.current_user_playlists()
    menu = dict()
    for i, item in enumerate(playlists["items"]):
        if item["owner"]["id"] == me["id"]:
            menu[item["name"]] = item["id"]

    track = None
    if args.track:
        track = sp.track(sp.search(q="track:" + args.track, limit=1)["tracks"]["items"][0]["id"])
    else:
        track = sp.track(data["item"]["id"])
    trackName, trackID = track["name"], track["id"]
    trackArtist, trackAlbum = track["artists"][0]["name"], track["album"]["name"]

    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curIdx = 0
    keys = list(menu)
    playlist_print(stdscr, curIdx, menu, trackName, trackArtist, trackAlbum)
    while True:
        key = stdscr.getch()
        if key == ord('q'):
            break
        if key == curses.KEY_UP and curIdx > 0:
            curIdx -= 1
        elif key == curses.KEY_DOWN and curIdx < len(menu) - 1:
            curIdx += 1
        elif key == curses.KEY_ENTER or key in [10, 13]:
            stdscr.erase()
            try:
                playlist = keys[curIdx]
                sp.playlist_add_items(menu[playlist], [trackID])
                stdscr.addstr(f"Added {trackName} to {playlist} successfully" + "\n\n")
                stdscr.addstr("Press any button to return...")
                stdscr.refresh()
                stdscr.getch()
            except:
                stdscr.addstr("Could not add track to playlist")
                stdscr.refresh()
                stdscr.getch()
        playlist_print(stdscr, curIdx, menu, trackName, trackArtist, trackAlbum)

def playlist_add(args):
    try:
        curses.wrapper(playlist_selector, args)
    except:
        return


def player_helper(stdscr, args):
    try:
        k = 0
        curses.halfdelay(10)
        curses.use_default_colors()
        curses.noecho()
        while True:
            data = sp.current_playback()
            height, width = stdscr.getmaxyx()

            k = stdscr.getch()
            if k == ord('q'):
                break
            if k == ord('p'):
                sp.pause_playback()
            if k == curses.KEY_SRIGHT:
                sp.next_track()
            if k == curses.KEY_SLEFT:
                sp.previous_track()
            if k == ord(' '):
                toggle_playback(data)
            if k == curses.KEY_UP:
                sp.volume(min(100, data['device']['volume_percent'] + 10))
            if k == curses.KEY_DOWN:
                sp.volume(max(0, data['device']['volume_percent'] - 10))
            stdscr.erase()
            name = data["item"]["name"]
            device = data["device"]["name"]
            artists = data["item"]["artists"]
            artist = artists[0]["name"]
            feats = '(feat. ' + ', '.join([artists[i]["name"] for i in range(1, len(artists))]) + ')' \
                if (len(artists) > 1 and 'feat.' not in name) else ''
            album = data["item"]["album"]["name"]
            track_str = f"Track: {name} - {artist} {feats}"
            album_str = f"Album: {album}"
            pbar, prog_str, total_str = progress_bar(data["progress_ms"] / data["item"]["duration_ms"], data["progress_ms"], data["item"]["duration_ms"])
            stdscr.addstr(f"="*width)
            if args.a == True:
                image = get_image(data["item"]["album"]["images"][0]["url"], 0.25, width)
                stdscr.addstr(image + '\n')
            stdscr.addstr("Now playing...\n") if data["is_playing"] else stdscr.addstr("Paused\n")
            stdscr.addstr(track_str + '\n')
            stdscr.addstr(album_str + '\n')
            stdscr.addstr(f"{pbar}")
            stdscr.addstr(f"{prog_str}{total_str : >{width - len(prog_str)}}\n")
            stdscr.addstr(f"On: {device}\n")
            stdscr.addstr(f"="*width)
            stdscr.refresh()
    except:
        print("Could not retrieve live playback")
        # pprint(data)
        os.system("stty sane && clear")
        exit()

def player(args):
    curses.wrapper(player_helper, args)
    # pprint(sp.current_playback())

def run():
    args = get_args()
    args.func(args)
    
if  __name__=='__main__':
    scope = "user-read-playback-state,user-modify-playback-state,playlist-modify-public,playlist-modify-private,playlist-read-private"
    auth_manager = SpotifyClientCredentials()
    sp = spotipy.Spotify(client_credentials_manager=SpotifyOAuth(scope=scope))
    # sp = spotipy.Spotify(auth_manager=auth_manager)
    run()