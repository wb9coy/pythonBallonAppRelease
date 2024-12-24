import os
import queue
import threading
import time
from datetime import datetime


class logger():
    
    def __init__(self,
                 logFilePath,
                 debug=False):
        
        self._logQ        = queue.Queue(1024*50)
        self._logFilePath = logFilePath
        self._debug       = True
        self._runable     = True

        self._logThread   = None
        self._fileId      = None
        
    def logBanner(self,txt=""):
        bannerStr = " **********************************************************************************************"
        self.LOG(bannerStr)
        self.LOG(txt)
        self.LOG(bannerStr)      
        
    def START(self):
        
        rtn = True

        try:
            self._fileId = open(self._logFilePath,"w")
            self._fileId.close()
        except OSError as e:
            print(e)
            rtn = False

        self._logThread = threading.Thread(target=self._logFunction)
        if(self._logThread != None):
            self._logThread.start()
            time.sleep(1)
        else:
            rtn = False
        
        return rtn 

    def LOG(self, msg):
        rtn = True
        if(self._fileId != None):
            try:
                self._logQ.put(msg)
            except queue.Full as e:
                print(str(e))
                rtn = False
            
        return rtn
                            
    def _logFunction(self):
        print("**** Starting Logger Thread ******")
        while(self._runable):
            logMsg = self._logQ.get(True)
            now = datetime.now()
            t = now.strftime("%Y:%m:%d %H:%M:%S")
            temp = t + " " + logMsg
            if(self._fileId != None):
                self._fileId = open(self._logFilePath,"a")
                self._fileId.write(temp+"\n")
                self._fileId.close()

