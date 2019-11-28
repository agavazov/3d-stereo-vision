import cv2
import numpy as np
import json
import os
import time
import glob
import winsound

config = json.loads(open('config.json', 'r').read())

pattern_size = (config['pattern_rows'], config['pattern_columns'])
preview_with = config['preview_width']
camera_files_0 = config['temporary_directory'] + "*-0.pgm"
camera_files_1 = config['temporary_directory'] + "*-1.pgm"
calibration_files_directory = config['calibration_files_directory']
camera_0_is_left = config['camera_0_is_left']
rotate_left = config['rotate_left']
rotate_right = config['rotate_right']

while (True):
    time.sleep(0.01)
    key = cv2.waitKey(1)

    # Get files except last 2 files
    files_0 = glob.glob(camera_files_0)[:-1]
    files_1 = glob.glob(camera_files_1)[:-1]
    print (files_0)

    # Check minimal files number
    if (len(files_0) + len(files_1) < 2):
        continue

    # Group images
    file_groups = []
    for file_0 in files_0:
        check_0 = file_0.replace('-0.', '')
        for file_1 in files_1:
            check_1 = file_1.replace('-1.', '')
            if check_0 == check_1:
                file_groups.append([file_0, file_1])

    # Get last taken photos for preview
    if camera_0_is_left:
        file_left, file_right = file_groups[-1]
    else:
        file_right, file_left = file_groups[-1]


    img_left = cv2.imread(file_left)
    img_right = cv2.imread(file_right)

    if img_left is None or img_right is None:
        continue

    img_left = cv2.cvtColor(img_left, cv2.COLOR_BGR2GRAY)
    img_right = cv2.cvtColor(img_right, cv2.COLOR_BGR2GRAY)

    if rotate_left:
        img_left = cv2.flip(img_left, 1)
        img_left = cv2.flip(img_left, 0)

    if rotate_right:
        img_right = cv2.flip(img_right, 1)
        img_right = cv2.flip(img_right, 0)

    preview_left = img_left.copy()
    preview_right = img_right.copy()

    # Find chessboard
    if key & 0xFF == ord('s'):
        winsound.Beep(2500, 150)

        ret_left, corners_left = cv2.findChessboardCorners(preview_left, pattern_size)
        if ret_left:
            cv2.cornerSubPix(preview_left, corners_left, (11, 11), (-1, -1),
                             (cv2.TERM_CRITERIA_MAX_ITER + cv2.TERM_CRITERIA_EPS, 30, 0.01))
            cv2.drawChessboardCorners(preview_left, pattern_size, corners_left, True)

        ret_right, corners_right = cv2.findChessboardCorners(preview_right, pattern_size)
        if ret_right:
            cv2.cornerSubPix(preview_right, corners_right, (11, 11), (-1, -1),
                             (cv2.TERM_CRITERIA_MAX_ITER + cv2.TERM_CRITERIA_EPS, 30, 0.01))
            cv2.drawChessboardCorners(preview_right, pattern_size, corners_right, True)

        if ret_left and ret_right:
            if not os.path.exists(calibration_files_directory):
                os.makedirs(calibration_files_directory)

            unix_time = int(time.time())
            cv2.imwrite(calibration_files_directory + '/' + str(unix_time) + '-left.pgm', img_left)
            cv2.imwrite(calibration_files_directory + '/' + str(unix_time) + '-right.pgm', img_right)
            winsound.Beep(1500, 150)

    # Preview
    preview_ration = float(preview_with) / float(img_left.shape[1])
    preview_left = cv2.resize(preview_left, None, fx=preview_ration, fy=preview_ration, interpolation=cv2.INTER_CUBIC)
    preview_right = cv2.resize(preview_right, None, fx=preview_ration, fy=preview_ration, interpolation=cv2.INTER_CUBIC)
    preview = np.hstack([preview_left, preview_right])
    cv2.imshow('Preview', preview)

    # Delete all photos
    for file_0, file_1 in zip(files_0, files_1):
        for file in [file_0, file_1]:
            try:
                os.remove(file)
            except OSError:
                pass

    # Quit key
    if key & 0xFF == ord('q'):
        break
