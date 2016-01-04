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

import numpy as np
import matplotlib.pyplot as plt

import SensorRecords

class SensorPlot():
    
    # this is used to provide the x axis data for the plots
    xAxis = np.arange(-SensorRecords.SENSOR_RECORD_LENGTH, 0, 1)
    
    # this list contains the active figures (one per sensor)
    figures = []
    
    # this list contains the axis data for each figure
    axes = []
    
    def __doPlot(self, figNumber, sensor):
        if (figNumber > len(self.figures)):
            return
        
        if (figNumber == len(self.figures)):
            # need to add a figure
            fig, axarr = plt.subplots(5, sharex = True)
            self.figures.append(fig)
            self.axes.append(axarr)
            fig.subplots_adjust(hspace = 0.5)
            fig.set_size_inches(8, 10, forward=True)
       
        # now ready to actually draw the charts
       
        plt.figure(figNumber + 1)
        axarr = self.axes[figNumber]
        
        self.figures[figNumber].canvas.set_window_title(sensor.getTopicName())
       
        # do accel plot
        axarr[0].clear()
        axarr[0].set_ylim(-2, 2)        
        if (sensor.getAccelValid()):
 
            axarr[0].plot(self.xAxis, sensor.getAccelDataX(), 'b-', 
                            label = 'Accel X (%.2fg)' % sensor.getCurrentAccelDataX())
            axarr[0].plot(self.xAxis, sensor.getAccelDataY(), 'r-', 
                            label = 'Accel Y(%.2fg)' % sensor.getCurrentAccelDataY())
            axarr[0].plot(self.xAxis, sensor.getAccelDataZ(), 'g-', 
                            label = 'Accel Z(%.2fg)' % sensor.getCurrentAccelDataZ())
        else:
            axarr[0].plot(self.xAxis, sensor.getAccelDataX(), 'b-', 
                            label = 'No data')

        axarr[0].legend(loc='upper center', shadow=True, fontsize='x-small')
        axarr[0].set_title("Accelerometer data")

        #do light intensity plot
        axarr[1].clear()
        axarr[1].set_ylim(0, 1500)
        if (sensor.getLightValid()):
            axarr[1].plot(self.xAxis, sensor.getLightData(), 'b-', 
                           label = 'Light (%.2f lux)' % sensor.getCurrentLightData())
        else:
            axarr[1].plot(self.xAxis, sensor.getLightData(), 'b-', 
                           label = 'No data')
            
        axarr[1].legend(loc='upper center', shadow=True, fontsize='x-small')
        axarr[1].set_title("Light intensity data")
       
        #do temperature plot 
        axarr[2].clear()
        axarr[2].set_ylim(-50, 150)
        if (sensor.getTemperatureValid()):
            axarr[2].plot(self.xAxis, sensor.getTemperatureData(), 'b-', 
                           label = 'Temperature (%.2f deg C)' % sensor.getCurrentTemperatureData())
        else:
            axarr[2].plot(self.xAxis, sensor.getTemperatureData(), 'b-', 
                           label = 'No data')
                
        axarr[2].legend(loc='upper center', shadow=True, fontsize='x-small')
        axarr[2].set_title("Temperature data")
                 
        #do pressure plot 
        axarr[3].clear()
        axarr[3].set_ylim(800, 1200)
        if (sensor.getPressureValid()):
            axarr[3].plot(self.xAxis, sensor.getPressureData(), 'b-', 
                           label = 'Pressure (%.2f hPa)' % sensor.getCurrentPressureData())
        else:
            axarr[3].plot(self.xAxis, sensor.getPressureData(), 'b-', 
                           label = 'No data')
                
        axarr[3].legend(loc='upper center', shadow=True, fontsize='x-small')
        axarr[3].set_title("Pressure data")
                 
        #do humidity plot 
        axarr[4].clear()
        axarr[4].set_ylim(0, 100)
        if (sensor.getHumidityValid()):
            axarr[4].plot(self.xAxis, sensor.getHumidityData(), 'b-', 
                           label = 'Humidity (%.2f %%RH)' % sensor.getCurrentHumidityData())
        else:
            axarr[4].plot(self.xAxis, sensor.getHumidityData(), 'b-', 
                           label = 'No data')
                
        axarr[4].legend(loc='upper center', shadow=True, fontsize='x-small')
        axarr[4].set_title("Humidity data")
                          
    def __init__(self):
        ''' Sets up the sensor plot '''
        plt.ion()
       
    def plot(self, sensors):
        ''' Plots the data in the list of sensors '''
        
        figNumber = 0
        for sensor in sensors:
            self.__doPlot(figNumber, sensor)
            figNumber += 1
            
        if (len(self.figures) > 0):    
            plt.draw()
                       
        # check if anything has gone missing
        while (len(self.figures) > figNumber):
            plt.close(len(self.figures))
            self.figures.pop()
            self.axes.pop()
            
            
        
 
      
        
        
    
