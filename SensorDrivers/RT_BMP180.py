#!/usr/bin/python

'''
////////////////////////////////////////////////////////////////////////////
//
//  This file is part of RTMQTT
//
//  Copyright (c) 2015, richards-tech, LLC
//
//  Permission is hereby granted, free of charge, to any person obtaining a copy of
//  this software and associated documentation files (the "Software"), to deal in
//  the Software without restriction, including without limitation the rights to use,
//  copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the
//  Software, and to permit persons to whom the Software is furnished to do so,
//  subject to the following conditions:
//
//  The above copyright notice and this permission notice shall be included in all
//  copies or substantial portions of the Software.
//
//  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
//  INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
//  PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
//  HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
//  OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
//  SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

from RT_I2C import RT_I2C
from RT_NullSensor import RT_NullSensor

# Hardware address

BMP180_ADDRESS = 0x77                   # i2c address

# Register defs

BMP180_REG_AC1 = 0xaa                   # first calibration coefficient
BMP180_REG_ID = 0xd0                    # the id register

# Conversion reg defs

BMP180_REG_SCO = 0xf4                   # start conversion reg address

BMP180_SCO_TEMPCONV = 0x2e              # temperature conversion
BMP180_SCO_PRESSURECONV_ULP = 0         # ultra low power pressure conversion
BMP180_SCO_PRESSURECONV_STD = 1         # standard pressure conversion
BMP180_SCO_PRESSURECONV_HR = 2          # high res pressure conversion
BMP180_SCO_PRESSURECONV_UHR = 3         # ultra high res pressure conversion

# Result reg def

BMP180_REG_RESULT = 0xf6
BMP180_REG_XLSB = 0xf8

# State definitions

BMP180_STATE_IDLE = 0
BMP180_STATE_TEMPERATURE = 1
BMP180_STATE_PRESSURE = 2

class RT_BMP180(RT_NullSensor):
    ''' richards-tech driver for the BMP180 pressure sensor '''
    
    def __init__(self): 
        RT_NullSensor.__init__(self)
        self.oss = BMP180_SCO_PRESSURECONV_ULP
        self.temperature = 0
        self.pressure = 0
        self.sensorValid = True
 
    def __readShort(self, data0, data1):
        res = data1 | (data0 << 8)
        if res > 32767: 
            res -= 65536
            
        return res  
        
    def __readUnsignedShort(self, data0, data1):
        res = data1 | (data0 << 8)
        return res  
       
    def enable(self, busnum=-1, debug=False):
        # check if already enabled
        if (self.dataValid):
            return
        # check for the presence of the pressure sensor
        self.bmp = RT_I2C(BMP180_ADDRESS, busnum, debug)
        if self.bmp.missing:
            self.sensorValid = False
            return

        if self.bmp.readU8(BMP180_REG_ID) != 0x55:
            print("BMP180 not found")
            self.sensorValid = False
            return
        
        # start the pressure sensor running
        
        data = self.bmp.readList(BMP180_REG_AC1, 22)
  
        self.AC1 = self.__readShort(data[0], data[1]);
        self.AC2 = self.__readShort(data[2], data[3]);
        self.AC3 = self.__readShort(data[4], data[5]);
        self.AC4 = self.__readUnsignedShort(data[6], data[7]);
        self.AC5 = self.__readUnsignedShort(data[8], data[9]);
        self.AC6 = self.__readUnsignedShort(data[10], data[11]);
        self.B1 = self.__readShort(data[12], data[13]);
        self.B2 = self.__readShort(data[14], data[15]);
        self.MB = self.__readShort(data[16], data[17]);
        self.MC = self.__readShort(data[18], data[19]);
        self.MD = self.__readShort(data[20], data[21]);

        self.state = BMP180_STATE_IDLE;
 
    # Read the sensor
    def readPressure(self):
        ''' returns pressure in hPa '''
        return self.pressure
        
    def readTemperature(self):
        ''' returns temperature in degrees C '''
        return self.temperature
        
    def background(self):

        if (self.state == BMP180_STATE_IDLE):
            # start a temperature conversion
            self.bmp.write8(BMP180_REG_SCO, BMP180_SCO_TEMPCONV)
            self.state = BMP180_STATE_TEMPERATURE
            return
	        
        elif (self.state == BMP180_STATE_TEMPERATURE):
	        # see if temperature ready
            res = self.bmp.readU8(BMP180_REG_SCO)
            if ((res & 0x20) == 0x20):
                return                                      # conversion not finished
			
			# get the temperature
            data = self.bmp.readList(BMP180_REG_RESULT, 2)
            self.uncompensatedTemperature = self.__readUnsignedShort(data[0], data[1])
		
		    # start the pressure reading
            self.bmp.write8(BMP180_REG_SCO, 0x34 + (self.oss << 6))
            self.state = BMP180_STATE_PRESSURE
            return

        elif (self.state == BMP180_STATE_PRESSURE):
            # see if pressure ready
            res = self.bmp.readU8(BMP180_REG_SCO)
            if ((res & 0x20) == 0x20):
                return                                          # conversion not finished

            data = self.bmp.readList(BMP180_REG_RESULT, 2)
            self.rawPressure = self.__readUnsignedShort(data[0], data[1])
            
      	    XLSB = self.bmp.readU8(BMP180_REG_XLSB)
            self.uncompensatedPressure = ((self.rawPressure << 8) + XLSB) >> (8 - self.oss);
            
            self.compensateTemperature()
            self.compensatePressure()
            self.dataValid = True

            self.state = BMP180_STATE_IDLE

    def compensateTemperature(self):
        # calculate compensated temperature
        self.X1 = ((self.uncompensatedTemperature - self.AC6) * self.AC5) / 32768

        if ((self.X1 + self.MD) == 0):
            return
		
        self.X2 = (self.MC * 2048)  / (self.X1 + self.MD)
        self.B5 = self.X1 + self.X2
        self.temperature = float((self.B5 + 8) / 16) / 10

    def compensatePressure(self):
        # calculate compensated pressure

        self.B6 = self.B5 - 4000
        self.X1 = (self.B2 * ((self.B6 * self.B6) / 4096)) / 2048
        self.X2 = (self.AC2 * self.B6) / 2048
        self.X3 = self.X1 + self.X2
        self.B3 = (((self.AC1 * 4 + self.X3) << self.oss) + 2) / 4
        self.X1 = (self.AC3 * self.B6) / 8192
    	self.X2 = (self.B1 * ((self.B6 * self.B6) / 4096)) / 65536
        self.X3 = ((self.X1 + self.X2) + 2) / 4
        self.B4 = (self.AC4 * (self.X3 + 32768)) / 32768
        self.B7 = (self.uncompensatedPressure - self.B3) * (50000 >> self.oss)

        if (self.B7 > 0):
            self.p = (self.B7 * 2) / self.B4
        else:
            self.p = ((0x100000000 + self.B7) / self.B4) * 2

        self.X1 = (self.p / 256) * (self.p / 256)
        self.X1 = (self.X1 * 3038) / 65536
        self.X2 = (-7357 * self.p) / 65536;
        self.pressure = float(self.p + (self.X1 + self.X2 + 3791) / 16) / 100  # pressure in hPa units
        
  
    def setFakeData(self):
        # call this function for testing only
        # should give T = 15.0 (15.0C) and pressure 699.65 (hPa)

        self.AC1 = 408
        self.AC2 = -72
        self.AC3 = -14383
        self.AC4 = 32741
        self.AC5 = 32757
        self.AC6 = 23153
        self.B1 = 6190
        self.B2 = 4
        self.MB = -32767
        self.MC = -8711
        self.MD = 2868
        
        self.uncompensatedTemperature = 27898
        self.uncompensatedPressure = 23843

# test code
if __name__ == "__main__":
    bmp = RT_BMP180()                                       # create an instance in test mode
    bmp.setFakeData()                                       # set up the fake data
    bmp.compensateTemperature()
    bmp.compensatePressure()
    # this should print 150, 699.65 (seems to give 699.64...)
    print "Compensated temp = %d, compensated pressure = %d" % (bmp.temperature, bmp.pressure)
    

