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

class RT_NullSensor():
    ''' richards-tech base class for physical sensors '''
    
    def __init__(self):
        # the dataValid flag indicates if data is valid
        self.dataValid = False;
        # the sensorValid flag indicates if sensor is valid (null sensor is not)
        self.sensorValid = False;

    @property
    def dataValid(self):
        return self.dataValid

    @property
    def sensorValid(self):
        return self.sensorValid
        
    # the following functions can be overriden by real sensors if they support the function
    
    def setI2CAddress(self, addr):
        # this function sets the I2C address. Call before enable.
        self.addr = addr
    
    def enable(self, busnum=-1, debug=False):
        # this function is called to start data collection in a real sensor
        pass
    
    def background(self):
        # in case a sensor needs a background loop
        pass
        
    def readAccel(self):
        # dummy accel data
        return [0, 0, 0]
        
    def readLight(self):
        # dummy light data
        return 0
        
    def readTemperature(self):
        # dummy temperature data
        return 0
        
    def readPressure(self):
        # dummy pressure data
        return 0
        
    def readHumidity(self):
        # dummy humidity data
        return 0
            
        
        
        
