
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
wikipediaurls = {"Billboard Top 100 2020's":"https://en.wikipedia.org/wiki/List_of_Billboard_Hot_100_number-one_singles_of_the_2020s","Billboard Top 100 By Year":"https://en.wikipedia.org/wiki/Billboard_Year-End_Hot_100_singles_of_"}

# Used for showing menu options
def menu():
    global wikipediaurls
    counter = 1
    print("Please choose an option")
    for name in wikipediaurls.keys():
        print(f"{counter}. {name}({wikipediaurls[name]})")
        counter+=1
    choice = input("Choice:")

    return choice

def timer():
    return time.perf_counter()

# Call choices of menu
def choose_option(choice):
    global wikipediaurls, notfound
    parsedpage = []
    start_time = 0.0

    match choice:
        case "1": # Billboard top 100 2020's
            # grab table from result
            start_time = timer()
            page = wikipedia.Wikipedia.grab_table_result(wikipediaurls["Billboard Top 100 2020's"]) # first url
            
            # parse the results
            parsedpage = wikipedia.Wikipedia.parse_billboard_hot_100_2020(page)

        case "2": # Billboard top 100 by year
            year = input("Please enter the year you would like: ")
            start_time = timer()
            page = wikipedia.Wikipedia.grab_table_result(wikipediaurls["Billboard Top 100 By Year"] + year) # add year to url and grab it

            print(page)
            exit(0)
        case _:
            print("Unknown choice")

    # Authenticate with Spotify
    try:
        sp = spotify.Spotify.authenticate_spotify()
        user_id = sp.current_user()["id"]
    except Exception as exc:
        print(f"Spotify authentication failed: {exc}")
        print("Please authorize the app again and try running the script.")
        return

    # parsed-page needs to be {"track":"artist",...} format
    notfound, uris = spotify.Spotify.search_spotify_uris(sp,parsedpage,debug)

    # If dry run don't create playlist
    if(dryRun): 
        print("Dry run set to `True`, would've created a playlist of these songs/uris:")
        print(parsedpage)
        print(uris)
    else:
        # Need playlist name
        name = input("Please enter a name you would like for the Playlist that will be created (ImportToSpotify DATE is default): ").strip()
        if not name:
            name = f"ImportToSpotify {time.strftime('%Y-%m-%d')}" # Default to this as name
        spotify.Spotify.create_spotify_playlist(sp, user_id, name, uris)

    # end timer of program
    end_time = timer()

    metrics(parsedpage,uris,end_time-start_time)


def load_environment():
    global debug, dryRun
    """Loads environment variables from the .env file."""
    load_dotenv()
    # Set two custom envs
    if(os.getenv("DEBUG") == "True"): 
        debug = True

    if(os.getenv("DRY_RUN") == "True"): 
        dryRun = True

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
    # Load from env
    load_environment()

    # call menu and options
    choose_option(menu())

if __name__ == "__main__":
    main()