import os
import subprocess
import shutil

def makePicPath(picDir,picNum):
    strPicNum = "{:03d}".format(picNum)
    picPath = picDir + "/image" + strPicNum + ".jpg"
    return picPath

def makeVidPath(vidDir,picNum):
    strPicNum = "{:03d}".format(picNum)
    vidPath = vidDir + "/vid" + strPicNum + ".h264"
    return vidPath

def cleanUpOldFlightData(spaceLimit,numFlightsToSave,dirPath):

    fs = int(freeSpace())
    print("Free space = " + str(fs) + "GB")

    if(fs < spaceLimit): 
        with os.scandir(dirPath) as entries:
            sorted_entries = sorted(entries, key=lambda entry: entry.name)
            sorted_items = [entry.name for entry in sorted_entries]

        numDirs = len(sorted_items) -1     
        for i in range(numDirs - numFlightsToSave):
            temp = dirPath + "/" + sorted_items[i]
            cmd = ["sudo","rm","-R",temp]
            subprocess.call(cmd)
            print("Removed " + sorted_items[i])

def freeSpace():

    KB = 1024
    MB = 1024 * KB
    GB = 1024 * MB

    fs = shutil.disk_usage('/').free / GB

    return fs

