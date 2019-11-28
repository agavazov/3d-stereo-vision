import cv2
import numpy as np
import json

config = json.loads(open('config.json', 'r').read())

preview_with = config['preview_width']
webcam_resolution_x = config['webcam_resolution_x']
webcam_resolution_y = config['webcam_resolution_y']

camera_from = cv2.VideoCapture(0)
camera_to = cv2.VideoCapture(1)

camera_from.set(3, webcam_resolution_x)
camera_from.set(4, webcam_resolution_y)

camera_to.set(3, webcam_resolution_x)
camera_to.set(4, webcam_resolution_y)

for setting_id in range(0, 100):
    value = camera_from.get(setting_id)
    if value != -1:
        camera_from.set(setting_id, value)
        camera_to.set(setting_id, value)

while (True):
    key = cv2.waitKey(1)

    ret, img_from = camera_from.read()
    ret, img_to = camera_to.read()

    # Preview
    preview_ration = float(preview_with) / float(img_from.shape[1])
    preview_left = cv2.resize(img_from, None, fx=preview_ration, fy=preview_ration, interpolation=cv2.INTER_CUBIC)
    preview_right = cv2.resize(img_to, None, fx=preview_ration, fy=preview_ration, interpolation=cv2.INTER_CUBIC)
    preview = np.hstack([preview_left, preview_right])
    cv2.imshow('Preview', preview)

    # Quit key
    if key & 0xFF == ord('q'):
        break

camera_from.release()
camera_to.release()
cv2.destroyAllWindows()
