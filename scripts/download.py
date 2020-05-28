# pylint: disable=fixme, import-error
from scripts import globalVars
from pytube import YouTube
from pytube import Playlist
import requests

####################################################################################
# This script contains methods to download video or audio from youtube or given URL
####################################################################################

def download_youtube_video(link: str):
    vid = YouTube(link)
    file_name = "sample"
    file_loc = globalVars.tmp_videos_loc + file_name
    if vid.streams.filter(progressive=True).get_by_resolution("720p") is None:
        vid.streams.filter(progressive=True).get_highest_resolution().download(globalVars.tmp_videos_loc, file_name)
    else:
        vid.streams.filter(progressive=True).get_by_resolution("720p").download(globalVars.tmp_videos_loc, file_name)

    return f"{file_loc}.mp4"
"""
def download_youtube_playlist(link:str):
    playlist = Playlist(link)
    print(f"Number of videos in playlist: {len(playlist.video_urls)}")
    playlist.
    playlist.download_all()
"""
def download_youtube_audio(link: str):
    file_name = ''.join(e for e in link if e.isalnum())
    file_loc = globalVars.tmp_sounds_loc
    try:
        vid = YouTube(link)
        vid.streams.get_audio_only().download(file_loc, file_name)
    except:
        print(f"ERROR: downloading {link} failed!")
        return None

    print(f"{file_loc}{file_name}.mp4")
    return f"{file_loc}{file_name}.mp4"


def download_from_url(url, file_loc):
    # Read the gif from the web, save to the disk
    file = requests.get(url)
    open(file_loc, "wb").write(file.content)