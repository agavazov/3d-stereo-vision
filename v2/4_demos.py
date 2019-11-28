import glob

testId = '03'
importFiles = glob.glob('data/test' + testId + '/demo/*')

oddIsLeft = False

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

    print('python images_to_pointcloud D:\\Workspace\\htdocs\\stereo-vision\\data\\test' + testId + '\\calibrations_out\\ D:\\Workspace\\htdocs\\stereo-vision\\' + fileLeft + ' D:\\Workspace\\htdocs\\stereo-vision\\' + fileRight + ' D:\\Workspace\\htdocs\\stereo-vision\\data\\test' + testId + '\\demo\\' + str(fileId) + '.ply')

    fileLeft = False
    fileRight = False
