
import requests
import os
import json
from dotenv import load_dotenv
import time
from spotifyapp import spotify
from wikipediaapp import wikipedia

# global variables
debug = False
dryRun = False
notfound=[]
PERPAGE=100

def load_environment():
    global debug, dryRun
    """Loads environment variables from the .env file."""
    load_dotenv()
    # Set two custom envs
    if(os.getenv("DEBUG") == "True"): 
        debug = True

    if(os.getenv("DRY_RUN") == "True"): 
        dryRun = True

# Per page defaults to 100
# Search url defaults to ``
# Returns json response of results in pages
def callCogs(year,page,per_page=PERPAGE,search_url=""):
    CONSUMER_KEY=os.getenv("CONSUMER_KEY")
    CONSUMER_SECRET=os.getenv("CONSUMER_SECRET")
    params = {"format":"single","year": year, "per_page": per_page, "page": page, "country":"US"} 
    headers = {"User-Agent": "DiscogsToSpotify/0.1 +https://github.com/ikoded/BillboardToSpotifyPlaylist","Authorization" : f"Discogs key={CONSUMER_KEY}, secret{CONSUMER_SECRET}"}
    
    response = requests.get(search_url, headers=headers, params=params)
    jsonresponse = json.loads(response.text)
    return jsonresponse

# Metrics for ending program
def metrics(song_names: dict[str,str], uris: list, timeelapsed: float):
    expectedsongs = len(song_names)
    foundsongs = len(uris)

    print("------------------------------")
    print("Songs Not Found:")
    for song in notfound:
        print(f"- {song}")
    print("------------------------------")
    print("Metrics for script:")
    print(f"Expected Songs: {expectedsongs}\nFound Songs: {foundsongs}\nTime elapsed: {timeelapsed} seconds")
    print("------------------------------")

def main():
    global notfound
    # Start for tracking execution time
    start_time = time.perf_counter()

    # Load from env
    load_environment()

    # Need playlist name
    name = input("Please enter a name you would like for the Playlist that will be created (ImportToSpotify DATE is default): ").strip()
    if not name:
        name = f"ImportToSpotify {time.strftime('%Y-%m-%d')}" # Default to this as name

    # Authenticate with Spotify
    try:
        sp = spotify.Spotify.authenticate_spotify()
        user_id = sp.current_user()["id"]
    except Exception as exc:
        print(f"Spotify authentication failed: {exc}")
        print("Please authorize the app again and try running the script.")
        return

    # grab table from result
    # TODO: Make this have different links you can create a playlist from and maybe change sources
    page = wikipedia.Wikipedia.grabTableResult('https://en.wikipedia.org/wiki/List_of_Billboard_Hot_100_number-one_singles_of_the_2020s')
    # parse the results
    parsedpage = wikipedia.Wikipedia.parsebillboardhot100(page)
    
    # sortedResults needs to be {"track":"artist",...} format
    notfound, uris = spotify.Spotify.search_spotify_uris(sp,parsedpage,debug)
    # If dry run don't create playlist
    if(dryRun): 
        print("Dry run set to `True`, would've created a playlist of these songs/uris:")
        print(parsedpage)
        print(uris)
    else:
        spotify.Spotify.create_spotify_playlist(sp, user_id, name, uris)
    
    # Metrics
    end_time= time.perf_counter()
    metrics(parsedpage,uris,end_time-start_time)

if __name__ == "__main__":
    main()