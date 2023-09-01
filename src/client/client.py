# client.py Client that takes pictures using webcam and uploads them to server
# Version 1.0, Sep 1, 2023
# plant-cam
# by Evyn Price me@evynprice.com
# _____________________________________________________________________________
#

import os
import sys
import cv2
import time
from datetime import datetime
import requests

# This function will search camera ports until a valid port is found, returning as an int.
def findCamPort():
    attempts = 0
    camPort = 1
    while(attempts < 6): # If there are more than 5 non working ports, stop.
        camera = cv2.VideoCapture(camPort)
        if not camera.isOpened():
            attempts = attempts + 1
            now = datetime.now().strftime("%Y%m%d:%H%M%S")
            print("[debug][ " + now + "] Port " + camPort + " is unavailable.")
            camPort = camPort + 1
        else:
            isReading, img = camera.read()
            w = camera.get(3)
            h = camera.get(4)
            if isReading:
                now = datetime.now().strftime("%Y%m%d:%H%M%S")
                print("[debug][" + str(now) + "] Connected to camera on port " + str(camPort) + " and reading images (" + str(w) + " x " + str(h) + ")")
                return camPort
            else:
                now = datetime.now().strftime("%Y%m%d:%H%M%S")
                print("[debug][" + str(now) + "] Connected to camera on port " + str(camPort) + " but cannot read images.")
    return -1


def takePicture(camPort, path):
    if(camPort < 0):
        now = datetime.now().strftime("%Y%m%d:%H%M%S")
        print("[debug][" + str(now) + "] No camera port was found.")
        return

    cam = cv2.VideoCapture(camPort)
    time.sleep(3) # Sleep 3 seconds to give camera time to adjust
    result, image = cam.read()

    if result:
        now = datetime.now().strftime("%Y%m%d:%H%M%S")

        isExist = os.path.exists(path)
        if not isExist:
            os.makedirs(path)
            print("[debug][" + str(now) + "] Created path: " + path)

        imgName = str(now) + ".png"
        imgPath = os.path.join(path, imgName)

        cv2.imwrite(imgPath, image)
        print("[info][" + str(now) + "] Saved image: " + imgPath)
    else:
        print("[debug][" + str(now) + "] No image detected.")

    return imgPath

def uploadPicture(url, image):
    now = datetime.now().strftime("%Y%m%d:%H%M%S")
    imgFile = open(image, "rb")
    res = requests.post(url, files = {"file": imgFile})
    if res.ok:
        print("[info][" + str(now) + "] Image uploaded successfully: " + str(image))
    else:
        print("[error][" + str(now) + "] Failed to upload image " + str(image))
    res.close()
    imgFile.close()

def main():
    if(len(sys.argv) > 0):
        if("-camera" in sys.argv):
            argIndex = sys.argv.index("-camera") + 1
            camPort = int(sys.argv[argIndex])
        else:
            camPort = findCamPort()
        
        if("-path" in sys.argv):
            argIndex = sys.argv.index("-path") + 1
            path = str(sys.argv[argIndex])
        else:
            path = "images"

        if("-minutes" in sys.argv):
            argIndex = sys.argv.index("-minutes") + 1
            minutes = float(sys.argv[argIndex])
        else:
            minutes = 60
        
        if("-server" in sys.argv):
            argIndex = sys.argv.index("-server") + 1
            upload = str(sys.argv[argIndex])
        else:
            upload = ""
        
    else:
        camPort = findCamPort()
        path = "images"
        minutes = 60
        upload = ""

    print("[info] Taking images at " + str(minutes) + " minute intervals. Press ctrl + C to stop.")
    while(True):
        imgPath = takePicture(camPort, path)
        if not (upload == ''):
            uploadPicture(upload, imgPath)
        time.sleep(minutes * 60)

if __name__== "__main__":
    main()