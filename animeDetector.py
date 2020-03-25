import cv2
import os.path
import globalVar


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

    # frame
    currentframe = 0
    while True:
        # reading from frame
        ret, frame = cam.read()

        if ret:
            # if video is still left continue creating images
            image_loc = globalVar.images_loc + str(currentframe) + ".jpg"
            # writing the extracted images
            cv2.imwrite(image_loc, frame)
            # Check if anime
            detected_anime = detect_anime_image(image_loc)
            # Clean
            os.remove(image_loc)
            if detected_anime:
                break
            # increasing counter so that it will
            # show how many frames are created
            currentframe += 24
        else:
            break

    # Release all space and windows once done
    cam.release()
    cv2.destroyAllWindows()

    return detected_anime