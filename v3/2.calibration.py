import cv2
import numpy as np
import json
import glob
import os

config = json.loads(open('config.json', 'r').read())

pattern_size = (config['pattern_rows'], config['pattern_columns'])
square_size_mm = config['square_size_mm']
calibration_data_directory = config['calibration_data_directory']
files_left = glob.glob(config['calibration_files_directory'] + "*-left.png")
files_right = glob.glob(config['calibration_files_directory'] + "*-right.png")

################

height, width = cv2.imread(files_left[0]).shape[:2]
image_size = (width, height)

criteria = (cv2.TERM_CRITERIA_MAX_ITER + cv2.TERM_CRITERIA_EPS, square_size_mm, 0.00001)
flags = (cv2.CALIB_FIX_ASPECT_RATIO + cv2.CALIB_ZERO_TANGENT_DIST + cv2.CALIB_SAME_FOCAL_LENGTH)

################

object_points = []
image_points = {"left": [], "right": []}
image_count = 0

# Group images
groups = []
for file_left in files_left:
    check_left = file_left.replace('-left', '')
    for file_right in files_right:
        check_right = file_right.replace('-right', '')
        if check_left == check_right:
            #groups.append([file_left, file_right])
            groups.append([file_right, file_left])

################

corner_coordinates = np.zeros((np.prod(pattern_size), 3), np.float32)
corner_coordinates[:, :2] = np.indices(pattern_size).T.reshape(-1, 2)
corner_coordinates *= (square_size_mm / 10)

#corner_coordinates = np.zeros((10 * 7, 3), np.float32)
#corner_coordinates[:, :2] = np.mgrid[0:600:7j, 0:900:10j].T.reshape(-1, 2)

################

for files in groups:
    print('Read files ', files)

    img_left, im_right = cv2.imread(files[0]), cv2.imread(files[1])

    side = "left"
    object_points.append(corner_coordinates)
    for image in (img_left, im_right):
        temp = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        ret, corners = cv2.findChessboardCorners(temp, pattern_size)
        cv2.cornerSubPix(temp, corners, (11, 11), (-1, -1), criteria)

        if False:
            temp = image
            cv2.drawChessboardCorners(temp, pattern_size, corners, True)
            window_name = "Chessboard"
            cv2.imshow(window_name, temp)
            if cv2.waitKey(0):
                cv2.destroyWindow(window_name)

        image_points[side].append(corners.reshape(-1, 2))
        side = "right"
        image_count += 1

####################

print('Start calibration')

#
cam_mats = {"left": None, "right": None}
dist_coefs = {"left": None, "right": None}
rot_mat = None
trans_vec = None
e_mat = None
f_mat = None
#
rect_trans = {"left": None, "right": None}
proj_mats = {"left": None, "right": None}
disp_to_depth_mat = None
valid_boxes = {"left": None, "right": None}
#
undistortion_map = {"left": None, "right": None}
rectification_map = {"left": None, "right": None}
#

(cam_mats["left"], dist_coefs["left"],
 cam_mats["right"], dist_coefs["right"],
 rot_mat, trans_vec, e_mat,
 f_mat) = cv2.stereoCalibrate(object_points,
                              image_points["left"],
                              image_points["right"],
                              cam_mats["left"],
                              dist_coefs["left"],
                              cam_mats["right"],
                              dist_coefs["right"],
                              image_size,
                              rot_mat,
                              trans_vec,
                              e_mat,
                              f_mat,
                              criteria=criteria,
                              flags=flags)[1:]

(rect_trans["left"], rect_trans["right"],
 proj_mats["left"], proj_mats["right"],
 disp_to_depth_mat, valid_boxes["left"],
 valid_boxes["right"]) = cv2.stereoRectify(cam_mats["left"],
                                           dist_coefs["left"],
                                           cam_mats["right"],
                                           dist_coefs["right"],
                                           image_size,
                                           rot_mat,
                                           trans_vec,
                                           flags=0)
for side in ("left", "right"):
    (undistortion_map[side],
     rectification_map[side]) = cv2.initUndistortRectifyMap(
        cam_mats[side],
        dist_coefs[side],
        rect_trans[side],
        proj_mats[side],
        image_size,
        cv2.CV_32FC1)
# This is replaced because my results were always bad. Estimates are
# taken from the OpenCV samples.
width, height = image_size
focal_length = 0.8 * width
disp_to_depth_mat = np.float32([[1, 0, 0, -0.5 * width],
                                [0, -1, 0, 0.5 * height],
                                [0, 0, 0, -focal_length],
                                [0, 0, 1, 0]])

############### check_calibration(self, calibration):
sides = "left", "right"
which_image = {sides[0]: 1, sides[1]: 2}
undistorted, lines = {}, {}
for side in sides:
    undistorted[side] = cv2.undistortPoints(
        np.concatenate(image_points[side]).reshape(-1,
                                                   1, 2),
        cam_mats[side],
        dist_coefs[side],
        P=cam_mats[side])
    lines[side] = cv2.computeCorrespondEpilines(undistorted[side],
                                                which_image[side],
                                                f_mat)
total_error = 0
this_side, other_side = sides
for side in sides:
    for i in range(len(undistorted[side])):
        total_error += abs(undistorted[this_side][i][0][0] *
                           lines[other_side][i][0][0] +
                           undistorted[this_side][i][0][1] *
                           lines[other_side][i][0][1] +
                           lines[other_side][i][0][2])
    other_side, this_side = sides
total_points = image_count * len(object_points)

print("ERROR: ", format(total_error / total_points))

######################
##### save


if not os.path.exists(calibration_data_directory):
    os.makedirs(calibration_data_directory)

np.save(calibration_data_directory + 'e_mat.npy', e_mat)
np.save(calibration_data_directory + 'f_mat.npy', f_mat)
np.save(calibration_data_directory + 'disp_to_depth_mat.npy', disp_to_depth_mat)
np.save(calibration_data_directory + 'rot_mat.npy', rot_mat)
np.save(calibration_data_directory + 'trans_vec.npy', trans_vec)

np.save(calibration_data_directory + 'cam_mats_left.npy', cam_mats['left'])
np.save(calibration_data_directory + 'cam_mats_right.npy', cam_mats['right'])
np.save(calibration_data_directory + 'dist_coefs_left.npy', dist_coefs['left'])
np.save(calibration_data_directory + 'dist_coefs_right.npy', dist_coefs['right'])
np.save(calibration_data_directory + 'proj_mats_left.npy', proj_mats['left'])
np.save(calibration_data_directory + 'proj_mats_right.npy', proj_mats['right'])
np.save(calibration_data_directory + 'rect_trans_left.npy', rect_trans['left'])
np.save(calibration_data_directory + 'rect_trans_right.npy', rect_trans['right'])
np.save(calibration_data_directory + 'rectification_map_left.npy', rectification_map['left'])
np.save(calibration_data_directory + 'rectification_map_right.npy', rectification_map['right'])
np.save(calibration_data_directory + 'undistortion_map_left.npy', undistortion_map['left'])
np.save(calibration_data_directory + 'undistortion_map_right.npy', undistortion_map['right'])
np.save(calibration_data_directory + 'valid_boxes_left.npy', valid_boxes['left'])
np.save(calibration_data_directory + 'valid_boxes_right.npy', valid_boxes['right'])
