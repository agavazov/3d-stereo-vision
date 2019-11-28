import cv2
import json

config = json.loads(open('config.json', 'r').read())

camera_0_is_left = config['camera_0_is_left']
webcam_resolution_x = config['webcam_resolution_x']
webcam_resolution_y = config['webcam_resolution_y']

if camera_0_is_left:
    camera_left = cv2.VideoCapture(1)
    camera_right = cv2.VideoCapture(0)
else:
    camera_left = cv2.VideoCapture(0)
    camera_right = cv2.VideoCapture(1)

camera_left.set(3, webcam_resolution_x)
camera_left.set(4, webcam_resolution_y)

camera_right.set(3, webcam_resolution_x)
camera_right.set(4, webcam_resolution_y)

while (True):
    ret, frame_left = camera_left.read()
    ret, frame_right = camera_right.read()

    cv2.imshow('frame_left', frame_left)
    cv2.imshow('frame_right', frame_right)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

camera_left.release()
camera_right.release()
cv2.destroyAllWindows()
