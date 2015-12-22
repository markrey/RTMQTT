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

TSL2561_ADDRESS_ADDR_GND = 0x29       # ADDR SEL grounded address
TSL2561_ADDRESS_ADDR_FLOAT = 0x39     # ADDR SEL floating address
TSL2561_ADDRESS_ADDR_VCC = 0x49       # ADDR SEL VCC address

# Register definitions    

TSL2561_CONTROL = 0                   # basic control
TSL2561_TIMING = 1                    # integration timing
TSL2561_THRESHOLD_LOWLOW = 2          # low byte of low interrupt threshold
TSL2561_THRESHOLD_LOWHIGH = 3         # high byte of low threshold
TSL2561_THRESHOLD_HIGHLOW = 4         # low byte of high interrupt threshold
TSL2561_THRESHOLD_HIGHHIGH = 5        # high byte of high threshold
TSL2561_INTERRUPT = 6                 # interrupt control
TSL2561_ID = 0xa                      # id reg
TSL2561_DATA0LOW = 0xc                # low byte of ADC channel 0
TSL2561_DATA0HIGH = 0xd               # high byte of ADC channel 0
TSL2561_DATA1LOW = 0xe                # low byte of ADC channel 1
TSL2561_DATA1HIGH = 0xf               # high byte of ADC channel 1

# Command bits

TSL2561_COMMAND_CMD = 0x80            # must always be set
TSL2561_COMMAND_CLEAR = 0x40          # interrupt clear
TSL2561_COMMAND_WORD = 0x20           # word protocol
TSL2561_COMMAND_BLOCK = 0x10          # block protocol

# Control register bits

TSL2561_CONTROL_POWERDOWN = 0         # power down the device
TSL2561_CONTROL_POWERUP = 3           # power up the device

# Timing register bits

TSL2561_TIMING_GAIN16x = 0x10         # selects 16x gain
TSL2561_TIMING_MANUAL = 8             # begins an cycle in manual mode
TSL2561_TIMING_INTEG13D7 = 0          # 13.7mS integration time
TSL2561_TIMING_INTEG101 = 1           # 101mS integration time
TSL2561_TIMING_INTEG402 = 2           # 402mS integration time
TSL2561_TIMING_INTEGMAN = 3           # manual cycles

# Scale factors

TSL2561_SCALE_13D7 = (1.0 / 0.034)
TSL2561_SCALE_101 = (1.0 / 0.252)
TSL2561_SCALE_402 = (1.0)

# Interrupt control bits

TSL2561_INTERRUPT_LEVEL = 0x10        # level interrupt mode enable

class RT_TSL2561(RT_NullSensor):
    ''' richards-tech driver for the TSL2561 light sensor '''
    
    def __init__(self):
        RT_NullSensor.__init__(self)
        self.integrationTime = TSL2561_TIMING_INTEG101
        self.addr = TSL2561_ADDRESS_ADDR_FLOAT
        self.sensorValid = True
      
    def enable(self, busnum=-1, debug=False):
        # check if already enabled
        if (self.dataValid):
            return

        # check for the presence of the light sensor
        self.light = RT_I2C(self.addr, busnum, debug)
        if self.light.missing:
            self.sensorValid = False
            return
        # start the light sensor running
        command = TSL2561_COMMAND_CMD | TSL2561_CONTROL 
        param = TSL2561_CONTROL_POWERUP
        self.light.write8(command, param)
        command = TSL2561_COMMAND_CMD | TSL2561_TIMING 
        param = TSL2561_TIMING_GAIN16x | self.integrationTime
        self.light.write8(command, param)
        self.dataValid = True
       
    def setIntegrationTime(self, integrationTime):
        self.integrationTime = integrationTime

    # Read the sensor
    def readLight(self):
        ''' returns light level in Lux '''
        command = TSL2561_COMMAND_CMD | TSL2561_COMMAND_WORD | TSL2561_DATA0LOW
        adc0 = self.light.readList(command, 2)
        command = TSL2561_COMMAND_CMD | TSL2561_COMMAND_WORD | TSL2561_DATA1LOW
        adc1 = self.light.readList(command, 2)
   
        if ((adc0[0] == 0) and (adc0[1] == 0)):
            return 0                                     # avoids a crash at least
	
        ch0 = (adc0[0] | (adc0[1] << 8)) * TSL2561_SCALE_101
        ch1 = (adc1[0] | (adc1[1] << 8)) * TSL2561_SCALE_101
		
        ratio = ch1 / ch0
	
        if ((0 < ratio) and (ratio <= 0.5)):
            return 0.0304 * ch0 - 0.062 * ch0 * pow(ratio, 1.4)
        elif ((0.5 < ratio) and (ratio <= 0.61)):
            return 0.0224 * ch0 - 0.031 * ch1
        elif ((0.61 < ratio) and (ratio <= 0.8)):
            return 0.0128 * ch0 - 0.0153 * ch1
        elif ((0.8 < ratio) and (ratio <= 1.3)):
            return 0.00146 * ch0 - 0.00112 * ch1
        return 0


