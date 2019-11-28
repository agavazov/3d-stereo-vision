import json
import glob
import os

config = json.loads(open('config.json', 'r').read())

# To tmp
files_left = glob.glob(config['calibration_files_directory'] + "*-left.png")
files_right = glob.glob(config['calibration_files_directory'] + "*-right.png")

for file_left in files_left:
    os.rename(file_left, file_left + '.tmp')

for file_right in files_right:
    os.rename(file_right, file_right + '.tmp')

# To normal
files_left = glob.glob(config['calibration_files_directory'] + "*-left.png.tmp")
files_right = glob.glob(config['calibration_files_directory'] + "*-right.png.tmp")

for file_left in files_left:
    new_file_name = file_left
    new_file_name = new_file_name.replace('-left', '-right')
    new_file_name = new_file_name.replace('.tmp', '')
    os.rename(file_left, new_file_name)

for file_right in files_right:
    new_file_name = file_right
    new_file_name = new_file_name.replace('-right', '-left')
    new_file_name = new_file_name.replace('.tmp', '')
    os.rename(file_right, new_file_name)
