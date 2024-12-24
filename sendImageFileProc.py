import os
import time
import threading
import packetDefs
import libscrc
import ctypes
import utils

class sendImageFileProc():
    def __init__(self,
                 picDir,
                 imageFileNameQueue,
                 txDataQueue,
                 endImageEvent,
                 debug=False):
        self._picDir             = picDir
        self.imagePicNumQueue    = imageFileNameQueue  
        self._txDataQueue        = txDataQueue
        self._debug              = debug
        
        self._runnable              = True
        self.sendImageFileThread    = threading.Thread(target=self._sendImageFileThreadFunction)
        self.endImageEvent          = endImageEvent
        
    def join(self):
        self.sendImageFileThread.join()
        
    def _sendImageFileThreadFunction(self):
        print("**** Starting Send Image Thread ******")
        HABPacketImageStart = packetDefs.HABPacketImageStartType()
        HABPacketImageData  = packetDefs.HABPacketImageDataType()
        HABPacketImageEnd   = packetDefs.HABPacketImageEndType()
        imageSeqnum         = None
        while(self._runnable):
            picNum    = self.imagePicNumQueue.get()
            picPath = utils.makePicPath(self._picDir,picNum)
            print("_sendImageFileThreadFunction" + picPath)
            if(os.path.exists(picPath) == False):
                print("Error File Not Found _sendImageFileThreadFunction " +  picPath)
            else:
                HABPacketImageStart.packetType  = packetDefs.START_IMAGE
                HABPacketImageStart.imageFileID = picNum
                HABPacketImageStart.fileSize    = os.path.getsize(picPath)
                if( (HABPacketImageStart.fileSize % packetDefs.MAX_IMG_BUF_LEN) != 0):
                    wholeNum = int(HABPacketImageStart.fileSize/packetDefs.MAX_IMG_BUF_LEN)
                    wholeNum +=1
                    pad = (wholeNum * packetDefs.MAX_IMG_BUF_LEN) - HABPacketImageStart.fileSize
                    HABPacketImageStart.fileSize = HABPacketImageStart.fileSize + pad
                tempLen =  ctypes.sizeof(HABPacketImageStart) - packetDefs.NPAR - packetDefs.CRC16_LEN 
                crcByteArray = bytes(HABPacketImageStart)
                crc16 = libscrc.ibm(crcByteArray[:tempLen])
                HABPacketImageStart.crc16 = crc16                     
                sendByteArray = bytes(HABPacketImageStart)
                self._txDataQueue.put(sendByteArray)

                imageSeqnum = 0
                f = open(picPath, mode="rb")
                time.sleep(.1)
                data = f.read(packetDefs.MAX_IMG_BUF_LEN)
                while data:
                    HABPacketImageData.packetType   = packetDefs.IMAGE_DATA
                    HABPacketImageData.imageFileID  = picNum
                    HABPacketImageData.imageSeqnum  = imageSeqnum
                    HABPacketImageData.imageDataLen = len(data)
                    ctypes.memmove(ctypes.pointer(HABPacketImageData.imageData), data, HABPacketImageData.imageDataLen)
                    sendByteArray = bytes(HABPacketImageData)
                    self._txDataQueue.put(sendByteArray)                   
                    imageSeqnum +=1
                    data = f.read(packetDefs.MAX_IMG_BUF_LEN)

                f.close()
                HABPacketImageEnd.packetType  = packetDefs.END_IMAGE
                HABPacketImageEnd.imageFileID = picNum
                tempLen =  ctypes.sizeof(HABPacketImageEnd) - packetDefs.NPAR - packetDefs.CRC16_LEN 
                crcByteArray = bytes(HABPacketImageEnd)
                crc16 = libscrc.ibm(crcByteArray[:tempLen])
                HABPacketImageEnd.crc16 = crc16                  
                sendByteArray = bytes(HABPacketImageEnd)
                self._txDataQueue.put(sendByteArray)
                self.endImageEvent.wait()
                self.endImageEvent.clear()
                if(self._debug):
                    print("clear event")
                time.sleep(.1)
            
        print("End _sendImageFileThreadFunction")
        
    def START(self):
        self.sendImageFileThread.start()
        time.sleep(1)
        
    def STOP(self):
        self._runnable = False
        time.sleep(.1)
        