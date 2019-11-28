# 3D Stereo Vision research with Python and OpenCV

This is part of my code about my research with 3D Stereo Vision

Note: the project is from year ~2015 and this is my 1st experience with Python and C++. Anyway the examples may help you.

![](https://github.com/agavazov/3d-stereo-vision/raw/master/img/opencv.png)
![](https://github.com/agavazov/3d-stereo-vision/raw/master/img/python.png)

![](https://github.com/agavazov/3d-stereo-vision/raw/master/img/depth.png)

## Advices

- Before start using real cameras, try to do the things with stamps from internet (photos and calibration)
- Before buying expensive industrial cameras, try to work with cheap USB cameras (it is super easy to use them in python with `cv2.VideoCapture(0)`)
- If you intend to buy more expensive cameras check what SDK they have and is it ok for you to use it
- Don't start with fish-eye lenses (in fact don't use them), the less distortion you have, the easier it is to calibrate and examine
- Read little bit about lens
- [**Matlab** Stereo Camera Calibrator](https://www.mathworks.com/help/vision/ug/stereo-camera-calibrator-app.html) is very useful when doing your research

## C++ shooter

Uses the FlyCapture2 SDK. `AsyncTriggerEx.cpp` has hard-coded variable `filesPrefix` which is the directory where files will be saved.
The program can works with array of cameras `allCameras` (You can push one or infinity cameras) and all will be triggered at the same time (with less than 0.001 diff)
The output format is `pgm` which as far as I remember it was suitable for python.

![](https://github.com/agavazov/3d-stereo-vision/raw/master/img/camera.jpg)
![](https://github.com/agavazov/3d-stereo-vision/raw/master/img/camera-stand.png)

## v3 python scripts

1st check `config.json` and set your preferences

![](https://github.com/agavazov/3d-stereo-vision/raw/master/img/calibration1.png)
![](https://github.com/agavazov/3d-stereo-vision/raw/master/img/calibration2.png)

### 0.webcams_view.py

Will show the USB web cam live streaming

### 1.create_calibrations_from_images.py

Make calibration stamps when press the `space` key

### 1.create_calibrations_from_webcams.py

Live/automatic shooting from web cameras (you have to walk around like a monkey with a calibration board)

### 2.calibration.py

Crate calibration from the generated files/stamps

### 3.webcam_examples.py

No idea, I do not remember what that files do.

### 4.make_3d.py

The interesting part when you generate the 3D 

### 5.extract-shapes.py

I'm not entirely sure if this script is working properly, but it should extract the 3D shapes

## Bonus

2 Python scripts for car plate recognition
