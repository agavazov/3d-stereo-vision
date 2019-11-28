import cv2
from glob import glob
import numpy as np

patternSize = (6, 9)

cameraLeft = cv2.VideoCapture(1)
cameraRight = cv2.VideoCapture(0)

## CHECK
square_size = 1
pattern_points = np.zeros((np.prod(patternSize), 3), np.float32)
pattern_points[:, :2] = np.indices(patternSize).T.reshape(-1, 2)
pattern_points *= square_size
## CHECK

objPointsLeft = []
objPointsRight = []

imgPointsLeft = []
imgPointsRight = []

width = 0
height = 0

extension = 'ppm'
directory = './calibrations/'

# Load images and calibrate
totalFiles = (len(glob(directory + '*.' + extension)) / 2) + 1
totalFiles = 4
for fileId in range(1, totalFiles):
    leftCalibrationImg = cv2.imread(directory + 'left' + str(fileId) + '.' + extension, 0)
    rightCalibrationImg = cv2.imread(directory + 'right' + str(fileId) + '.' + extension, 0)

    calibrationImg = np.hstack([leftCalibrationImg, rightCalibrationImg])
    cv2.imshow('calibrationImg', calibrationImg)

    retLeft, cornersLeft = cv2.findChessboardCorners(leftCalibrationImg, patternSize, None)
    if retLeft == True:
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        objPointsLeft.append(pattern_points)
        cv2.cornerSubPix(leftCalibrationImg, cornersLeft, (11, 11), (-1, -1), criteria)
        imgPointsLeft.append(cornersLeft)

    retRight, cornersRight = cv2.findChessboardCorners(rightCalibrationImg, patternSize, None)
    if retRight == True:
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        objPointsRight.append(pattern_points)
        cv2.cornerSubPix(rightCalibrationImg, cornersRight, (11, 11), (-1, -1), criteria)
        imgPointsRight.append(cornersRight)

    height, width = leftCalibrationImg.shape[:2]

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()

# Calibrate
retval, cameraMatrix1, distCoeffs1, cameraMatrix2, distCoeffs2, R, T, E, F = cv2.stereoCalibrate(
    objectPoints=objPointsLeft, imagePoints1=imgPointsLeft, imagePoints2=imgPointsRight, cameraMatrix1=None,
    distCoeffs1=None, cameraMatrix2=None, distCoeffs2=None, imageSize=(width, height))

# Show result
"""
while (True):
    ret, frameLeft = cameraLeft.read()
    ret, frameRight = cameraRight.read()

    grayViewLeft = cv2.cvtColor(frameLeft, cv2.COLOR_BGR2GRAY)
    grayViewRight = cv2.cvtColor(frameRight, cv2.COLOR_BGR2GRAY)

    cv2.imshow('grayViewLeft', grayViewLeft)
    cv2.imshow('grayViewRight', grayViewRight)

    stereo = cv2.StereoSGBM(1, 16, 15)
    disparity = stereo.compute(grayViewLeft, grayViewRight)

    stereoView = cv2.normalize(disparity, disparity, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U)
    cv2.imshow('stereoView', stereoView)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cameraLeft.release()
cameraRight.release()
cv2.destroyAllWindows()




"""

lFrame = cv2.imread('./calibrations/left1.ppm')
rFrame = cv2.imread('./calibrations/right1.ppm')
w, h = lFrame.shape[:2]  # both frames should be of same shape
frames = [lFrame, rFrame]

# Params from camera calibration
camMats = [cameraMatrix1, cameraMatrix2]
distCoeffs = [distCoeffs1, distCoeffs2]

camSources = [0, 1]
for src in camSources:
    distCoeffs[src][0][4] = 0.0  # use only the first 2 values in distCoeffs

# The rectification process
newCams = [0, 0]
roi = [0, 0]
for src in camSources:
    newCams[src], roi[src] = cv2.getOptimalNewCameraMatrix(cameraMatrix=camMats[src], distCoeffs=distCoeffs[src],
                                                           imageSize=(w, h), alpha=0)

rectFrames = [0, 0]
for src in camSources:
    rectFrames[src] = cv2.undistort(frames[src], camMats[src], distCoeffs[src])

# See the results
view = np.hstack([frames[0], frames[1]])
rectView = np.hstack([rectFrames[0], rectFrames[1]])

cv2.imshow('view', view)
cv2.imshow('rectView', rectView)


stereo = cv2.StereoSGBM(1, 16, 15)
disparity = stereo.compute(rectFrames[0], rectFrames[1])
disparity = cv2.normalize(disparity, disparity, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U)
cv2.imshow('disparity', disparity)






# Wait indefinitely for any keypress
cv2.waitKey(0)
