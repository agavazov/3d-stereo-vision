from argparse import ArgumentParser

import cv2

from stereovision.blockmatchers import StereoBM, StereoSGBM
from stereovision.calibration import StereoCalibration
from stereovision.ui_utils import find_files, BMTuner, STEREO_BM_FLAG


def main():
    parser = ArgumentParser(description="Read images taken from a calibrated "
                           "stereo pair, compute disparity maps from them and "
                           "show them interactively to the user, allowing the "
                           "user to tune the stereo block matcher settings in "
                           "the GUI.", parents=[STEREO_BM_FLAG])
    parser.add_argument("calibration_folder",
                        help="Directory where calibration files for the stereo "
                        "pair are stored.")
    parser.add_argument("image_folder",
                        help="Directory where input images are stored.")
    parser.add_argument("--bm_settings",
                        help="File to save last block matcher settings to.",
                        default="")
    args = parser.parse_args()

    calibration_folder = 'D:\\Workspace\\htdocs\\stereo-vision\\data\\test07\\calibration-data\\'

    calibration = StereoCalibration(input_folder=calibration_folder)
    image_folder = 'D:\\Workspace\\htdocs\\stereo-vision\\data\\test07\\examples2'

    input_files = find_files(image_folder)
    if args.use_stereobm:
        block_matcher = StereoBM()
    else:
        block_matcher = StereoSGBM()

    image_pair = [cv2.imread(image) for image in input_files[:2]]
    input_files = input_files[2:]
    rectified_pair = calibration.rectify(image_pair)
    tuner = BMTuner(block_matcher, calibration, rectified_pair)

    while input_files:
        image_pair = [cv2.imread(image) for image in input_files[:2]]
        rectified_pair = calibration.rectify(image_pair)
        tuner.tune_pair(rectified_pair)
        input_files = input_files[2:]

    for param in block_matcher.parameter_maxima:
        print("{}\n".format(tuner.report_settings(param)))

    if args.bm_settings:
        block_matcher.save_settings(args.bm_settings)


if __name__ == "__main__":
    main()
