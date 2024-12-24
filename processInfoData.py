import packetDefs
import libscrc
import packetDefs
import ctypes

class processInfoData():
    def __init__(self,
                 txDataQueue,
                 versionInfo,
                 debug=False):
        
        self._txDataQueue = txDataQueue
        self.versionInfo  = versionInfo
        self.debug        = debug
        
    def sendInfoDataPacket(self):
        rtn = True
        
        HABPacketInfoData = packetDefs.HABPacketInfoDataType()
        
        HABPacketInfoData.packetType  = packetDefs.INFO_DATA
        HABPacketInfoData.infoDataLen = len(self.versionInfo)
        ctypes.memmove(ctypes.pointer(HABPacketInfoData.infoData), str.encode( " "*packetDefs.MAX_INFO_DATA_SIZE ), packetDefs.MAX_INFO_DATA_SIZE)
        ctypes.memmove(ctypes.pointer(HABPacketInfoData.infoData), str.encode(self.versionInfo), HABPacketInfoData.infoDataLen)
        tempLen =  ctypes.sizeof(HABPacketInfoData) - packetDefs.NPAR - packetDefs.CRC16_LEN 
        crcByteArray = bytes(HABPacketInfoData)
        crc16 = libscrc.ibm(crcByteArray[:tempLen])
        HABPacketInfoData.crc16 = crc16           
        sendByteArray = bytes(HABPacketInfoData)
        if self._txDataQueue.empty():
            self._txDataQueue.put(sendByteArray)
        else:
            self._txDataQueue.queue.insert(0,sendByteArray)
          
        return rtn