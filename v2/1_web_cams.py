import cv2
import numpy as np

cameraLeft = cv2.VideoCapture(1)
cameraRight = cv2.VideoCapture(0)

while (True):
    ret, frameLeft = cameraLeft.read()
    ret, frameRight = cameraRight.read()

    view = np.hstack([frameLeft, frameRight])
    cv2.imshow('view', view)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cameraLeft.release()
cameraRight.release()
cv2.destroyAllWindows()
