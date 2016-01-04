#!/usr/bin/python
"""
////////////////////////////////////////////////////////////////////////////
//
//  This file is part of RTMQTT
//
//  Copyright (c) 2015-2016, richards-tech, LLC
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
"""

import json
import SensorJSON
import SensorRecordInstance

# global defines

SENSOR_RECORD_LENGTH = 600                                  # number of time intervals

# the sensor record array indices

SENSOR_RECORD_ACCEL_X = 0
SENSOR_RECORD_ACCEL_Y = 1
SENSOR_RECORD_ACCEL_Z = 2
SENSOR_RECORD_LIGHT = 3
SENSOR_RECORD_TEMPERATURE = 4
SENSOR_RECORD_PRESSURE = 5
SENSOR_RECORD_HUMIDITY = 6

SENSOR_RECORD_COUNT = 7

class SensorRecords():
    ''' Sensor model used by viewers '''
        
    def __init__(self, topicName, accumInterval):       
        # the sensor instance vars
        self.sensorRecords = []
        for i in range (0, SENSOR_RECORD_COUNT):
            self.sensorRecords.append(SensorRecordInstance.SensorRecordInstance(SENSOR_RECORD_LENGTH,
                            accumInterval))
        self.topicName = topicName
        self.accumInterval = accumInterval
                              
    def newJSONData(self, data):
        ''' adds a sensor JSON record to the record '''
        # decode the JSON record
        sensorDict = json.loads(data)
        newTimestamp = sensorDict.get(SensorJSON.TIMESTAMP)
        newAccelData = sensorDict.get(SensorJSON.ACCEL_DATA)
        newLightData = sensorDict.get(SensorJSON.LIGHT_DATA)
        newTemperatureData = sensorDict.get(SensorJSON.TEMPERATURE_DATA)
        newPressureData = sensorDict.get(SensorJSON.PRESSURE_DATA)
        newHumidityData = sensorDict.get(SensorJSON.HUMIDITY_DATA)
        
        if (newTimestamp == None):
            print ("Received JSON record without timestamp")
            return
            
        # now update instances
        
        if (newAccelData != None):
            self.sensorRecords[SENSOR_RECORD_ACCEL_X].addData(newTimestamp, newAccelData[0])
            self.sensorRecords[SENSOR_RECORD_ACCEL_Y].addData(newTimestamp, newAccelData[1])
            self.sensorRecords[SENSOR_RECORD_ACCEL_Z].addData(newTimestamp, newAccelData[2])
            
        if (newLightData != None):
             self.sensorRecords[SENSOR_RECORD_LIGHT].addData(newTimestamp, newLightData)
             
        if (newTemperatureData != None):
             self.sensorRecords[SENSOR_RECORD_TEMPERATURE].addData(newTimestamp, newTemperatureData)
             
        if (newPressureData != None):
             self.sensorRecords[SENSOR_RECORD_PRESSURE].addData(newTimestamp, newPressureData)
             
        if (newHumidityData != None):
             self.sensorRecords[SENSOR_RECORD_HUMIDITY].addData(newTimestamp, newHumidityData)
   
    def getTopicName(self):
        return self.topicName
   
    # data validity functions
    
    def getAccelValid(self):
        return self.sensorRecords[SENSOR_RECORD_ACCEL_X].getDataValid()
        
    def getLightValid(self):
        return self.sensorRecords[SENSOR_RECORD_LIGHT].getDataValid()
    
    def getTemperatureValid(self):
        return self.sensorRecords[SENSOR_RECORD_TEMPERATURE].getDataValid()
    
    def getPressureValid(self):
        return self.sensorRecords[SENSOR_RECORD_PRESSURE].getDataValid()
    
    def getHumidityValid(self):
        return self.sensorRecords[SENSOR_RECORD_HUMIDITY].getDataValid()
        
    # accumulated data access function
    
    def getAccelDataX(self):
        return self.sensorRecords[SENSOR_RECORD_ACCEL_X].getData()
        
    def getAccelDataY(self):
        return self.sensorRecords[SENSOR_RECORD_ACCEL_Y].getData()
        
    def getAccelDataZ(self):
        return self.sensorRecords[SENSOR_RECORD_ACCEL_Z].getData()
        
    def getLightData(self):
        return self.sensorRecords[SENSOR_RECORD_LIGHT].getData()
    
    def getTemperatureData(self):
        return self.sensorRecords[SENSOR_RECORD_TEMPERATURE].getData()
    
    def getPressureData(self):
        return self.sensorRecords[SENSOR_RECORD_PRESSURE].getData()
    
    def getHumidityData(self):
        return self.sensorRecords[SENSOR_RECORD_HUMIDITY].getData()
        
    # current data access function
    
    def getCurrentAccelDataX(self):
        return self.sensorRecords[SENSOR_RECORD_ACCEL_X].getCurrentData()
        
    def getCurrentAccelDataY(self):
        return self.sensorRecords[SENSOR_RECORD_ACCEL_Y].getCurrentData()
        
    def getCurrentAccelDataZ(self):
        return self.sensorRecords[SENSOR_RECORD_ACCEL_Z].getCurrentData()
        
    def getCurrentLightData(self):
        return self.sensorRecords[SENSOR_RECORD_LIGHT].getCurrentData()
    
    def getCurrentTemperatureData(self):
        return self.sensorRecords[SENSOR_RECORD_TEMPERATURE].getCurrentData()
    
    def getCurrentPressureData(self):
        return self.sensorRecords[SENSOR_RECORD_PRESSURE].getCurrentData()
    
    def getCurrentHumidityData(self):
        return self.sensorRecords[SENSOR_RECORD_HUMIDITY].getCurrentData()
        
        
        
        
        
        
 
