import cv2
import numpy as np
import json
import os
import time
import winsound

config = json.loads(open('config.json', 'r').read())

auto_shooting_time = 5

pattern_size = (config['pattern_rows'], config['pattern_columns'])
preview_with = config['preview_width']
calibration_files_directory = config['calibration_files_directory']
camera_0_is_left = config['camera_0_is_left']
webcam_resolution_x = config['webcam_resolution_x']
webcam_resolution_y = config['webcam_resolution_y']
webcam_exposure = config['webcam_exposure']

if camera_0_is_left:
    camera_left = cv2.VideoCapture(1)
    camera_right = cv2.VideoCapture(0)
else:
    camera_left = cv2.VideoCapture(0)
    camera_right = cv2.VideoCapture(1)

camera_left.set(3, webcam_resolution_x)
camera_left.set(4, webcam_resolution_y)
camera_left.set(15, webcam_exposure)

camera_right.set(3, webcam_resolution_x)
camera_right.set(4, webcam_resolution_y)
camera_right.set(15, webcam_exposure)

ret_left = False
ret_right = False

while (True):
    key = cv2.waitKey(1)

    if ret_left and ret_right:
        time.sleep(1)

    ret, img_left = camera_left.read()
    ret, img_right = camera_right.read()

    preview_left = img_left.copy()
    preview_right = img_right.copy()

    shoot = False
    ret_left = False
    ret_right = False

    if key & 0xFF == ord('s'):
        shoot = False

    if auto_shooting_time > 0 and int(time.time()) % auto_shooting_time == 0:
        shoot = True

    # Find chessboard
    if shoot:
        winsound.Beep(2500, 150)

        check_img_left = cv2.cvtColor(img_left.copy(), cv2.COLOR_BGR2GRAY)
        check_img_right = cv2.cvtColor(img_right.copy(), cv2.COLOR_BGR2GRAY)

        ret_left, corners_left = cv2.findChessboardCorners(check_img_left, pattern_size)
        if ret_left:
            cv2.cornerSubPix(check_img_left, corners_left, (11, 11), (-1, -1),
                             (cv2.TERM_CRITERIA_MAX_ITER + cv2.TERM_CRITERIA_EPS, 30, 0.01))
            cv2.drawChessboardCorners(preview_left, pattern_size, corners_left, True)

        ret_right, corners_right = cv2.findChessboardCorners(check_img_right, pattern_size)
        if ret_right:
            cv2.cornerSubPix(check_img_right, corners_right, (11, 11), (-1, -1),
                             (cv2.TERM_CRITERIA_MAX_ITER + cv2.TERM_CRITERIA_EPS, 30, 0.01))
            cv2.drawChessboardCorners(preview_right, pattern_size, corners_right, True)

        if ret_left and ret_right:
            if not os.path.exists(calibration_files_directory):
                os.makedirs(calibration_files_directory)

            unix_time = int(time.time())
            cv2.imwrite(calibration_files_directory + '/' + str(unix_time) + '-left.png', img_left,
                        (cv2.IMWRITE_PNG_COMPRESSION, 8))
            cv2.imwrite(calibration_files_directory + '/' + str(unix_time) + '-right.png', img_right,
                        (cv2.IMWRITE_PNG_COMPRESSION, 8))
            winsound.Beep(1500, 150)

    # Preview
    preview_ration = float(preview_with) / float(img_left.shape[1])
    preview_left = cv2.resize(preview_left, None, fx=preview_ration, fy=preview_ration, interpolation=cv2.INTER_AREA)
    preview_right = cv2.resize(preview_right, None, fx=preview_ration, fy=preview_ration, interpolation=cv2.INTER_AREA)
    preview = np.hstack([preview_left, preview_right])
    cv2.imshow('Preview', preview)

    # Quit key
    if key & 0xFF == ord('q'):
        break

camera_left.release()
camera_right.release()
cv2.destroyAllWindows()
