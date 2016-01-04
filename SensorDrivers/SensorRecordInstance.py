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

class SensorRecordInstance():
    ''' Sensor record for a single sensor type '''
        
    def __init__(self, recordLength, timeInterval): 
        # this var determines how big the record array is
        self.recordLength = recordLength
        
        # this var defines the time interval represented by each location in the array
        self.timeInterval = timeInterval
          
        # this var is used to accumulate data in the current time interval
        self.currentData = 0    
        # and this is how many samples have been accumulated
        self.currentDataCount = 0
     
        # this var is used to store averaged record per time interval
        self.data = []
    
        # this var indicates if data has been received
        self.dataValid = False
            
        # preset the store
        for i in range (0, self.recordLength):
            self.data.append(0.0)  
            
        # this is used to time the aggregation
        self.currentTime = 0 
                          
    def addData(self, newTimestamp, newData):
        if (self.currentDataCount == 0):
            # special case for first data point
            self.currentTime = newTimestamp
            self.dataValid = True
            self.currentData = newData      
            self.currentDataCount = 1
            return
            
        if ((newTimestamp - self.currentTime) >= self.timeInterval):
            # this record is for a new time interval
            timeUnits = int((newTimestamp - self.currentTime) /
                        self.timeInterval)                  # this is how many slots to fill based on gap
            self.currentTime += timeUnits                   # advance the clock
            
            for i in range(0, timeUnits):
                self.data.pop(0)
                self.data.append(self.currentData / self.currentDataCount)
 
            # zero out accumulator for next set
            self.currentData = 0
            self.currentDataCount = 0
        
        # add in new data   
        self.currentData += newData 
        self.currentDataCount += 1
    
    def getData(self):
        # accumulated data access function
        return self.data
        
    def getCurrentData(self):
        # current data access function
        if (self.currentDataCount == 0):
            return 0
        else:
            return self.currentData / self.currentDataCount
   
    def getDataValid(self):
        # data valid function
        return self.dataValid
 
        
        
        
        
