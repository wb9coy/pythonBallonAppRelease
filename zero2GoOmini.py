import smbus as smbus

class zero2GoOmini():
    def __init__(self,I2CAddress,debug=False):
        self._debug = debug

        self._bus        = None
        self._I2CAddress = I2CAddress

    def initialize(self,i2c_ch=1):
        rtn = True
        try:
            self._bus = smbus.SMBus(i2c_ch)
        except Exception as e:
            rtn = False
            print(e)
        return rtn

    def getBattVoltageChan1(self):
        ba1 = 0
        try:
            val1 = self._bus.read_i2c_block_data(self._I2CAddress, 1)
            val2 = self._bus.read_i2c_block_data(self._I2CAddress, 2)
            ba1 = val1[0] + val2[0]/100
        except Exception as e:
            print(e)
        return ba1

    def getBattVoltageChan2(self):
        ba2 = 0
        try:
            val3 = self._bus.read_i2c_block_data(self._I2CAddress, 3)
            val4 = self._bus.read_i2c_block_data(self._I2CAddress, 4)
            ba2 = val3[0] + val4[0]/100
        except Exception as e:
            print(e)
        return ba2

    def getBattVoltageChan3(self):
        ba3 = 0
        try:
            val5 = self._bus.read_i2c_block_data(self._I2CAddress, 5)
            val6 = self._bus.read_i2c_block_data(self._I2CAddress, 6)
            ba3 = val5[0] + val6[0]/100
        except Exception as e:
            print(e)
        return ba3








      