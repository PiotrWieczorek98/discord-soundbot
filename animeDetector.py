import cv2
import os.path
import globalVar
import requests
import imageio
from acrcloud import ACRcloud
from pytube import YouTube


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

    if len(faces) > 0:
        return True
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
            image_loc = globalVar.images_loc + str(current_frame) + ".jpg"
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
    detected_anime = False
    config = {
        'host': 'http://identify-eu-west-1.acrcloud.com',
        'key': 'a840dd31ba72330c4ddc1780b156a195',
        'secret': 'wk35b7rB2aRGib2p3OMcLZh8pth6z24D9bd0AW9i',
        'debug': True,
        'timeout': 10
    }
    acr = ACRcloud(config)
    metadata = acr.recognizer(file_loc)

    print(metadata)
    for entry in globalVar.weeb_songs:
        if entry in str(metadata).casefold():
            detected_anime = True
            break

    for entry in globalVar.weeb_songs:
        if entry in str(metadata):
            detected_anime = True
            break

    return detected_anime


def detect_anime_gif(file_loc: str):
    detected_anime = False
    # Read the gif from disk to `RGB`s
    gif = imageio.mimread(file_loc)
    frames_total = len(gif)

    # convert form RGB to BGR
    images = [cv2.cvtColor(img, cv2.COLOR_RGB2BGR) for img in gif]

    ## Check the gif
    current_frame = 0
    frame_images = []
    while current_frame < frames_total:
        image_loc = globalVar.images_loc + str(current_frame) + ".jpg"
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


def download_youtube(link: str):
    vid = YouTube(link)
    file_name = "sample"
    file_loc = globalVar.images_loc + file_name
    if vid.streams.filter(progressive=True).get_by_resolution("720p") is None:
        vid.streams.filter(progressive=True).get_highest_resolution().download(globalVar.images_loc, file_name)
    else:
        vid.streams.filter(progressive=True).get_by_resolution("720p").download(globalVar.images_loc, file_name)

    return file_loc + ".mp4"


def download_url(url, file_loc):
    # Read the gif from the web, save to the disk
    myfile = requests.get(url)
    open(file_loc, "wb").write(myfile.content)
