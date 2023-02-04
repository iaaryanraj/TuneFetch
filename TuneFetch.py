import json
import os
import subprocess

from prompt_toolkit import print_formatted_text as print
from prompt_toolkit import prompt
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.shortcuts import checkboxlist_dialog, set_title
from prompt_toolkit.styles import Style
from prompt_toolkit.validation import Validator

from utils.content import Collection
from utils.song import Song
from utils.spotify import get_collection_tracks, search

# Set the title of the terminal.
set_title("TuneFetch | v1.0")

# Clear the screen.
os.system("cls" if os.name == "nt" else "clear")


# Global style
style = Style.from_dict(
    {
        # Default style for user input.
        "": "fg:yellow",
        # Default style for prompt.
        "prompt": "fg:cyan bg:black bold",
        # Style for the logo.
        "logo": "fg:purple bg:black bold",
        # Style for the error message.
        "error": "fg:red bg:black bold",
        # Style for text that shows a loading state.
        "loading": "fg:green bg:black italic",
        # Style for the info text.
        "info": "fg:white bg:black bold",
        # Style for the warning text.
        "warning": "fg:yellow bg:black bold",
    }
)


# Dialog style
dialog_style = Style.from_dict(
    {
        "dialog": "bg:blue",
        "dialog frame.label": "bg:#ffffff #000000",
        "dialog.body": "bg:#000000 yellow",
    }
)


# Validator for the name prompt
validator = Validator.from_callable(
    lambda text: text.strip() != "",
    error_message="Please enter a valid search term",
    move_cursor_to_end=True,
)


# The logo.
logo = """
  _______               ______   _       _     
 |__   __|             |  ____| | |     | |    
    | |_   _ _ __   ___| |__ ___| |_ ___| |__  
    | | | | | '_ \ / _ \  __/ _ \ __/ __| '_ \ 
    | | |_| | | | |  __/ | |  __/ || (__| | | |
    |_|\__,_|_| |_|\___|_|  \___|\__\___|_| |_|
"""


def get_download_choice(
    results: dict[int, Song | Collection]
) -> (Song | Collection) | None:
    """Get the user's choice of seasons and episodes to download.

    Parameters:
        results (dict[int, Song|Collection]): The search results.

    Returns:
        (Song | Collection) | None: The user's choice of songs, albums or playlists to download.
    """
    values = []
    for result in results:
        values.append(
            (
                result,
                f"{results[result].title} | {results[result].year} | {results[result].artist} | {results[result].type}",
            )
        )
    checkbox = checkboxlist_dialog(
        title="Select the songs, albums or playlists to download",
        values=values,
        ok_text="Download",
        cancel_text="Cancel",
        style=dialog_style,
    )
    checkbox.mouse_support = True
    download_choice = checkbox.run()
    if download_choice is None or download_choice == []:
        return download_choice
    else:
        return download_choice


def main():
    # Print the logo.
    print(HTML(f"<logo>{logo}</logo>"), style=style)

    # Load config file.
    try:
        with open("config.json", "r") as f:
            config = json.load(f)
            os.environ["SPOTIPY_CLIENT_ID"] = config["SPOTIPY_CLIENT_ID"]
            os.environ["SPOTIPY_CLIENT_SECRET"] = config["SPOTIPY_CLIENT_SECRET"]
    except FileNotFoundError:
        print(
            HTML(
                "<error>config.json not found! Please create one with your Spotify client ID and secret</error>"
            ),
            style=style,
        )
        exit()
    except KeyError:
        print(
            HTML(
                "<error>config.json is missing one or more keys! Please make sure it contains your Spotify client ID and secret</error>"
            ),
            style=style,
        )
        exit()

    # Check if ffmpeg is installed.
    try:
        subprocess.run("ffmpeg", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        os.environ["FFMPEG"] = "1"
    except FileNotFoundError:
        print(
            HTML(
                "<warning>FFmpeg not found! Final file won't be converted to mp3 and meta data won't be added</warning>"
            ),
            style=style,
        )

    if not os.path.exists("Downloads"):
        os.mkdir("Downloads")
    os.chdir("Downloads")

    # Ask for the song's name.
    query = prompt(
        HTML("<prompt>Enter the name of a song, album or playlist: </prompt> "),
        style=style,
        validator=validator,
    )
    unfiltered_results = search(query)
    results = {}
    for result in enumerate(unfiltered_results):
        results[result[0]] = result[1]
    download_choices = get_download_choice(results)
    if download_choices in (None, []):
        print(HTML("<info>Exiting...</info>"), style=style)
        exit()
    for download_choice in download_choices:
        if results[download_choice].type == "song":
            print(
                HTML(
                    f"<info>Downloading <u>{results[download_choice].title}</u>...</info>"
                ),
                style=style,
            )
            results[download_choice].download()
            print(
                HTML(
                    f"<info>Downloaded <u>{results[download_choice].title}</u>!</info>"
                ),
                style=style,
            )
        else:
            if os.path.exists(results[download_choice].title):
                os.chdir(results[download_choice].title)
            else:
                os.mkdir(results[download_choice].title)
                os.chdir(results[download_choice].title)
            print(HTML(f"<info>Getting tracks from the {results[download_choice].type} {results[download_choice].title}</info>"), style=style)
            results[download_choice].set_songs(
                get_collection_tracks(results[download_choice].id)
            )
            for song in results[download_choice].songs:
                print(
                    HTML(f"<info>Downloading <u>{song.title}</u>...</info>"),
                    style=style,
                )
                song.download()
                print(
                    HTML(f"<info>Downloaded <u>{song.title}</u>!</info>"), style=style
                )
            print("\n" * 2)
            os.chdir("..")


if __name__ == "__main__":
    main()
