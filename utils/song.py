import os
import subprocess
import time

import js2py
import requests
import tqdm
from bs4 import BeautifulSoup


class Song:
    """Song class

    Attributes:
    ----------
    title: str
        The title of the song
    artist: str
        The artist of the song
    year: str
        The year of the song
    poster_url: str
        The url of the poster of the song
    song_url: str
        The url of the song
    type: str
        The type of object
    """

    api_url = "https://www.jiosaavn.com/api.php"
    type = "song"

    def __init__(self, title: str, artist: str, year: str, poster_url: str):
        """Initialize the Song object.

        Parameters:
        ----------
        title: str
            The title of the song
        artist: str
            The artist of the song
        year: str
            The year of the song
        poster_url: str
            The url of the poster of the song

        Returns:
        -------
        Song
            The Song object.
        """
        self.title = title
        self.artist = artist
        self.year = year
        self.poster_url = poster_url
        self.song_url = None

    def get_url(self) -> str | None:
        """Get the url of the song.

        Returns:
        -------
        str
            The error message if any, else None.
        """
        params = {
            "__call": "autocomplete.get",
            "query": f"{self.title} {self.artist}",
            "_format": "json",
            "_marker": 0,
            "ctx": "web6dot0",
        }
        # Try thrice before throwing an error
        for i in range(4):
            try:
                resp = requests.get(self.api_url, params=params)
                resp.raise_for_status()
                break
            except Exception:
                if i == 3:
                    return
                print(
                    "\033[91m",  # Red foreground
                    "\033[40m",  # Black background
                    "Could not get song download url. Retrying...",
                    "\033[0m",  # Reset
                )
                time.sleep(5)
        data = resp.json()["songs"]["data"]
        if len(data) == 0:
            print(
                "\033[91m",  # Red foreground
                "\033[40m",  # Black background
                "No song found",
                "\033[0m",  # Reset
            )
            return
        song_url = data[0]["url"]
        self.song_url = song_url

    def download(self) -> None:
        """Download the song and its poster."""
        self.get_url()
        if self.song_url is None:
            print(
                "\033[91m",  # Red foreground
                "\033[40m",  # Black background
                "Could not download song",
                "\033[0m",  # Reset
            )
            return
        try:
            resp = requests.get(self.poster_url)
            resp.raise_for_status()
            with open(f"{self.title}.jpg", "wb") as f:
                f.write(resp.content)
        except Exception:
            print(
                "\033[91m",  # Red foreground
                "\033[40m",  # Black background
                "Could not download poster",
                "\033[0m",  # Reset
            )
        # Sometimes the song url is not available, so try 3 times
        for i in range(4):
            try:
                session = requests.Session()
                resp = session.get(self.song_url)
                resp.raise_for_status()
                soup = BeautifulSoup(resp.text, "html.parser")
                script_tag = soup.select_one("body > script:nth-child(5)")
                data = js2py.eval_js(script_tag.text).to_dict()
                encrypted_media_url = data["song"]["song"]["encrypted_media_url"]
                if data["song"]["song"]["has_lyrics"]:
                    lyrics = data["song"]["song"]["lyrics"]["content"]
                    lyrics = lyrics.replace("'", "").replace('"', "")
                else:
                    lyrics = ""
                params = {
                    "__call": "song.generateAuthToken",
                    "url": encrypted_media_url,
                    "bitrate": 320,
                    "api_version": 4,
                    "_format": "json",
                    "ctx": "web6dot0",
                    "_marker": 0,
                }
                resp = session.get(self.api_url, params=params)
                resp.raise_for_status()
                download_url = resp.json()["auth_url"]
                resp = session.get(download_url, stream=True)
                resp.raise_for_status()
                size = int(resp.headers.get("content-length"))
                f = open(f"{self.title}.m4a", "wb")
                for chunk in tqdm.tqdm(
                    resp.iter_content(chunk_size=1024),
                    total=(size // 1024),
                    colour="green",
                    unit="KB",
                    dynamic_ncols=True,
                ):
                    f.write(chunk)
                f.close()
                break
            except Exception as err:
                if i == 3:
                    return
                print(
                    "\033[91m",  # Red foreground
                    "\033[40m",  # Black background
                    "Trying again...",
                    err,
                    "\033[0m",  # Reset
                )
                time.sleep(5)
        if os.environ.get("FFMPEG") == "1":
            subprocess.run(
                f'ffmpeg -i "{self.title}.m4a" -acodec libmp3lame -ab 320k "{self.title}_mp3.mp3"',
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            os.remove(f"{self.title}.m4a")
            subprocess.run(
                f'ffmpeg -i "{self.title}_mp3.mp3" -i "{self.title}.jpg" -c copy -map 0 -map 1 -metadata title="{self.title}" -metadata year="{self.year}" -metadata artist="{self.artist}" -metadata lyrics="{lyrics}" "{self.title}.mp3"',
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            os.remove(f"{self.title}.jpg")
            os.remove(f"{self.title}_mp3.mp3")

    def __str__(self) -> str:
        """Return the string representation of the Song object."""
        return f"{self.title} by {self.artist} ({self.year}) - {self.poster_url}"


if __name__ == "__main__":
    song = Song(
        "Kabir",
        "Pritam, Tochi Raina, Rekha Bhardwaj",
        "2001",
        "https://i.scdn.co/image/ab67616d0000b273707ea5b8023ac77d31756ed4",
    )
    os.environ["FFMPEG"] = "1"
    print(f"Downloading {song.title} by {song.artist}")
    song.download()
