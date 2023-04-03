import os
from ascii import get_image
from player import format_ms

COLUMNS = os.get_terminal_size().columns # NOT USED FOR LIVE PLAYBACK DISPLAY

def get_data(name, searchType, sp):
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

def search(args, sp): # displays relevant info about artist
    data = dict()
    tab, nl = "\t", "\n"
    if args.artist:
        data = get_data(args.artist, "artist", sp)
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
        data = get_data(args.album, "album", sp)
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
        data = get_data(args.track, "track", sp)
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