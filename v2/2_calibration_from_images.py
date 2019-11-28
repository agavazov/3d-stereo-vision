import cv2
import numpy as np
import os
import glob

importExtension = 'png'
exportExtension = 'ppm'

testId = '02'
dirExport = '../data/test' + testId + '/calibrations/'
importFiles = glob.glob('../data/test' + testId + '/camera/*.' + importExtension)

oddIsLeft = False

patternSize = (11, 7)
previewWith = 400

fileLeft = False
fileRight = False

for fileId, fileName in enumerate(importFiles):
    if int(fileId) % 2 == 0:
        if oddIsLeft == False:
            fileLeft = fileName
        else:
            fileRight = fileName
    else:
        if oddIsLeft == True:
            fileLeft = fileName
        else:
            fileRight = fileName

    if fileLeft == False or fileRight == False:
        continue

    print('Start width: ', fileLeft, fileRight)

    imgLeft = cv2.imread(fileLeft)
    imgRight = cv2.imread(fileRight)

    # Rotate left image
    imgRight = cv2.flip(imgRight, 0)
    imgRight = cv2.flip(imgRight, 1)

    retLeft, cornersLeft = cv2.findChessboardCorners(imgLeft, patternSize, None)
    retRight, cornersRight = cv2.findChessboardCorners(imgRight, patternSize, None)

    previewRation = float(previewWith) / float(imgLeft.shape[1])

    if retLeft and retRight:
        print('Found')

        if not os.path.exists(dirExport):
            os.makedirs(dirExport)

        textId = str(fileId / 2)
        if fileId / 2 < 10:
            textId = '0' + textId

        cv2.imwrite(dirExport + 'left_' + textId + '.' + exportExtension, imgLeft)
        cv2.imwrite(dirExport + 'right_' + textId + '.' + exportExtension, imgRight)
    else:
        print('Not found')

    if retLeft == True:
        imageGrayLeft = cv2.cvtColor(imgLeft, cv2.COLOR_BGR2GRAY)
        retRight, cornersLeft = cv2.findChessboardCorners(imageGrayLeft, patternSize)
        cv2.drawChessboardCorners(imgLeft, patternSize, cornersLeft, 0)

    if retRight == True:
        imageGrayRight = cv2.cvtColor(imgRight, cv2.COLOR_BGR2GRAY)
        retRight, cornersRight = cv2.findChessboardCorners(imageGrayRight, patternSize)
        cv2.drawChessboardCorners(imgRight, patternSize, cornersRight, 0)

    imgLeft = cv2.resize(imgLeft, None, fx=previewRation, fy=previewRation, interpolation=cv2.INTER_CUBIC)
    imgRight = cv2.resize(imgRight, None, fx=previewRation, fy=previewRation, interpolation=cv2.INTER_CUBIC)

    preview = np.hstack([imgLeft, imgRight])
    cv2.imshow('Preview', preview)

    fileLeft = False
    fileRight = False

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

###

print(
    'python calibrate_cameras --rows 11 --columns 7 --square-size 4.5 D:\\Workspace\\htdocs\\stereo-vision\\data\\test' + testId + '\\calibrations\\ D:\\Workspace\\htdocs\\stereo-vision\\data\\test' + testId + '\\calibrations_out\\')

for fileId in range(1, len(importFiles) + 1):
    textId = str(fileId / 2)
    if fileId / 2 < 10:
        textId = '0' + textId

    print(
        'python images_to_pointcloud D:\\Workspace\\htdocs\\stereo-vision\\data\\test' + testId + '\\calibrations_out\\ D:\\Workspace\\htdocs\\stereo-vision\\data\\test' + testId + '\\calibrations\\left_' + textId + '.ppm D:\\Workspace\\htdocs\\stereo-vision\\data\\test' + testId + '\\calibrations\\right_' + textId + '.ppm D:\\Workspace\\htdocs\\stereo-vision\\data\\test' + testId + '\\calibrations\\' + textId + '.ply')
