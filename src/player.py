import curses
import os
from time import sleep
from playback import playback_controls
from playlist import playlist_add
from ascii import get_image
from pprint import pprint

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

def art_helper(stdscr, args, sp):
    try:
        curses.curs_set(0)
        scale_factor = 0.30
        pad = curses.newpad(curses.LINES - 1, curses.COLS - 1)
        data = sp.current_playback()
        cur, prev = data["item"]["id"], ""
        curses.noecho()
        while True:
            height, width = pad.getmaxyx()
            data = sp.current_playback()

            stdscr.nodelay(True)
            k = stdscr.getch()
            pb = playback_controls(args, k, data, sp)
            if pb == -1:
                break

            pad.erase()
            cur = data["item"]["id"]
            if(cur != prev): # update image
                image = get_image(data["item"]["album"]["images"][0]["url"], scale_factor, width)
                rowInc = 0
                offset = int(scale_factor * width) // 2
                for line in image.split("\n"):
                    pad.addstr(0 + rowInc, width // 2 - offset, line)
                    rowInc += 1
                pad.refresh(0, 0, 0, 0, height - 1, width - 1)
            prev = cur
            sleep(1)
    except:
        print("Couldn't print art")
        return

def art(args, sp):
    curses.wrapper(art_helper, args, sp)

def player_helper(stdscr, args, sp):
    try:
        curses.use_default_colors()
        curses.noecho()
        curses.curs_set(0)
        while True:
            data = sp.current_playback()
            height, width = stdscr.getmaxyx()

            stdscr.nodelay(True)
            k = stdscr.getch()
            pb = playback_controls(args, k, data, sp)
            if pb == -1:
                break

            stdscr.erase() # erase prev info
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
            stdscr.refresh() # update with current info
            sleep(1)
    except:
        print("Could not retrieve live playback")
        os.system("stty sane && clear")
        exit()

def player(args, sp):
    curses.wrapper(player_helper, args, sp)