#include "stdafx.h"
#include "FlyCapture2.h"
#include <iostream>
#include <sstream>

#include <windows.h>
#include <ctime>
#include <vector>
#include <process.h>
#include <conio.h>
#include <fstream>
#include <string>

using namespace FlyCapture2;
using namespace std;

string filesPrefix = "D:\\Workspace\\htdocs\\stereo-vision\\data\\tmp\\";
unsigned int busyCams = 0;
std::vector<Camera *> allCameras;

void shoot(void *cameraId) {
    Camera *currentCamera = allCameras[(int) cameraId];

    Error error;

    Image image;

    unsigned int softwareTrigger = 0x62C;
    unsigned int fireVal = 0x80000000;

    error = currentCamera->WriteRegister(softwareTrigger, fireVal);
    if (error != PGRERROR_OK) {
        error.PrintErrorTrace();
        //return -1;
    }

    // Grab image
    error = currentCamera->RetrieveBuffer(&image);
    if (error != PGRERROR_OK) {
        error.PrintErrorTrace();
        //return -1;
    }

    // Save
    time_t timer;
    char buffer[26];
    struct tm* tm_info;
    time(&timer);
    tm_info = localtime(&timer);
    strftime(buffer, 26, "%Y-%m-%d-%H-%M-%S", tm_info);

    ostringstream filename;
    filename << filesPrefix;
    filename << "cam";
    filename << "-" << buffer;
    filename << "-" << (int) cameraId;
    filename << ".pgm";

    error = image.Save(filename.str().c_str());
    if (error != PGRERROR_OK) {
        error.PrintErrorTrace();
        //return -1;
    }

    // Continue
    busyCams--;
    cout << filename.str().c_str() << endl;
}

int main(int /*argc*/, char ** /*argv*/) {
    Error error;
    BusManager busMgr;

    cout << endl << endl << "Start the process" << endl;

    // Get all cameras
    unsigned int totalCameras = 0;

    error = busMgr.GetNumOfCameras(&totalCameras);
    if (error != PGRERROR_OK) {
        error.PrintErrorTrace();
        return -1;
    }

    // @todo make it dynamic
    Camera cam1;
    Camera cam2;
    allCameras.push_back(&cam1);
    allCameras.push_back(&cam2);

    TriggerMode triggerMode;
    StrobeControl mStrobe;

    PGRGuid guid;

    for (unsigned int cameraId = 0; cameraId < totalCameras; cameraId++) {
        error = busMgr.GetCameraFromIndex(cameraId, &guid);

        // Connect to a camera
        error = allCameras[cameraId]->Connect(&guid);
        if (error != PGRERROR_OK) {
            error.PrintErrorTrace();
            return -1;
        }

        // Power on the camera
        unsigned int cameraPower = 0x610;
        unsigned int powerVal = 0x80000000;
        error = allCameras[cameraId]->WriteRegister(cameraPower, powerVal);
        if (error != PGRERROR_OK) {
            error.PrintErrorTrace();
            return -1;
        }

        // Wait for camera to complete power-up
        unsigned int millisecondsToSleep = 100;
        unsigned int regVal = 0;
        unsigned int retries = 10;

        do {
            Sleep(millisecondsToSleep);
            error = allCameras[cameraId]->ReadRegister(cameraPower, &regVal);
            if (error == PGRERROR_TIMEOUT) {
                // ignore timeout errors, camera may not be responding to
                // register reads during power-up
            }
            else if (error != PGRERROR_OK) {
                error.PrintErrorTrace();
                return -1;
            }

            retries--;
        } while ((regVal & powerVal) == 0 && retries > 0);


        // Check for timeout errors after retrying
        if (error == PGRERROR_TIMEOUT) {
            error.PrintErrorTrace();
            return -1;
        }

        // Check for external trigger support
        TriggerModeInfo triggerModeInfo;
        error = allCameras[cameraId]->GetTriggerModeInfo(&triggerModeInfo);
        if (error != PGRERROR_OK) {
            error.PrintErrorTrace();
            return -1;
        }

        if (triggerModeInfo.present == NULL) {
            cout << "Camera does not support external trigger! Exiting..." << endl;
            return -1;
        }

        // Get current trigger settings
        TriggerMode triggerMode;
        error = allCameras[cameraId]->GetTriggerMode(&triggerMode);
        if (error != PGRERROR_OK) {
            error.PrintErrorTrace();
            return -1;
        }

        // Set camera to trigger mode 0
        triggerMode.onOff = true;
        triggerMode.mode = 0;
        triggerMode.parameter = 0;

        // A source of 7 means software trigger
        triggerMode.source = 7;

        error = allCameras[cameraId]->SetTriggerMode(&triggerMode);
        if (error != PGRERROR_OK) {
            error.PrintErrorTrace();
            return -1;
        }

        // Poll to ensure camera is ready
        unsigned int softwareTrigger = 0x62C;
        regVal = 0;

        do {
            error = allCameras[cameraId]->ReadRegister(softwareTrigger, &regVal);
            if (error != PGRERROR_OK) {
                error.PrintErrorTrace();
                cout << endl;
                cout << "Error polling for trigger ready!" << endl;
                return -1;
            }
        } while ((regVal >> 31) != 0);

        // Get the camera configuration
        FC2Config config;
        error = allCameras[cameraId]->GetConfiguration(&config);
        if (error != PGRERROR_OK) {
            error.PrintErrorTrace();
            return -1;
        }

        // Set the grab timeout to 5 seconds
        config.grabTimeout = 5000;

        // Set the camera configuration
        error = allCameras[cameraId]->SetConfiguration(&config);
        if (error != PGRERROR_OK) {
            error.PrintErrorTrace();
            return -1;
        }

        // Camera is ready, start capturing images
        error = allCameras[cameraId]->StartCapture();
        if (error != PGRERROR_OK) {
            error.PrintErrorTrace();
            return -1;
        }

        //CheckSoftwareTriggerPresence
        unsigned int triggerInq = 0x530;
        regVal = 0;

        error = allCameras[cameraId]->ReadRegister(triggerInq, &regVal);

        if (error != PGRERROR_OK) {
            error.PrintErrorTrace();
            return false;
        }

        if ((regVal & 0x10000) != 0x10000) {
            cout << "SOFT_ASYNC_TRIGGER not implemented on this camera! Stopping application" << endl;
            return -1;
        }
    }

    if (totalCameras < 1) {
        cout << "Please connect more then one camera!" << endl;
    }

    // Check is cameras ready
    for (unsigned int cameraId = 0; cameraId < totalCameras; cameraId++) {
        unsigned int softwareTrigger = 0x62C;
        unsigned int regVal = 0;

        do {
            error = allCameras[cameraId]->ReadRegister(softwareTrigger, &regVal);
            if (error != PGRERROR_OK) {
                error.PrintErrorTrace();
                return -1;
            }

        } while ((regVal >> 31) != 0);
    }

    // Shooting
    while (true) {
        if (busyCams != 0) {
            continue;
        }

        // Shoot
        cout << "Start shooting" << endl;
        for (unsigned int cameraId = 0; cameraId < totalCameras; cameraId++) {
            busyCams++;
            _beginthread(shoot, 0, (void *) cameraId);
        }
    }
}
