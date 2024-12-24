import time
import threading
import ctypes
import packetDefs
import libscrc
import zero2GoOmini
import gpiozero
import smbus2
import bme280

class sensorProc():
    def __init__(self,
                 gpsObj,
                 gpsInterval,
                 batteryVoltageInterval,
                 internalTempInterval,
                 externalTempInterval,
                 pressureInterval,
                 humidityInterval,
                 sensorDataQueue,
                 zero2GoOminiEnabled,
                 bme280Enabled,
                 lowVoltageThres,
                 voltageAdj,
                 powerUtilsObj,
                 loggerObj,
                 debug=False):
        self._gpsObj                 = gpsObj
        self._gpsInterval            = gpsInterval
        self._batteryVoltageInterval = batteryVoltageInterval
        self._internalTempInterval   = internalTempInterval
        self._externalTempInterval   = externalTempInterval
        self._pressureInterval       = pressureInterval
        self._humidityInterval       = humidityInterval
        self._sensorDataQueue        = sensorDataQueue
        self._zero2GoOminiEnabled    = zero2GoOminiEnabled
        self._bme280Enabled          = bme280Enabled
        self._lowVoltageThres        = lowVoltageThres
        self._voltageAdj             = voltageAdj
        self._lowVoltageCount        = 0

        self._powerUtilsObj          = powerUtilsObj
        self._loggerObj              = loggerObj

        self._debug                  = debug

        self._runnable        = True
        self._sensorThread    = threading.Thread(target=self._sensorThreadFunction)

        self._zero2GoOminiOK          = True
        self._zero2GoOminiI2CAddress  = 0x29
        self._zero2GoOminiObj = zero2GoOmini.zero2GoOmini(self._zero2GoOminiI2CAddress)

        self._i2cOK                   = True
        self._i2cBus                  = None

        self._bme280OK                = True
        self._bmeI2CAddress           = 0x77
        self._bme280CalibrationParams = None

    def initialize(self):

        if(self._zero2GoOminiEnabled):
            status = self._zero2GoOminiObj.initialize()
            if(status == False):
                print("Failed to initialize zero2GoOmini device")
                self._zero2GoOminiOK = False
            else:
                print("zero2GoOmini device initialized")

        try:
            self._i2cBus= smbus2.SMBus(1)
            print("I2C successfully detected")

        except Exception as e:
            print("Failed to initialize I2C")
            self._i2cOK = False
            print(e)


        if(self._bme280Enabled):
            if(self._i2cOK):
                try:
                    self._bme280CalibrationParams = bme280.load_calibration_params(self._i2cBus, self._bmeI2CAddress)
                    print("BME280 successfully detected")
                except Exception as e:
                    print("Failed to initialize BME280")
                    self._bme280OK = False
                    print(e)


    def join(self):
        self._sensorThread .join()

    def _sensorThreadFunction(self):
        print("**** Starting Sensor Thread ******")
        tic = 0

        while(self._runnable):
            tic+=1
            
            if(tic % self._gpsInterval == 0):
                if(self._gpsObj == None):
                    pass
                else:
                    self._sendGGA(self._gpsObj.getGGA())
                    self._sendRMC(self._gpsObj.getRMC())

            if(tic % self._batteryVoltageInterval == 0):
                if(self._zero2GoOminiEnabled):
                    if(self._zero2GoOminiOK):
                        self._sendBatteryVoltage(2,self._lowVoltageThres)
            if(tic % self._internalTempInterval   == 0):
                self._sendInternalTemp()
            if(tic % self._externalTempInterval   == 0):
                self._sendExtTemp()
            if(tic % self._pressureInterval       == 0):
                self._sendPressure()
            if(tic % self._humidityInterval       == 0):
                self._sendHumidity()

            time.sleep(1)

    def START(self):
        self._sensorThread.start()
        time.sleep(1)
        
    def STOP(self):
        self._runnable = False


    def _sendGGA(self,ggaSentence):
        HABPacketGPSData = packetDefs.HABPacketGPSDataType()
        if(ggaSentence != None):
            lenGGA = len(ggaSentence)
            if(lenGGA > packetDefs.MAX_GPS_DATA):
                HABPacketGPSData.packetType = packetDefs.GPS_GGA_1
                temp = ggaSentence[:packetDefs.MAX_GPS_DATA]
                HABPacketGPSData.gpsDataLen = len(temp)
                ctypes.memmove(ctypes.pointer(HABPacketGPSData.gpsData), str.encode(temp), HABPacketGPSData.gpsDataLen)
                sendByteArray = bytes(HABPacketGPSData)
                self._sensorDataQueue.put(sendByteArray)

                HABPacketGPSData.packetType = packetDefs.GPS_GGA_2
                temp = ggaSentence[packetDefs.MAX_GPS_DATA:lenGGA]
                HABPacketGPSData.gpsDataLen = len(temp)
                ctypes.memmove(ctypes.pointer(HABPacketGPSData.gpsData), str.encode(temp), HABPacketGPSData.gpsDataLen)
                sendByteArray = bytes(HABPacketGPSData)
                self._sensorDataQueue.put(sendByteArray)
            else:
                HABPacketGPSData.packetType = packetDefs.GPS_GGA
                HABPacketGPSData.gpsDataLen = lenGGA
                ctypes.memmove(ctypes.pointer(HABPacketGPSData.gpsData), str.encode(ggaSentence), HABPacketGPSData.gpsDataLen)
                sendByteArray = bytes(HABPacketGPSData)
                self._sensorDataQueue.put(sendByteArray)

            gga = ggaSentence.replace('\r\n\0',"")
            self._loggerObj.LOG(gga)

    def _sendRMC(self,rmcSentence):
        HABPacketGPSData = packetDefs.HABPacketGPSDataType()
        if(rmcSentence != None):
            lenRMC = len(rmcSentence)
            if(lenRMC > packetDefs.MAX_GPS_DATA):
                HABPacketGPSData.packetType = packetDefs.GPS_RMC_1
                temp = rmcSentence[:packetDefs.MAX_GPS_DATA]
                HABPacketGPSData.gpsDataLen = len(temp)
                ctypes.memmove(ctypes.pointer(HABPacketGPSData.gpsData), str.encode(temp), HABPacketGPSData.gpsDataLen)
                sendByteArray = bytes(HABPacketGPSData)
                self._sensorDataQueue.put(sendByteArray)

                HABPacketGPSData.packetType = packetDefs.GPS_RMC_2
                temp = rmcSentence[packetDefs.MAX_GPS_DATA:lenRMC]
                HABPacketGPSData.gpsDataLen = len(temp)
                ctypes.memmove(ctypes.pointer(HABPacketGPSData.gpsData), str.encode(temp), HABPacketGPSData.gpsDataLen)
                sendByteArray = bytes(HABPacketGPSData)
                self._sensorDataQueue.put(sendByteArray)
            else:
                HABPacketGPSData.packetType = packetDefs.GPS_RMC
                HABPacketGPSData.gpsDataLen = lenRMC
                ctypes.memmove(ctypes.pointer(HABPacketGPSData.gpsData), str.encode(rmcSentence), HABPacketGPSData.gpsDataLen)
                sendByteArray = bytes(HABPacketGPSData)
                self._sensorDataQueue.put(sendByteArray)

            rmc = rmcSentence.replace('\r\n\0',"")
            self._loggerObj.LOG(rmc)

    def _sendBatteryVoltage(self,chan,lowVoltageThres):

        if(self._zero2GoOminiEnabled):
            HABPacketBattInfoData = packetDefs.HABPacketBattInfoDataType()

            voltage  = 0.0
            try:
                if(chan == 1):
                    voltage = self._zero2GoOminiObj.getBattVoltageChan1()
                elif(chan == 2):
                    voltage = self._zero2GoOminiObj.getBattVoltageChan2()
                elif(chan == 3):
                    voltage = self._zero2GoOminiObj.getBattVoltageChan3()
            except Exception as e:
                print(e)

            voltage = voltage + self._voltageAdj
            voltage = round(voltage,1)
        
            if(self._debug):
                print(voltage)
                print(self._lowVoltageThres)

            HABPacketBattInfoData.packetType   = packetDefs.BATT_INFO
            HABPacketBattInfoData.battInfoData = voltage
            tempLen =  ctypes.sizeof(HABPacketBattInfoData) - packetDefs.NPAR - packetDefs.CRC16_LEN 
            crcByteArray = bytes(HABPacketBattInfoData)
            crc16 = libscrc.ibm(crcByteArray[:tempLen])
            HABPacketBattInfoData.crc16 = crc16              
            sendByteArray = bytes(HABPacketBattInfoData)
            self._sensorDataQueue.put(sendByteArray)
            self._loggerObj.LOG("$BATT " + str(voltage) + "V")

            if(voltage > 1.0):
                if(voltage < self._lowVoltageThres):
                    self._lowVoltageCount +=1
                    if(self._lowVoltageCount > 5):
                        self._loggerObj.LOG("*********************************")
                        self._loggerObj.LOG("LOW BATTERY VOLTAGE SHUTTING DOWN")
                        self._loggerObj.LOG("*********************************")
                        self._powerUtilsObj.powerOff()
                else:
                    self._lowVoltageCount = 0

    def _sendInternalTemp(self):
        HABPacketIntTempInfoData = packetDefs.HABPacketIntTempInfoDataType()

        cpuTemp = 0.0
        try:
            CPUTemperatureObj = gpiozero.CPUTemperature()
            cpuTemp = CPUTemperatureObj.temperature
        except Exception as e:
            print(e)

        HABPacketIntTempInfoData.packetType      = packetDefs.INT_TEMP
        degF = (cpuTemp * 9/5) + 32
        HABPacketIntTempInfoData.intTempInfoData = degF
        tempLen =  ctypes.sizeof(HABPacketIntTempInfoData) - packetDefs.NPAR - packetDefs.CRC16_LEN 
        crcByteArray = bytes(HABPacketIntTempInfoData)
        crc16 = libscrc.ibm(crcByteArray[:tempLen])
        HABPacketIntTempInfoData.crc16 = crc16          
        sendByteArray = bytes(HABPacketIntTempInfoData)
        self._sensorDataQueue.put(sendByteArray)
        df = round(degF)
        self._loggerObj.LOG("$INT_TEMP " + str(df) + "F")

    def _sendPressure(self):

        if(self._bme280Enabled):
            HABPacketPressureInfoData = packetDefs.HABPacketPressureInfoDataType()

            try:
                # Read sensor data
                data = bme280.sample(self._i2cBus, self._bmeI2CAddress, self._bme280CalibrationParams)
                HABPacketPressureInfoData.packetType       = packetDefs.PRESS_INFO
                HABPacketPressureInfoData.pressureInfoData = data.pressure
                tempLen =  ctypes.sizeof(HABPacketPressureInfoData) - packetDefs.NPAR - packetDefs.CRC16_LEN 
                crcByteArray = bytes(HABPacketPressureInfoData)
                crc16 = libscrc.ibm(crcByteArray[:tempLen])
                HABPacketPressureInfoData.crc16 = crc16                 
                sendByteArray = bytes(HABPacketPressureInfoData)
                self._sensorDataQueue.put(sendByteArray)
                p = "{0:.1f}".format(data.pressure)
                self._loggerObj.LOG("$PRES " + str(p) + "hPa")
            except Exception as e:
                print(e)

    def _sendExtTemp(self):

        if(self._bme280Enabled):
            HABPacketExtTempInfoData = packetDefs.HABPacketExtTempInfoDataType()

            try:
                # Read sensor data
                data = bme280.sample(self._i2cBus, self._bmeI2CAddress, self._bme280CalibrationParams)
                HABPacketExtTempInfoData.packetType       = packetDefs.EXT_TEMP
                HABPacketExtTempInfoData.extTempInfoData  = (data.temperature * 9/5) +32
                tempLen =  ctypes.sizeof(HABPacketExtTempInfoData) - packetDefs.NPAR - packetDefs.CRC16_LEN 
                crcByteArray = bytes(HABPacketExtTempInfoData)
                crc16 = libscrc.ibm(crcByteArray[:tempLen])
                HABPacketExtTempInfoData.crc16 = crc16                 
                sendByteArray = bytes(HABPacketExtTempInfoData )
                self._sensorDataQueue.put(sendByteArray)
                et = round(HABPacketExtTempInfoData.extTempInfoData)
                self._loggerObj.LOG("$EXT_TEMP " + str(et) + "F")
            except Exception as e:
                print(e)

    def _sendHumidity(self):

        if(self._bme280Enabled):
            HABPacketHumidityInfoData = packetDefs.HABPacketHumidityInfoDataType()

            try:
                # Read sensor data
                data = bme280.sample(self._i2cBus, self._bmeI2CAddress, self._bme280CalibrationParams)
                HABPacketHumidityInfoData.packetType       = packetDefs.HUM_INFO
                HABPacketHumidityInfoData.humidityInfoData = data.humidity
                tempLen =  ctypes.sizeof(HABPacketHumidityInfoData) - packetDefs.NPAR - packetDefs.CRC16_LEN 
                crcByteArray = bytes(HABPacketHumidityInfoData)
                crc16 = libscrc.ibm(crcByteArray[:tempLen])
                HABPacketHumidityInfoData.crc16 = crc16                 
                sendByteArray = bytes(HABPacketHumidityInfoData)
                self._sensorDataQueue.put(sendByteArray)
                h = round(data.humidity)
                self._loggerObj.LOG("$HUM " + str(h) + "RH")

            except Exception as e:
                print(e)














