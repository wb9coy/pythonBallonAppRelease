import packetDefs
import packetDefs
import ctypes
import libscrc

class processCallSignData():
    def __init__(self,
                 callSign,
                 txDataQueue,
                 debug=False):
        
        self._callSign    = callSign
        self._txDataQueue = txDataQueue
        self.debug        = debug
        
    def sendCallSignDataPacket(self):
        rtn = True
        
        HABPacketCallSignData = packetDefs.HABPacketCallSignDataType()
        
        HABPacketCallSignData.packetType = packetDefs.CW_ID
        HABPacketCallSignData.callSignDataLen = len(self._callSign)
        ctypes.memmove(ctypes.pointer(HABPacketCallSignData.callSignData), str.encode(self._callSign), HABPacketCallSignData.callSignDataLen)
        tempLen =  ctypes.sizeof(HABPacketCallSignData) - packetDefs.NPAR - packetDefs.CRC16_LEN 
        crcByteArray = bytes(HABPacketCallSignData)
        crc16 = libscrc.ibm(crcByteArray[:tempLen])
        HABPacketCallSignData.crc16 = crc16        
        sendByteArray = bytes(HABPacketCallSignData)
        
        if self._txDataQueue.empty():
            self._txDataQueue.put(sendByteArray)
        else:
            self._txDataQueue.queue.insert(0,sendByteArray)
          
        return rtn