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

# Based on an original from Adafruit:

# Copyright 2013 Adafruit Industries

# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

from RT_I2C import RT_I2C
from RT_NullSensor import RT_NullSensor

ADXL345_ADDRESS_ALT_GND  = 0x53
ADXL345_ADDRESS_ALT_VCC  = 0x1d

ADXL345_REG_DEVID        = 0x00 # Device ID
ADXL345_REG_BW_RATE      = 0x2c # bandwidth and rate
ADXL345_REG_DATA_FORMAT  = 0x31 # data format
ADXL345_REG_DATAX0       = 0x32 # X-axis data 0 (6 bytes for X/Y/Z)
ADXL345_REG_POWER_CTL    = 0x2D # Power-saving features control

ADXL345_DATARATE_0_10_HZ = 0x00
ADXL345_DATARATE_0_20_HZ = 0x01
ADXL345_DATARATE_0_39_HZ = 0x02
ADXL345_DATARATE_0_78_HZ = 0x03
ADXL345_DATARATE_1_56_HZ = 0x04
ADXL345_DATARATE_3_13_HZ = 0x05
ADXL345_DATARATE_6_25HZ  = 0x06
ADXL345_DATARATE_12_5_HZ = 0x07
ADXL345_DATARATE_25_HZ   = 0x08
ADXL345_DATARATE_50_HZ   = 0x09
ADXL345_DATARATE_100_HZ  = 0x0A # (default)
ADXL345_DATARATE_200_HZ  = 0x0B
ADXL345_DATARATE_400_HZ  = 0x0C
ADXL345_DATARATE_800_HZ  = 0x0D
ADXL345_DATARATE_1600_HZ = 0x0E
ADXL345_DATARATE_3200_HZ = 0x0F

ADXL345_RANGE_2_G        = 0x00 # +/-  2g (default)
ADXL345_RANGE_4_G        = 0x01 # +/-  4g
ADXL345_RANGE_8_G        = 0x02 # +/-  8g
ADXL345_RANGE_16_G       = 0x03 # +/- 16g

class RT_ADXL345(RT_NullSensor):

    def __init__(self):
        RT_NullSensor.__init__(self)
        # set default address
        self.addr = ADXL345_ADDRESS_ALT_GND
        self.sensorValid = True
            
    def enable(self, busnum=-1, debug=False):
        # check if already enabled
        if (self.dataValid):
            return
        # check for the presence of the accel
        self.accel = RT_I2C(self.addr, busnum, debug)

        if self.accel.missing:
            self.sensorValid = False
            return

        if self.accel.readU8(ADXL345_REG_DEVID) != 0xE5:
            print("ADXL345 not found")
            self.sensorValid = False
            return

        self.accel.write8(ADXL345_REG_POWER_CTL, 0x08)
        self.dataValid = True

    def setRange(self, range):
        # Read the data format register to preserve bits.  Update the data
        # rate, make sure that the FULL-RES bit is enabled for range scaling
        format = ((self.accel.readU8(ADXL345_REG_DATA_FORMAT) & ~0x0F) |
          range | 0x08)
        # Write the register back to the IC
        self.accel.write8(ADXL345_REG_DATA_FORMAT, format)


    def getRange(self):
        return self.accel.readU8(ADXL345_REG_DATA_FORMAT) & 0x03


    def setDataRate(self, dataRate):
        # Note: The LOW_POWER bits are currently ignored,
        # we always keep the device in 'normal' mode
        self.accel.write8(ADXL345_REG_BW_RATE, dataRate & 0x0F)


    def getDataRate(self):
        return self.accel.readU8(ADXL345_REG_BW_RATE) & 0x0F


    # Read the accelerometer
    def readAccel(self):
        raw = self.accel.readList(ADXL345_REG_DATAX0, 6)
        res = []
        for i in range(0, 6, 2):
            g = raw[i] | (raw[i+1] << 8)
            if g > 32767: g -= 65536
            res.append(g / 250.0)
        return res

