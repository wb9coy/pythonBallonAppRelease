import time
import subprocess
import gpiozero
class powerUtils:
  
    def powerOff(self):
        switchGPIO   = gpiozero.DigitalOutputDevice(4)
        systemUpGPIO = gpiozero.DigitalOutputDevice(17)

        switchGPIO.on()
        time.sleep(.5)
        switchGPIO.off()

        systemUpGPIO.on()

        cmd = ["sudo","shutdown","-h","now"]
        subprocess.call(cmd)

    def signalSystemUp(self):

        systemUpGPIO = gpiozero.DigitalOutputDevice(17)

        print("Send out the SYS_UP signal")
        systemUpGPIO.on()
        time.sleep(.5)
        systemUpGPIO.off()

