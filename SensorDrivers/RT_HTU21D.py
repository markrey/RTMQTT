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
import time
import io
import fcntl

# Hardware address

HTU21D_ADDRESS = 0x40                   # i2c address

# Command defs

HTU21D_CMD_TRIG_TEMP = "\xf3"           # no hold temp trigger
HTU21D_CMD_TRIG_HUM = "\xf5"            # no hold humidity trigger
HTU21D_CMD_SOFT_RESET = "\xfe"          # soft reset

# states

HTU21D_STATE_IDLE = 0                   # nothing happening
HTU21D_STATE_TEMP_REQ = 1               # requested temperature
HTU21D_STATE_HUM_REQ = 2                # requested humidity

HTU21D_STATE_INTERVAL = 0.25            # the interval between state changes

class RT_HTU21D(RT_NullSensor):
    ''' richards-tech driver for the HTU21D-F humidity/temperature sensor '''
    
    def __init__(self): 
        RT_NullSensor.__init__(self)
        self.temperature = 0
        self.humidity = 0
        self.sensorValid = True
 
    def enable(self, busnum=-1, debug=False):
        # check if already enabled
        if (self.dataValid):
            return

        self.busnum = busnum if busnum >= 0 else RT_I2C.getPiI2CBusNumber()

        try:
            self.writeI2C = io.open("/dev/i2c-" + str(self.busnum), "wb", 0)
        except:
            self.sensorValid = False
            return

        fcntl.ioctl(self.writeI2C, 0x0703, HTU21D_ADDRESS)
        
        self.readI2C = io.open("/dev/i2c-" + str(self.busnum), "rb", 0)
        fcntl.ioctl(self.readI2C, 0x0703, HTU21D_ADDRESS)
        
        # do a reset and wait 15mS
        self.writeI2C.write(HTU21D_CMD_SOFT_RESET)
        time.sleep(0.015)

        self.lastStateChange = time.time() - HTU21D_STATE_INTERVAL
        self.state = HTU21D_STATE_IDLE
 
    # Read the sensor
    def readHumidity(self):
        ''' returns humidity in %RH '''
        return self.humidity
        
    def readTemperature(self):
        ''' returns temperature in degrees C '''
        return self.temperature
        
    def background(self):
        # only do processing at the appropriate interval
        if ((time.time() - self.lastStateChange) < HTU21D_STATE_INTERVAL):
            return
            
        self.lastStateChange = time.time()

        if (self.state == HTU21D_STATE_IDLE):
            # start a temperature conversion
            self.writeI2C.write(HTU21D_CMD_TRIG_TEMP)
            self.state = HTU21D_STATE_TEMP_REQ
            return
	        
        elif (self.state == HTU21D_STATE_TEMP_REQ):
            # get temperature and then start humidity
            data = bytearray(self.readI2C.read(3))
            self.temperature = -46.85 + 175.72 * float((data[0] << 8) | data[1]) / 65536.0
	        
            # start the pressure reading
            self.writeI2C.write(HTU21D_CMD_TRIG_HUM)
            self.state = HTU21D_STATE_HUM_REQ
            return

        elif (self.state == HTU21D_STATE_HUM_REQ):
            # get the humidity
            data = bytearray(self.readI2C.read(3))
            self.humidity = -6.0 + 125.0 * float((data[0] << 8) | data[1]) / 65536.0
	        
            # now got valid data and start again
            self.dataValid = True
            self.state = HTU21D_STATE_IDLE


