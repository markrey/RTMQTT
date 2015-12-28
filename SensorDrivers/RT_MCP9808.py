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

# hardware defs - depends on setting sof a0, a1, a2

MCP9808_ADDRESS_000 = 0x18
MCP9808_ADDRESS_001 = 0x19
MCP9808_ADDRESS_010 = 0x1a
MCP9808_ADDRESS_011 = 0x1b
MCP9808_ADDRESS_100 = 0x1c
MCP9808_ADDRESS_101 = 0x1d
MCP9808_ADDRESS_110 = 0x1e
MCP9808_ADDRESS_111 = 0x1f

# Register defs

MCP9808_REG_CONFIG = 1                  # config register
MCP9808_REG_TEMP = 5                    # temp register (2 bytes)
MCP9808_REG_ID = 7                      # device ID

class RT_MCP9808(RT_NullSensor):
    ''' richards-tech driver for the MCP9808 temperature sensor '''
    
    def __init__(self):
        RT_NullSensor.__init__(self)
        self.addr = MCP9808_ADDRESS_000
        self.sensorValid = True
 
    def enable(self, busnum=-1, debug=False):
        # check if already enabled
        if (self.dataValid):
            return

        # enable the temp sensor
        self.temp = RT_I2C(self.addr, busnum, debug)
        if self.temp.missing:
            self.sensorValid = False
            return

        if self.temp.readU8(MCP9808_REG_ID) != 0x4:
            print("MCP9808 not found")
            self.sensorValid = False
            return

        self.dataValid = True

    def readTemperature(self):
        # read the sensor - returns temperature in degrees C
        val = self.temp.readList(MCP9808_REG_TEMP, 2) 
        
        # construct word result and clear flag bits      
        res = ((val[0] << 8) | val[1]) & 0x1fff
        
        if (res & 0x1000):
            # negative value
            res &= 0xfff
            temperature = float(4096 - res) / 16.0
        else:
            # positive value 
            temperature = float(res) / 16.0
        return temperature
        
