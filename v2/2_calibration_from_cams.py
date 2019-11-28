import cv2
import time
import numpy as np
import winsound

cameraLeft = cv2.VideoCapture(1)
cameraRight = cv2.VideoCapture(0)

totalSaves = 100

patternSize = (10, 7)
extension = 'ppm'  # png
directory = './calibrations/'

saveId = 80

def addText(img, text, color=(0, 0, 255), left=50, top=50):
    cv2.putText(img, text, (left, top), cv2.FONT_HERSHEY_PLAIN, 4, color)
    cv2.putText(img, text, (left + 1, top), cv2.FONT_HERSHEY_PLAIN, 4, color)
    cv2.putText(img, text, (left, top + 1), cv2.FONT_HERSHEY_PLAIN, 4, color)
    cv2.putText(img, text, (left + 1, top + 1), cv2.FONT_HERSHEY_PLAIN, 4, color)

while (True):
    key = cv2.waitKey(1)

    textLeft = 'OK (PRESS S)'
    textRight = 'OK (PRESS S)'

    ret, frameLeft = cameraLeft.read()
    ret, frameRight = cameraRight.read()

    retLeft, cornersLeft = cv2.findChessboardCorners(frameLeft, patternSize, None)
    retRight, cornersRight = cv2.findChessboardCorners(frameRight, patternSize, None)

    if retLeft == False:
        textLeft = 'FAIL'

    if retRight == False:
        textRight = 'FAIL'

    if key & 0xFF == ord('s') and retLeft == True and retRight == True:
        saveId = saveId + 1

        textId = str(saveId)
        if saveId < 10:
            textId = '0' + textId

        cv2.imwrite(directory + 'left_' + textId + '.' + extension, frameLeft)
        cv2.imwrite(directory + 'right_' + textId + '.' + extension, frameRight)

        addText(frameLeft, 'OK')
        addText(frameRight, 'OK')

        winsound.Beep(1500, 150)

        print('Save: ', saveId)
        time.sleep(0.5)

    if saveId >= totalSaves:
        break

    if key & 0xFF == ord('q'):
        break

    addText(frameLeft, textLeft)
    addText(frameRight, textRight)
    preview = np.hstack([frameLeft, frameRight])
    cv2.imshow('preview', preview)

cameraLeft.release()
cameraRight.release()
cv2.destroyAllWindows()
