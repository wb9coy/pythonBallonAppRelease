import time
import threading
import re
import serial
import ubloxPacketDefs
import ctypes


class ubloxGPSProc():
    def __init__(self,
                 port,
                 baud,
                 sensorDataQueue,
                 debug=False):
        
        self._port            = port
        self._baud            = baud
        self._sensorDataQueue = sensorDataQueue
        self._debug           = debug
        
        self._serialPort  = None
        self._runnable    = True
        self.gpsThread    = threading.Thread(target=self._gpsThreadFunction)

        self.ggaSentence  = None
        self.rmcSentence  = None
        

    def join(self):
        self.gpsThread.join()

    def getGGA(self):
        return self.ggaSentence

    def getRMC(self):
        return self.rmcSentence

    def checksum(self, data):
        ck_a = 0
        ck_b = 0
        for b in data:
            ck_a = ck_a + b & 0xFF
            ck_b = (ck_b + ck_a) & 0xFF
        return (ck_a, ck_b)

    def setGNSS(self):
        
        rtn = False
        
        expectedRsp = [ubloxPacketDefs.PREAMBLE2,
                       ubloxPacketDefs.CLASS_ACK,
                       ubloxPacketDefs.MSG_ACK_ACK,
                       0x02,
                       0x00,
                       ubloxPacketDefs.CLASS_CFG,
                       ubloxPacketDefs.MSG_CFG_GNSS,
                       0x4c,
                       0x75
                       ]        
        
        ubloxPacketSync   = ubloxPacketDefs.ubloxPacketSyncType()
        ubloxPacketHeader = ubloxPacketDefs.ubloxPacketHeaderType()
        UBXCFGGNSS        = ubloxPacketDefs.UBXCFGGNSSType()
        ubloxPacketCk     = ubloxPacketDefs.ubloxPacketCkType()        
        
        ubloxPacketSync.sync1    = ubloxPacketDefs.PREAMBLE1 
        ubloxPacketSync.sync2    = ubloxPacketDefs.PREAMBLE2
        ubloxPacketHeader.Class  = ubloxPacketDefs.CLASS_CFG
        ubloxPacketHeader.id     = ubloxPacketDefs.MSG_CFG_GNSS
        ubloxPacketHeader.length = ctypes.sizeof(UBXCFGGNSS)        

        UBXCFGGNSS.msgVer          = 0x00
        UBXCFGGNSS.numTrkChHw      = 0x00
        UBXCFGGNSS.numTrkChUse     = 0x20
        UBXCFGGNSS.numConfigBlocks = ubloxPacketDefs.NUM_CONFIG_BLOCKS
        
        UBXCFGGNSS.gnssConfigBlock[0].gnssId    = ubloxPacketDefs.GPS_ID
        UBXCFGGNSS.gnssConfigBlock[0].resTrkCh  = 0x08
        UBXCFGGNSS.gnssConfigBlock[0].maxTrkCh  = 0x10
        UBXCFGGNSS.gnssConfigBlock[0].reserved1 = 0x00
        UBXCFGGNSS.gnssConfigBlock[0].flags[0]  = 0x01
        UBXCFGGNSS.gnssConfigBlock[0].flags[1]  = 0x00
        UBXCFGGNSS.gnssConfigBlock[0].flags[2]  = 0x01
        UBXCFGGNSS.gnssConfigBlock[0].flags[3]  = 0x01
        
        UBXCFGGNSS.gnssConfigBlock[1].gnssId    = ubloxPacketDefs.SBAS_ID
        UBXCFGGNSS.gnssConfigBlock[1].resTrkCh  = 0x01
        UBXCFGGNSS.gnssConfigBlock[1].maxTrkCh  = 0x03
        UBXCFGGNSS.gnssConfigBlock[1].reserved1 = 0x00
        UBXCFGGNSS.gnssConfigBlock[1].flags[0]  = 0x00
        UBXCFGGNSS.gnssConfigBlock[1].flags[1]  = 0x00
        UBXCFGGNSS.gnssConfigBlock[1].flags[2]  = 0x01
        UBXCFGGNSS.gnssConfigBlock[1].flags[3]  = 0x01
        
        UBXCFGGNSS.gnssConfigBlock[2].gnssId    = ubloxPacketDefs.BeiDou_ID
        UBXCFGGNSS.gnssConfigBlock[2].resTrkCh  = 0x08
        UBXCFGGNSS.gnssConfigBlock[2].maxTrkCh  = 0x10
        UBXCFGGNSS.gnssConfigBlock[2].reserved1 = 0x00
        UBXCFGGNSS.gnssConfigBlock[2].flags[0]  = 0x00
        UBXCFGGNSS.gnssConfigBlock[2].flags[1]  = 0x00
        UBXCFGGNSS.gnssConfigBlock[2].flags[2]  = 0x01
        UBXCFGGNSS.gnssConfigBlock[2].flags[3]  = 0x01
        
        UBXCFGGNSS.gnssConfigBlock[3].gnssId    = ubloxPacketDefs.QZSS_ID
        UBXCFGGNSS.gnssConfigBlock[3].resTrkCh  = 0x00
        UBXCFGGNSS.gnssConfigBlock[3].maxTrkCh  = 0x03
        UBXCFGGNSS.gnssConfigBlock[3].reserved1 = 0x00
        UBXCFGGNSS.gnssConfigBlock[3].flags[0]  = 0x00
        UBXCFGGNSS.gnssConfigBlock[3].flags[1]  = 0x00
        UBXCFGGNSS.gnssConfigBlock[3].flags[2]  = 0x01
        UBXCFGGNSS.gnssConfigBlock[3].flags[3]  = 0x01 
        
        UBXCFGGNSS.gnssConfigBlock[4].gnssId    = ubloxPacketDefs.GLONASS_ID
        UBXCFGGNSS.gnssConfigBlock[4].resTrkCh  = 0x08
        UBXCFGGNSS.gnssConfigBlock[4].maxTrkCh  = 0x0E
        UBXCFGGNSS.gnssConfigBlock[4].reserved1 = 0x00
        UBXCFGGNSS.gnssConfigBlock[4].flags[0]  = 0x00
        UBXCFGGNSS.gnssConfigBlock[4].flags[1]  = 0x00
        UBXCFGGNSS.gnssConfigBlock[4].flags[2]  = 0x01
        UBXCFGGNSS.gnssConfigBlock[4].flags[3]  = 0x01        
        
        ck_a, ck_b = self.checksum( bytes(ubloxPacketHeader) + bytes(UBXCFGGNSS))
        ubloxPacketCk.cka = ck_a
        ubloxPacketCk.ckb = ck_b
        
        sendByteArray = bytes(ubloxPacketSync) + bytes(ubloxPacketHeader) + bytes(UBXCFGGNSS) + bytes(ubloxPacketCk)
        for retry in range(10):
            ack = False
            self._serialPort.write(sendByteArray)
            preambleFound = False
            for preambleCount in range(8200):
                rsp = self._serialPort.read()
                if rsp == ubloxPacketDefs.PREAMBLE1.to_bytes(1,"big"):
                    preambleFound = True
                    break
            if(preambleFound):
                rsp = self._serialPort.read(9)
                expectedRspIndx = 0
                ack = True
                for b in rsp:
                    if(b != expectedRsp[expectedRspIndx]):
                        ack = False
                    expectedRspIndx +=1
            if(ack):
                rtn = True
                break               
        if(rtn):
            print("GNSS set to GPS")     
        else:
            print("FAILED to set GNSS to GPS")             
            
        return rtn             
        
    def setDynModel(self):
        
        rtn = False
        
        expectedRsp = [ubloxPacketDefs.PREAMBLE2,
                       ubloxPacketDefs.CLASS_ACK,
                       ubloxPacketDefs.MSG_ACK_ACK,
                       0x02,
                       0x00,
                       ubloxPacketDefs.CLASS_CFG,
                       ubloxPacketDefs.MSG_CFG_NAV5,
                       0x32,
                       0x5b
                       ]
        
        ubloxPacketSync   = ubloxPacketDefs.ubloxPacketSyncType()
        ubloxPacketHeader = ubloxPacketDefs.ubloxPacketHeaderType()
        UBXCFGNAV5        = ubloxPacketDefs.UBXCFGNAV5Type()
        ubloxPacketCk     = ubloxPacketDefs.ubloxPacketCkType()

        ubloxPacketSync.sync1    = ubloxPacketDefs.PREAMBLE1 
        ubloxPacketSync.sync2    = ubloxPacketDefs.PREAMBLE2
        ubloxPacketHeader.Class  = ubloxPacketDefs.CLASS_CFG
        ubloxPacketHeader.id     = ubloxPacketDefs.MSG_CFG_NAV5
        ubloxPacketHeader.length = ctypes.sizeof(UBXCFGNAV5)
        
        UBXCFGNAV5.mask              = 0xffff
        UBXCFGNAV5.dynModel          = 0x06
        UBXCFGNAV5.fixMode           = 0x03
        UBXCFGNAV5.fixedAlt          = 0x00 
        UBXCFGNAV5.fixedAltVar       = 0x00002710
        UBXCFGNAV5.minElev           = 0x05
        UBXCFGNAV5.drLimit           = 0x00
        UBXCFGNAV5.pDop              = 0x00FA
        UBXCFGNAV5.tDop              = 0x00FA
        UBXCFGNAV5.pAcc              = 0x0064
        UBXCFGNAV5.tAcc              = 0x012c
        UBXCFGNAV5.staticHoldThresh  = 0x00
        UBXCFGNAV5.dgnssTimeout      = 0x00
        UBXCFGNAV5.cnoThreshNumSVs   = 0x00
        UBXCFGNAV5.cnoThresh         = 0x00
        UBXCFGNAV5.reserved1[0]      = 0x00
        UBXCFGNAV5.reserved1[1]      = 0x00
        UBXCFGNAV5.staticHoldMaxDist = 0x00
        UBXCFGNAV5.utcStandard       = 0x00
        UBXCFGNAV5.reserved2[0]      = 0x00
        UBXCFGNAV5.reserved2[1]      = 0x00
        UBXCFGNAV5.reserved2[2]      = 0x00
        UBXCFGNAV5.reserved2[3]      = 0x00        

        ck_a, ck_b = self.checksum( bytes(ubloxPacketHeader) + bytes(UBXCFGNAV5))
        ubloxPacketCk.cka = ck_a
        ubloxPacketCk.ckb = ck_b
    
        sendByteArray = bytes(ubloxPacketSync) + bytes(ubloxPacketHeader) + bytes(UBXCFGNAV5) + bytes(ubloxPacketCk)
        if(self._debug):
            for b in sendByteArray:
                print(hex(b))
        for retry in range(10):
            ack = False
            self._serialPort.write(sendByteArray)
            preambleFound = False
            for preambleCount in range(8200):
                rsp = self._serialPort.read()
                if rsp == ubloxPacketDefs.PREAMBLE1.to_bytes(1,"big"):
                    preambleFound = True
                    break
            if(preambleFound):
                rsp = self._serialPort.read(9)
                expectedRspIndx = 0
                ack = True
                for b in rsp:
                    if(b != expectedRsp[expectedRspIndx]):
                        ack = False
                    expectedRspIndx +=1
            if(ack):
                rtn = True
                break            
        if(rtn):
            print("GPS dynModel set to 8: airborne with <4g acceleration")          
        else:
            print("GPS dynModel FAILED to set to 8: airborne with <4g acceleration")            
            
        return rtn
    
    def setPowerMode(self):
        
        rtn = False
        
        expectedRsp = [ubloxPacketDefs.PREAMBLE2,
                       ubloxPacketDefs.CLASS_ACK,
                       ubloxPacketDefs.MSG_ACK_ACK,
                       0x02,
                       0x00,
                       ubloxPacketDefs.CLASS_CFG,
                       ubloxPacketDefs.MSG_CFG_RXM,
                       0x1F,
                       0x48
                       ]
        
        ubloxPacketSync   = ubloxPacketDefs.ubloxPacketSyncType()
        ubloxPacketHeader = ubloxPacketDefs.ubloxPacketHeaderType()
        UBXCFGRXMT        = ubloxPacketDefs.UBXCFGRXMType()
        ubloxPacketCk     = ubloxPacketDefs.ubloxPacketCkType()

        ubloxPacketSync.sync1    = ubloxPacketDefs.PREAMBLE1 
        ubloxPacketSync.sync2    = ubloxPacketDefs.PREAMBLE2
        ubloxPacketHeader.Class  = ubloxPacketDefs.CLASS_CFG
        ubloxPacketHeader.id     = ubloxPacketDefs.MSG_CFG_RXM
        ubloxPacketHeader.length = ctypes.sizeof(UBXCFGRXMT)
        
        UBXCFGRXMT.reserved1     = 0x08
        UBXCFGRXMT.lpMode        = 0x01     

        ck_a, ck_b = self.checksum( bytes(ubloxPacketHeader) + bytes(UBXCFGRXMT))
        ubloxPacketCk.cka = ck_a
        ubloxPacketCk.ckb = ck_b
    
        sendByteArray = bytes(ubloxPacketSync) + bytes(ubloxPacketHeader) + bytes(UBXCFGRXMT) + bytes(ubloxPacketCk)
        for retry in range(10):
            ack = False
            self._serialPort.write(sendByteArray)
            preambleFound = False
            for preambleCount in range(8200):
                rsp = self._serialPort.read()
                if rsp == ubloxPacketDefs.PREAMBLE1.to_bytes(1,"big"):
                    preambleFound = True
                    break
            if(preambleFound):
                rsp = self._serialPort.read(9)
                expectedRspIndx = 0
                ack = True
                for b in rsp:
                    if(b != expectedRsp[expectedRspIndx]):
                        ack = False
                    expectedRspIndx +=1
            if(ack):
                rtn = True
                break            
           
        if(rtn):
            print("GPS power save mode set")          
        else:
            print("FAILED to set GPS power save mode")            
            
        return rtn    

    def newCheckSum(self, NMEASentence, debug=False):
        checkSumVal = 0
        chksumdata = re.sub("(\r\n)","", NMEASentence[NMEASentence.find("$")+1:NMEASentence.find("*")])
        for c in chksumdata:
            # XOR'ing value of csum against the next char in line
            # and storing the new XOR value in csum
            checkSumVal ^= ord(c)
        hexVal =  "{:02x}".format(checkSumVal).upper()
        newNMEASentence = "$" + chksumdata + "*" + hexVal + "\r\n"

        return newNMEASentence

        
    def _gpsThreadFunction(self):
        print("**** Starting GPS Thread ******")
        
        status = True
        rtn = self.setGNSS()
        if(rtn == False):    
            status = False   
        
        rtn = self.setDynModel()
        if(rtn == False):    
            status = False

        rtn = self.setPowerMode()
        if(rtn == False):    
            status = False
            
        if(status == False):
            print("GPS Failed to configure")

        while(self._runnable):
            try:
                temp = None
                temp = self._serialPort.readline().decode().strip()
                if(temp.find('GGA') > 0):
                    temp = temp.replace("GNGGA","GPGGA")
                    self.ggaSentence = self.newCheckSum(temp)

                if(temp.find('RMC') > 0):
                    temp = temp.replace("GNRMC","GPRMC")
                    self.rmcSentence = self.newCheckSum(temp)
                
            except Exception as e:
                print(e)

    def START(self):
        
        self._serialPort = serial.Serial(self._port,baudrate=self._baud)
        self._serialPort.write(ubloxPacketDefs.RESET_CMD)
        time.sleep(1)               
            
        self.gpsThread.start()
        time.sleep(1)                   

    def STOP(self):
        self._runnable = False
        time.sleep(.1)