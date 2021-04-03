import cv2
import os 
os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;udp"

URL = "udp://192.168.0.60:5000?overrun_nonfatal=1"
DETECTION_RATE = 1
FACE_RECT_COLOR = (255, 0, 0)
PROFILE_RECT_COLOR = (0, 255, 0)
EYE_RECT_COLOR = (0, 0, 255)
BODY_RECT_COLOR = (0, 255, 255)

face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
profile_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')

def detectObjects(classifier, img, scale_fact, min_neigh):
    objects = classifier.detectMultiScale(gray, scale_fact, min_neigh)
    return objects

def drawRectangles(objects_coord, img, color):
    for (x,y,w,h) in objects_coord:
        cv2.rectangle(img, (x,y), (x + w, y + h), color, 2)

vcap = cv2.VideoCapture(URL, cv2.CAP_FFMPEG)
if not vcap.isOpened():
    print("Video capture not found")
    exit(-1)

i = 0
faces = []
profiles = []
eyes = []
body = []
while(1):
    ret, frame = vcap.read()
    if ret == True:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if i == DETECTION_RATE:
            faces = detectObjects(face_cascade, gray, 1.1, 8)
            #profiles = detectObjects(profile_cascade, gray, 1.1, 8)
            #eyes = detectObjects(eye_cascade, frame, 1.1, 4)
            i = 0
        drawRectangles(faces, frame, FACE_RECT_COLOR)
        drawRectangles(profiles, frame, PROFILE_RECT_COLOR)
        drawRectangles(eyes, frame, EYE_RECT_COLOR)
        frame = cv2.resize(frame, (1920,1080))
        cv2.imshow('VIDEO', frame)
        i += 1
    cv2.waitKey(1)
