import cv2
import numpy as np
import json
import time

config = json.loads(open('config.json', 'r').read())

calibration_data_directory = config['calibration_data_directory']

####################

ply_header = (
    '''ply
    format ascii 1.0
    element vertex {vertex_count}
    property float x
    property float y
    property float z
    property uchar red
    property uchar green
    property uchar blue
    end_header
    ''')

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

cam_mats['left'] = np.load(calibration_data_directory + 'cam_mats_left.npy')
cam_mats['right'] = np.load(calibration_data_directory + 'cam_mats_right.npy')
disp_to_depth_mat = np.load(calibration_data_directory + 'disp_to_depth_mat.npy')
dist_coefs['left'] = np.load(calibration_data_directory + 'dist_coefs_left.npy')
dist_coefs['right'] = np.load(calibration_data_directory + 'dist_coefs_right.npy')
e_mat = np.load(calibration_data_directory + 'e_mat.npy')
f_mat = np.load(calibration_data_directory + 'f_mat.npy')
proj_mats['left'] = np.load(calibration_data_directory + 'proj_mats_left.npy')
proj_mats['right'] = np.load(calibration_data_directory + 'proj_mats_right.npy')
rect_trans['left'] = np.load(calibration_data_directory + 'rect_trans_left.npy')
rect_trans['right'] = np.load(calibration_data_directory + 'rect_trans_right.npy')
rectification_map['left'] = np.load(calibration_data_directory + 'rectification_map_left.npy')
rectification_map['right'] = np.load(calibration_data_directory + 'rectification_map_right.npy')
rot_mat = np.load(calibration_data_directory + 'rot_mat.npy')
trans_vec = np.load(calibration_data_directory + 'trans_vec.npy')
undistortion_map['left'] = np.load(calibration_data_directory + 'undistortion_map_left.npy')
undistortion_map['right'] = np.load(calibration_data_directory + 'undistortion_map_right.npy')
valid_boxes['left'] = np.load(calibration_data_directory + 'valid_boxes_left.npy')
valid_boxes['right'] = np.load(calibration_data_directory + 'valid_boxes_right.npy')

####################

min_disparity = 16
num_disp = 96
uniqueness = 10
speckle_window_size = 100
speckle_range = 32
p1 = 216
p2 = 864
max_disparity = 1

new_frames = []

block_matcher = cv2.StereoSGBM_create(
    minDisparity=min_disparity,
    blockSize=4,
    numDisparities=num_disp,
    uniquenessRatio=uniqueness,
    speckleWindowSize=speckle_window_size,
    speckleRange=speckle_range,
    disp12MaxDiff=max_disparity,
    P1=p1,
    P2=p2
)

####################
if True:
    file = 'cam-2016-06-23-13-16-17'

    image_left = config['examples_directory'] + file + '-1.png'
    image_right = config['examples_directory'] + file + '-0.png'
    output_file = config['examples_directory'] + file + '_' + str(int(time.time())) + '.ply'
    image_pair = [cv2.imread(image) for image in [image_left, image_right]]
    print(image_left, image_right, output_file)

    rectified_pair = []
    for i, side in enumerate(("left", "right")):
        rectified_pair.append(cv2.remap(image_pair[i],
                                        undistortion_map[side],
                                        rectification_map[side],
                                        cv2.INTER_NEAREST))

    ####################



    # disparity = block_matcher.get_disparity(rectified_pair)
    disparity = block_matcher.compute(rectified_pair[0], rectified_pair[1]).astype(np.float32) / 16.0
    # points = block_matcher.get_3d(disparity, disp_to_depth_mat)
    points = cv2.reprojectImageTo3D(disparity, disp_to_depth_mat)
    colors = cv2.cvtColor(rectified_pair[0], cv2.COLOR_BGR2RGB)

    points = points.reshape(-1, 3)
    colors = colors.reshape(-1, 3)
    ####################

    mask = points[:, 2] > points[:, 2].min()
    points = points[mask]
    colors = colors[mask]

    points = points.reshape(-1, 3)
    colors = colors.reshape(-1, 3)

    ####################

    points = np.hstack([points, colors])
    with open(output_file, 'w') as outfile:
        outfile.write(ply_header.format(
            vertex_count=len(points)))
        np.savetxt(outfile, points, '%f %f %f %d %d %d')
