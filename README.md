<p align="center">
<img src="https://i.imgur.com/FtxtRAs.jpg"/>
</p>

# TuneFetch

## Description

A simple TUI application to download Spotify tracks, albums and playlists.

## Installation

```bash
git clone https://github.com/iaaryanraj/TuneFetch.git
cd TuneFetch
pip install -r requirements.txt
```

`FFmpeg` is not necessary for the application to work. It is only used to convert the downloaded `*.m4a` file to `*.mp3` file and add meta data like album art, artist details.

For Windows users, just copy the `ffmpeg.exe` file from the `ffmpeg` folder to the `SYSTEM32` folder.

For Linux users, run the following command to install `FFmpeg`:

```bash
sudo apt install ffmpeg
```

## Usage

```bash
python TuneFetch.py
```

Enter the song/album/playlist name and press `Enter` to search. Select the songs, albums and playlists to download from the dialog that appears and click `Ok` to download.

## Features

- [x] Download Spotify tracks, albums and playlists
- [x] No annoying ads or popups
- [x] Download in 320kbps
- [x] Automatically adds meta data like album art, artist details, and lyrics

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change

## Warning

This project is for educational purposes only. I am not responsible for any misuse of this project.
