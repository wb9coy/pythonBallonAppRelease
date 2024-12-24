import os
import datetime
import FSKModem
import cameraProc
import intervalTimer
import processCallSignData
import processInfoData
import sendImageFileProc
import configparser
import ubloxGPSProc
import sensorProc
import powerUtils
import packetDefs
import utils
import logger
import queue

versionInfo      = "Payload Version 1.0"

logDir           = os.path.abspath(os.getcwd()+"/log")
flightDir        = logDir + "/" + datetime.datetime.now().strftime("%Y%m%d%H%M%S")
picDir           = "/" + flightDir + "/pics"
vidDir           = "/" + flightDir + "/vid"
dataDir          = "/" + flightDir + "/data"

bps              = 9600
afcbw            = 31300
rxbw             = 20800
resetPin         = None
callSignInterval = 600 #10 min
picDirHighRes    = picDir + "/HighRes"
picDirLowRes     = picDir + "/LowRes"
flightDataPath   = dataDir + "/flightData.txt"

config = configparser.ConfigParser()
config.read('config.ini')

spiChannel          = int(config.get('modem', 'spiCS'))
dio0GpioN           = int(config.get('modem', 'dio0GpioN'))
freq                =    int(config.get('modem', 'freq'))
freqDev             = int(config.get('modem', 'freqDev'))
tx_power            = int(config.get('modem', 'tx_power'))
rotation            = int(config.get('cam',   'rotation'))
callSign            = config.get('payload', 'callSign')
gpsEnabled          = int(config.get('sensor', 'gpsEnabled'))
zero2GoOminiEnabled = int(config.get('sensor', 'zero2GoOminiEnabled'))
bme280Enabled       = int(config.get('sensor', 'bme280Enabled'))
lowVoltageThres     = float(config.get('zero2GoOmini', 'lowVoltageThres'))
voltageAdj          = float(config.get('zero2GoOmini', 'voltageAdj'))

gpsPort    = "/dev/serial0"
gpsBaund   = 9600

gpsInterval            = 15
batteryVoltageInterval = 30
internalTempInterval   = 60
externalTempInterval   = 30
pressureInterval       = 30
humidityInterval       = 60
infoInterval           = 700

debug                  = False

sensorDataQueue        = queue.Queue(100*1024)

powerUtilsObj          = powerUtils.powerUtils()
modemObj               = FSKModem.FSKModem(spiChannel,dio0GpioN,freq,tx_power,bps,afcbw,rxbw,freqDev,resetPin,sensorDataQueue,debug)
cameraProcObj          = cameraProc.cameraProc(picDirHighRes,picDirLowRes,vidDir,rotation)
processCallSignDataObj = processCallSignData.processCallSignData(callSign,modemObj.txDataQueue)
processInfoDataObj     = processInfoData.processInfoData(modemObj.txDataQueue,versionInfo)
sendImageFileProcObj   = sendImageFileProc.sendImageFileProc(picDirLowRes,
                                                             cameraProcObj.imagePicNumQueue,
                                                             modemObj.txDataQueue,
                                                             modemObj.endImageEvent)
IDTimerObj           = intervalTimer.intervalTimer(interval=callSignInterval,callback=processCallSignDataObj.sendCallSignDataPacket)
infoTimerObj         = intervalTimer.intervalTimer(interval=infoInterval,callback=processInfoDataObj.sendInfoDataPacket)
loggerObj            = logger.logger(flightDataPath)

def displayParameters():
    print("versionInfo      = " + str(versionInfo))
    print("spiChannel       = " + str(spiChannel))
    print("dio0GpioN        = " + str(dio0GpioN))
    print("freq             = " + str(freq))
    print("freqDev          = " + str(freqDev))
    print("tx_power         = " + str(tx_power))
    print("bps              = " + str(bps))
    print("afcbw            = " + str(afcbw))
    print("rxbw             = " + str(rxbw))
    print("resetPin         = " + str(resetPin))
    print("callSignInterval = " + str(callSignInterval))
    print("picDirHighRes    = " + picDirHighRes)
    print("picDirLowRes     = " + picDirLowRes)
    print("vidDir           = " + vidDir)
    print("flightDataPath   = " + flightDataPath)
    print("rotation         = " + str(rotation))
    print("callSign         = " + callSign)


def main():
    rtn    = True
    status = True

    powerUtilsObj.signalSystemUp()

    displayParameters()
    
    rtn = modemObj.run()
    if(rtn != True):
        status = False
        print("Failed to run modem")
    else: 
        if(os.path.exists(logDir) == False):
            os.mkdir(logDir,0o755)

        os.mkdir(flightDir,0o755)
        os.mkdir(picDir,0o755)
        os.mkdir(picDirHighRes,0o755)
        os.mkdir(picDirLowRes,0o755)
        os.mkdir(vidDir,0o755)
        os.mkdir(dataDir,0o755)

        numFlightsToSave = 5
        spaceLimit       = 5 #GB
        utils.cleanUpOldFlightData(spaceLimit,numFlightsToSave,logDir)

        rtn = loggerObj.START()
        if(rtn):
            loggerObj.LOG("$INFO " + versionInfo)
        else:
            print("Logger thread failed to start")
            
        sendImageFileProcObj.START()
        cameraProcObj.START()
        processCallSignDataObj.sendCallSignDataPacket()
        processInfoDataObj.sendInfoDataPacket()
        IDTimerObj.START()
        infoTimerObj.START() 
        ubloxGPSObj = None
        if(gpsEnabled):
            ubloxGPSObj= ubloxGPSProc.ubloxGPSProc(gpsPort,gpsBaund,sensorDataQueue)
            ubloxGPSObj.START()

        sensorProcObj = sensorProc.sensorProc(ubloxGPSObj,
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
                                              loggerObj)

        sensorProcObj.initialize()
        sensorProcObj.START()
        
        modemObj.txProcess.join()
        modemObj.rxProcess.join()
        cameraProcObj.join()
        sendImageFileProcObj.join()
        IDTimerObj.join()
        

if __name__ == "__main__":
    main()
