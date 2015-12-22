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

# hardware defs

TMP102_ADDRESS_AD0_GND = 0x48                             # AD0 low
TMP102_ADDRESS_AD0_VCC = 0x49                             # AD0 high
TMP102_ADDRESS_AD0_SDA = 0x4a                             # AD0 connected to SDA
TMP102_ADDRESS_AD0_SCL = 0x4b                             # AD0 connected to SCL

# Register defs

TMP102_DATA = 0                                           # temperature data
TMP102_CONTROL = 1                                        # control bits
TMP102_DATA_TLOW = 2                                      # low limit register
TMP102_DATA_THIGH = 3                                     # high limit register

# Control low byte register bits

TMP102_CONTROL_LOW_EM = 0x10                              # enables extended mode
TMP102_CONTROL_LOW_AL = 0x20                              # alarm bit (read only)
TMP102_CONTROL_LOW_CRD25 = 0x00                           # 0.25Hz conversion rate
TMP102_CONTROL_LOW_CR1 = 0x40                             # 1Hz conversion rate
TMP102_CONTROL_LOW_CR4 = 0x80                             # 4Hz conversion rate
TMP102_CONTROL_LOW_CR8 = 0xc0                             # 8Hz conversion rate

# Control high byte register bits

TMP102_CONTROL_HIGH_SD = 0x1                              # enables shutdown mode
TMP102_CONTROL_HIGH_TM = 0x2                              # sets interrupt for thermometer mode
TMP102_CONTROL_HIGH_POL = 0x40                            # polarity mode
TMP102_CONTROL_HIGH_OS = 0x80                             # enables one shot mode

class RT_TMP102(RT_NullSensor):
    ''' richards-tech driver for the TMP102 temperature sensor '''
    
    def __init__(self):
        RT_NullSensor.__init__(self)
        self.addr = TMP102_ADDRESS_AD0_VCC
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

        self.tempRate = TMP102_CONTROL_LOW_CR8
        control = [0, 0]
        control[1] = self.tempRate | TMP102_CONTROL_LOW_EM
        control[0] = 0
        self.temp.writeList(TMP102_CONTROL, control)
        self.dataValid = True
        
    def setSampleRate(self, sampleRate):
        # set the sample rate
        self.tempRate = sampleRate

    def readTemperature(self):
        # read the sensor - returns temperature in degrees C
        val = self.temp.readList(TMP102_DATA, 2)       
        res = (val[0] << 5) | (val[1] >> 3)
        temperature = res * 0.0625
        return temperature
        
