import threading
import time
import ctypes
import reedsolo
import RFM9x
import packetDefs
import cw

class txProc():
    def __init__(self,
                 dataQueue,
                 sensorQueue,
                 sendFSK,
                 dataLED,
                 cwObj,
                 endImageEvent,
                 debug=False):
        
        self._runnable              = True
        self.txThread               = threading.Thread(target=self._txThreadFunction)
        self._dataQueue             = dataQueue
        self._sensorQueue           = sensorQueue
        self._sendFSK               = sendFSK
        self._dataLED               = dataLED
        self._cwObj                 = cwObj
        self.endImageEvent          = endImageEvent
        self._debug                 = debug

    def join(self):
        self.txThread.join()
        
    def _txThreadFunction(self):
        print("**** Starting Tx Thread ******")
        HABPacketCallSignData = packetDefs.HABPacketCallSignDataType()
        
        rsc = reedsolo.RSCodec(packetDefs.NPAR,fcr=1)

        while(self._runnable):
            if self._sensorQueue.empty():
                pass
            else:
                self._dataLED.on()
                qData = self._sensorQueue.get()
                lenOfData = len(qData) - packetDefs.NPAR
                encodedData = rsc.encode(qData[:lenOfData])
                padLen = packetDefs.MTU - len(encodedData)
                txData = encodedData + b' ' * padLen 
                self._sendFSK(bytes(txData))
                time.sleep(.01)
                self._dataLED.off()

            if self._dataQueue.empty():
                time.sleep(.01)
            else:
                self._dataLED.on()
                qData = self._dataQueue.get()
                lenOfData = len(qData) - packetDefs.NPAR
                encodedData = rsc.encode(qData[:lenOfData])
                padLen = packetDefs.MTU - len(encodedData)
                txData = encodedData + b' ' * padLen 
                self._sendFSK(bytes(txData))
                self._dataLED.off()
            
                packetType = int.from_bytes(qData[0:1], "little")
                if(packetType == packetDefs.CW_ID):
                    ctypes.memmove(ctypes.pointer(HABPacketCallSignData),qData,ctypes.sizeof(HABPacketCallSignData))
                    bytesCallSign = HABPacketCallSignData.callSignData[0:HABPacketCallSignData.callSignDataLen]
                    callSign = bytes(bytesCallSign).decode('ascii')
                    self._cwObj.send(callSign)
                elif (packetType == packetDefs.START_IMAGE):
                    pass
                elif (packetType == packetDefs.END_IMAGE):
                    self.endImageEvent.set()

                
        print("End txThreadFunction")
                                     
    def _START(self):
        self.txThread.start()
        time.sleep(1)
        
    def STOP(self):
        self._runnable = False
        time.sleep(.1)
        
    def keyDown(self):
        self._setModeTx()

    def keyUp(self):
        self._setModeRx()
        
class rxProc():
    def __init__(self,
                 dataQueue,
                 led,
                 debug=False):
        self._debug     = True
        
        self._runnable  = True
        self._rxThread  = threading.Thread(target=self._rxThreadFunction)
        self._dataQueue = dataQueue
        self._led       = led
        
    def join(self):
        self._rxThread.join()
        
    def _rxThreadFunction(self):
        print("**** Starting Rx Thread ******")
        while(self._runnable):
            self._led.off()
            try:
                data = self._dataQueue.get(timeout=1)
                self._led.on()
                if(self._debug):
                    print(data)
            except:
                pass
                
        print("End rxThreadFunction")
                                     
    def _START(self):
        self._rxThread.start()
        time.sleep(1)
        
    def STOP(self):
        self._runnable = False
        time.sleep(.1)
        
class FSKModem(RFM9x.RFM9x):
    def __init__(self,spiChannel,dio0GpioN,freq,txPower,bps,afcbw,rxbw,freqDev,resetPin,sensorQueue,debug=False):
        super().__init__(spiChannel,dio0GpioN,resetPin,debug)
        
        self._freq          = freq
        self._txPower       = txPower
        self._bps           = bps
        self._afcbw         = afcbw
        self._rxbw          = rxbw
        self._freqDev       = freqDev
        self._sensorQueue   = sensorQueue
        self._debug         = debug
         
        self.endImageEvent = threading.Event()
        self._cwObj        = cw.cw(self.setModeTx,self.setModeRx)
        self.txProcess     = txProc(self.txDataQueue,self._sensorQueue,self.sendFSK, self.dataLED, self._cwObj, self.endImageEvent, self._debug)
        self.rxProcess     = rxProc(self.rxDataQueue,self.linkLED,self._debug)
        
    def run(self):
        status = True
        
        rtn = self.setMaxCurrent(0x1b)
        if(rtn != True):
            status = False
            print("Could not set Max Current")
            
        rtn = self.setFSK()
        if(rtn != 0):
            status = False
            print("Could not set FSK mode")
        else:
            print("FSK mode set")
            
        if(status):
            rtn = self.setBitrate(self._bps)
            if(rtn != True):
                status = False
                print("Could not set bit rate")
                
        if(status):
            rtn = self.setDeviationFSK(self._freqDev)
            if(rtn != True):
                status = False
                print("Could not set bit rate")
                
        if(status):
            rtn = self.setAFCBandwidth(self._afcbw)
            if(rtn != True):
                status = False
                print("Could not set AFC Bandwidth")
                
        if(status):
            rtn = self.setRxBandwidth(self._rxbw)
            if(rtn != True):
                status = False
                print("Could not set Rx Bandwidth")
                
        if(status):
            rtn = self.setGaussian(bt=1)
            if(rtn != True):
                status = False
                print("Could not set Gaussian")
                
        if(status):
            rtn = self.setRxConf(0x1E)
            if(rtn != True):
                status = False
                print("Could not set Rx Config")
                
        syncBytes = bytearray([0x08,0x6D,0x53,0x88])
        if(status):
            rtn = self.setSyncConf(0x53,syncBytes)
            if(rtn != True):
                status = False
                print("Could not set Rx Config")
                
        if(status):
            rtn = self.setPreambleLength(8)
            if(rtn != True):
                status = False
                print("Could not set preamble length")
                
        if(status):
            rtn = self.setPreambleDetect(0xAA)
            if(rtn != True):
                status = False
                print("Could not set preamble detect")
                
        if(status):
            rtn = self.setPacketConfig(0x08,0x40)
            if(rtn != True):
                status = False
                print("Could not set packet config")
                                
        if(status):
            rtn = self.setStandbye()
            if(rtn != True):
                status = False
                print("Could not set standbye")
                
        if(status):
            rtn = self.setFrequency(self._freq)
            if(rtn != True):
                status = False
                print("Could not set frequency")
                
        if(status):
            rtn = self.setTxPower(self._txPower)
            if(rtn != True):
                status = False
                print("Could not set Tx power")
                        
        if(status):
            rtn = self.clearIRQFlags()
            if(rtn != True):
                status = False
                print("Could not clear IRQ flags")
                
        if(status):
            self.txProcess._START()
            self.rxProcess._START()
            self.setModeRx()
            self.linkLED.off()
    
        return status
        
        
    def set_mode_tx(self):
        pass