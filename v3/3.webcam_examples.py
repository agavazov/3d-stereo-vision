import cv2
import numpy as np
import json
import os
import time
import winsound

config = json.loads(open('config.json', 'r').read())

pattern_size = (config['pattern_rows'], config['pattern_columns'])
preview_with = config['preview_width']
calibration_files_directory = config['examples_directory']
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
    key = cv2.waitKey(1)

    ret, img_left = camera_left.read()
    ret, img_right = camera_right.read()

    preview_left = img_left.copy()
    preview_right = img_right.copy()

    # Find chessboard
    if key & 0xFF == ord('s'):

        if not os.path.exists(calibration_files_directory):
            os.makedirs(calibration_files_directory)

        unix_time = int(time.time())
        cv2.imwrite(calibration_files_directory + '/' + str(unix_time) + '-left.png', img_left,
                    (cv2.IMWRITE_PNG_COMPRESSION, 8))
        cv2.imwrite(calibration_files_directory + '/' + str(unix_time) + '-right.png', img_right,
                    (cv2.IMWRITE_PNG_COMPRESSION, 8))
        winsound.Beep(2000, 300)

    # Preview
    preview_ration = float(preview_with) / float(img_left.shape[1])
    preview_left = cv2.resize(preview_left, None, fx=preview_ration, fy=preview_ration, interpolation=cv2.INTER_CUBIC)
    preview_right = cv2.resize(preview_right, None, fx=preview_ration, fy=preview_ration, interpolation=cv2.INTER_CUBIC)
    preview = np.hstack([preview_left, preview_right])
    cv2.imshow('Preview', preview)

    # Quit key
    if key & 0xFF == ord('q'):
        break

camera_left.release()
camera_right.release()
cv2.destroyAllWindows()
