import os
import time
import threading
import subprocess
import queue
import utils
import constants
from PIL import Image

class cameraProc():
    def __init__(self,
                 picDirHighRes,
                 picDirLowRes,
                 vidDir,         
                 rotation,
                 debug=False):

        self._picDirHighRes = picDirHighRes
        self._picDirLowRes  = picDirLowRes
        self._vidDir        = vidDir       
        self._rotation      = rotation
        self._debug         = debug
        
        self._runnable        = True
        self.camThread        = threading.Thread(target=self._cameraThreadFunction)
        self.imagePicNumQueue = queue.LifoQueue(10*1024)
        self._width           = 4608
        self._height          = 2592
        self._vidWidth        = 1920
        self._vidHeight       = 1080

        os.environ["LIBCAMERA_LOG_LEVELS"] = "3"
        
    def join(self):
        self.camThread.join()
        
    def _cameraThreadFunction(self):
        print("**** Starting Camera Thread ******")

        picNum          = 0
        vidNum          = 0

        while(self._runnable): 
            highResPicPath = utils.makePicPath(self._picDirHighRes,picNum)
            print("Take Pic " + highResPicPath)
            cmd = ["libcamera-still","-o",highResPicPath,"-n","--lens-position","0.0","--rotation",str(self._rotation),"--width",str(self._width),"--height",str(self._height)]
            #cmd = ["libcamera-still","-o",highResPicPath,"-n","--autofocus-mode","manual","--lens-position","0.0","--width",str(self._width),"--height",str(self._height)]
            #cmd = ["libcamera-still","-o",highResPicPath,"-n","--rotation",str(self._rotation),"--autofocus-range","normal","--width",str(self._width),"--height",str(self._height)]
            #cmd = ["libcamera-still","-o",highResPicPath,"-n","--rotation",str(self._rotation),"--width",str(self._width),"--height",str(self._height)]
            process = subprocess.Popen(cmd)
            timeoutFlag = False
            try:
                # Compliant: makes sure to terminate the child process when
                # the timeout expires.
                outs, errs = process.communicate(timeout=15)
            except subprocess.TimeoutExpired:
                process.kill()
                outs, errs = process.communicate()
                timeoutFlag = True
                print("Camera Timeout")

            if(timeoutFlag == False):
                subprocess.call(["sync"])
        
                try:
                    highResImage  = Image.open(highResPicPath)
                    lowResImage   = highResImage.resize((640,480))
                    lowResPicPath = utils.makePicPath(self._picDirLowRes,picNum)
                    lowResImage.save(lowResPicPath)
                    time.sleep(1)
                    subprocess.call(["sync"])
                    self.imagePicNumQueue.put(picNum)
                    if(picNum != 254):
                        picNum = picNum + 1
                except:
                    pass

                vidPath = utils.makeVidPath(self._vidDir,vidNum)
                print("Take Video " + vidPath)
                cmd = ["libcamera-vid","-t","20000","-n","-b","9000000","--rotation",str(self._rotation),"--lens-position","0.0","--width",str(self._vidWidth),"--height",str(self._vidHeight),"-o",vidPath]
                process = subprocess.Popen(cmd) 
                try:
                    # Compliant: makes sure to terminate the child process when
                    # the timeout expires.
                    outs, errs = process.communicate(timeout=25)
                    subprocess.call(["sync"])
                    if(vidNum != 254):
                    	vidNum = vidNum + 1
                except subprocess.TimeoutExpired:
                    process.kill()
                    outs, errs = process.communicate()
                    print("Video Timeout")
            
    def START(self):
        self.camThread.start()
        time.sleep(1)
        
    def STOP(self):
        self._runnable = False
        time.sleep(.1)
                                            

        