import spotipy
from spotipy.oauth2 import SpotifyOAuth
from rapidfuzz import fuzz
import os

class Spotify:
    # Authenticates with Spotify and returns a Spotipy client
    @staticmethod
    def authenticate_spotify() -> spotipy.Spotify:
        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope="playlist-modify-private", client_id=os.getenv("CLIENT_ID"), client_secret=os.getenv("CLIENT_SECRET"), redirect_uri=os.getenv("REDIRECT_URI"), cache_path="./token.txt"))
        return sp

    # Searches for song URIs on Spotify using fuzzy matching when needed
    @staticmethod
    def search_spotify_uris(sp: spotipy.Spotify, song_names: dict[str,str]) -> list:
        global notfound
        uris = []

        for song in song_names: # map format is {"title":"artist",...}
            try:
                # Attempt exact search first
                result = sp.search(q=f"track:{song} artist:{song_names[song]}", type="track", limit=1)
                items = result["tracks"]["items"]
                if items:
                    uri = items[0]["uri"]
                    if(debug): print(f"Song {song} by {song_names[song]} was found at {uri}.")
                    uris.append(uri)
                    continue

                # If not found, use fuzzy matching on broader search
                fallback_result = sp.search(q=song, type="track", limit=10)
                best_match = None
                highest_score = 0

                for item in fallback_result["tracks"]["items"]:
                    title = item["name"]
                    score = fuzz.ratio(song.lower(), title.lower())
                    if score > highest_score:
                        highest_score = score
                        best_match = item

                if best_match and highest_score >= 80:
                    if(debug): print(f"Fuzzy matched: '{song}' → '{best_match['name']}' ({highest_score}%)")
                    uris.append(best_match["uri"])
                else:
                    if(debug): 
                        print(f"{song} not found, even with fuzzy search.")
                    titleartist = f"{song} - {song_names[song]}"
                    # Add for metrics
                    notfound.append(titleartist)

            except Exception as e:
                print(f"Error with {song}: {e}")

        return uris

    # Creates a new private Spotify playlist and adds the found songs
    @staticmethod
    def create_spotify_playlist(sp: spotipy.Spotify, user_id: str, playlist_name: str, uris: list):
        playlist = sp.user_playlist_create(user=user_id, name=f"{playlist_name}", public=False)
        sp.playlist_add_items(playlist_id=playlist["id"], items=uris)

        print(f"Playlist '{playlist['name']}' created successfully!\nLive at: {playlist['external_urls']['spotify']}")
