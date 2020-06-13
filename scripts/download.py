import requests
from pytube import Playlist
from pytube import YouTube

from scripts import globalVars

####################################################################################
# This script contains methods to download video or audio from youtube or given URL
####################################################################################
to_download = []
voice = None


def download_youtube_video(link: str):
    vid = YouTube(link)
    file_name = "sample"
    file_loc = globalVars.tmp_videos_loc + file_name
    streams = vid.streams.filter(progressive=True, file_extension='mp4')
    streams.order_by('resolution').desc().first().download(globalVars.tmp_videos_loc, file_name)

    return f"{file_loc}.mp4"


def download_youtube_audio(link: str):
    try:
        vid = YouTube(link)
        streams = vid.streams.filter(only_audio=True)
        file_loc = streams[0].download(globalVars.tmp_sounds_loc)
    except:
        print(f"ERROR: downloading {link} failed!")
        return None
    return f"{file_loc}"


def get_youtube_playlist_urls(link: str):
    try:
        playlist = Playlist(link)
        print(f"Number of videos in playlist: {len(playlist.video_urls)}")
        urls = playlist.video_urls
    except:
        print(f"ERROR: downloading {link} failed!")
        return None
    return urls


def download_from_url(url, file_loc):
    # Read the gif from the web, save to the disk
    file = requests.get(url)
    open(file_loc, "wb").write(file.content)
