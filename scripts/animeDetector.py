import os.path
import imageio
import requests
from acrcloud import ACRcloud
from cv2 import cv2
from pytube import YouTube

# pylint: disable=fixme, import-error
from scripts import globalVar


# detect anime face disabled for a while
def detect_anime_image(filename, cascade_file="lbpcascade_animeface.xml"):
    if not os.path.isfile(cascade_file):
        raise RuntimeError("%s: not found" % cascade_file)

    cascade = cv2.CascadeClassifier(cascade_file)
    image = cv2.imread(filename, cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)

    faces = cascade.detectMultiScale(gray,
                                     # detector options
                                     scaleFactor=1.1,
                                     minNeighbors=5,
                                     minSize=(24, 24))

    # if len(faces) > 0:
    #   return True
    return False


def detect_anime_video(vid_loc):
    detected_anime = False
    # Read the video from specified path
    cam = cv2.VideoCapture(vid_loc)

    try:
        # creating a folder named data
        if not os.path.exists('data'):
            os.makedirs('data')

        # if not created then raise error
    except OSError:
        print('Error: Creating directory of data')

    # frame and frame cap
    fps = cam.get(cv2.CAP_PROP_FPS)
    frame_count = int(cam.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = frame_count / fps
    if duration > 60:
        max_frame = int(fps * 60)
        step = int(fps * 10)
    elif 30 < duration < 60:
        max_frame = frame_count
        step = int(fps)
    elif 5 < duration < 30:
        max_frame = frame_count
        step = int(fps / 4)
    else:
        max_frame = frame_count
        step = int(5)

    current_frame = 0
    image_loc = ""
    frame_images = []
    while current_frame <= max_frame:
        # reading from frame
        cam.set(1, current_frame)
        ret, frame = cam.read()

        if ret:
            # if video is still left continue creating images
            image_loc = f"{globalVar.images_loc}{current_frame}.jpg"
            frame_images.append(image_loc)
            # writing the extracted images
            cv2.imwrite(image_loc, frame)
            # Check if anime
            detected_anime = detect_anime_image(image_loc)
            if detected_anime:
                break
            # increasing counter so that it will
            # show how many frames are created
            current_frame += step
        else:
            break

    # Release all space and windows once done
    cam.release()
    cv2.destroyAllWindows()
    # Clean
    for entry in frame_images:
        os.remove(entry)

    return detected_anime


def detect_anime_music(file_loc):
    # result: 0 - not detected, 1 - detected anime, 2 - detected jojo
    result = 0
    config = {
        'host': 'http://identify-eu-west-1.acrcloud.com',
        'key': 'a840dd31ba72330c4ddc1780b156a195',
        'secret': 'wk35b7rB2aRGib2p3OMcLZh8pth6z24D9bd0AW9i',
        'debug': True,
        'timeout': 10
    }
    acr = ACRcloud(config)
    metadata = acr.recognizer(file_loc)

    print("\n METADATA:")
    print(metadata)
    for entry in globalVar.jojo_reference:
        if entry in str(metadata).casefold():
            result = 2
            break

    if result == 0:
        for entry in globalVar.weeb_songs:
            if entry in str(metadata).casefold():
                result = 1
                break

        for entry in globalVar.weeb_letters:
            if entry in str(metadata).casefold():
                result = 1
                break

    return result


def detect_anime_gif(file_loc: str):
    detected_anime = False
    # Read the gif from disk to `RGB`s
    gif = imageio.mimread(file_loc)
    frames_total = len(gif)

    # convert form RGB to BGR
    images = [cv2.cvtColor(img, cv2.COLOR_RGB2BGR) for img in gif]

    # Check the gif
    current_frame = 0
    frame_images = []
    while current_frame < frames_total:
        image_loc = f"{globalVar.tmp_images_loc}{current_frame}.jpg"
        frame_images.append(image_loc)
        cv2.imwrite(image_loc, images[current_frame])
        # Check if anime
        detected_anime = detect_anime_image(image_loc)
        if detected_anime:
            break
        # increasing counter so that it will
        current_frame += 12

    # Release all space and windows once done
    cv2.destroyAllWindows()
    # Clean
    for entry in frame_images:
        os.remove(entry)
    os.remove(file_loc)

    return detected_anime


def download_youtube_video(link: str):
    vid = YouTube(link)
    file_name = "sample"
    file_loc = globalVar.tmp_videos_loc + file_name
    if vid.streams.filter(progressive=True).get_by_resolution("720p") is None:
        vid.streams.filter(progressive=True).get_highest_resolution().download(globalVar.tmp_videos_loc, file_name)
    else:
        vid.streams.filter(progressive=True).get_by_resolution("720p").download(globalVar.tmp_videos_loc, file_name)

    return f"{file_loc}.mp4"


def download_youtube_audio(link: str):
    file_name = ''.join(e for e in link if e.isalnum())
    file_loc = globalVar.tmp_sounds_loc
    try:
        vid = YouTube(link)
        vid.streams.get_audio_only().download(file_loc, file_name)
    except:
        print(f"ERROR: downloading {link} failed!")
        return None

    print(f"{file_loc}{file_name}.mp4")
    return f"{file_loc}{file_name}.mp4"


def download_url(url, file_loc):
    # Read the gif from the web, save to the disk
    file = requests.get(url)
    open(file_loc, "wb").write(file.content)


def load_lists():
    file_names = [globalVar.weeb_songs_txt, globalVar.weeb_letters_txt, globalVar.jojo_reference_txt]
    list_names = [globalVar.weeb_songs, globalVar.weeb_letters, globalVar.jojo_reference]

    for i in range(len(list_names)):
        file = open(globalVar.txt_loc + file_names[i], encoding='utf-8')
        lines = file.read().splitlines()

        for line in lines:
            list_names[i].append(line)

        file.close()
        print(f"{file_names[i]} list loaded")
