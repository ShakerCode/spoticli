import curses

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

def playlist_selector(stdscr, args, sp):
    curses.use_default_colors()
    curses.curs_set(0)
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

def playlist_add(args, sp):
    try:
        curses.wrapper(playlist_selector, args, sp)
    except:
        print("Something went wrong (playlist)")