import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

from utils.content import Collection
from utils.song import Song


def search(query: str):
    """Search for a song on Spotify.

    Parameters:
    ----------
    query: str
        The query to search for.
    Returns:
    -------
    list[Song, Collection]
        The results of the search.
    """
    auth_manager = SpotifyClientCredentials()
    sp = spotipy.Spotify(auth_manager=auth_manager)
    filtered_results = []
    unfiltered_results = sp.search(q=query, type="track,album,playlist", limit=5)
    tracks = unfiltered_results["tracks"]["items"]
    albums = unfiltered_results["albums"]["items"]
    playlists = unfiltered_results["playlists"]["items"]
    for track in tracks:
        filtered_results.append(
            Song(
                track["name"],
                ", ".join([artist["name"] for artist in track["artists"]]),
                track["album"]["release_date"],
                track["album"]["images"][0]["url"],
            )
        )
    for album in albums:
        filtered_results.append(
            Collection(
                album["name"],
                album["id"],
                "album",
                ", ".join([artist["name"] for artist in album["artists"]]),
                album["release_date"][:4],
            )
        )
    for playlist in playlists:
        filtered_results.append(
            Collection(
                playlist["name"],
                playlist["id"],
                "Playlist",
                playlist["owner"]["display_name"],
            )
        )
    return filtered_results


def get_collection_tracks(album_id: str):
    """Get the tracks of an album.

    Parameters:
    ----------
    album_id: str
        The ID of the album.

    Returns:
    -------
    list[Song]
        The tracks of the album.
    """
    auth_manager = SpotifyClientCredentials()
    sp = spotipy.Spotify(auth_manager=auth_manager)
    tracks = sp.album_tracks(album_id)
    # print(tracks['items'][1])
    filtered_results = []
    for track in tracks["items"]:
        info = sp.track(track["id"])
        filtered_results.append(
            Song(
                track["name"],
                track["artists"][0]["name"],
                info["album"]["release_date"],
                info["album"]["images"][0]["url"],
            )
        )
    return filtered_results
