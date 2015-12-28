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

# standard imports

import sys
import getopt
import time
import json
import paho.mqtt.client as paho
import binascii

# import the sensor drivers

sys.path.append('../SensorDrivers')

import RT_ADXL345
import RT_TSL2561
import RT_TMP102
import RT_BMP180
import RT_MCP9808
import RT_HTU21D
import RT_NullSensor
import SensorJSON

# The set of sensors. Uncomment one in each class or use NullSensor if no physical sensor
# Multi sensor objects (such as BMP180 for temp and pressure) can be reused

# Acceleration

#accel = RT_NullSensor.RT_NullSensor()
accel = RT_ADXL345.RT_ADXL345()

# Light

#light = RT_NullSensor.RT_NullSensor()
light = RT_TSL2561.RT_TSL2561()

# Temperature

#temperature = RT_NullSensor.RT_NullSensor()
#temperature = RT_TMP102.RT_TMP102()
#temperature = RT_MCP9808.RT_MCP9808()
temperature = RT_BMP180.RT_BMP180()

# Pressure

#pressure = RT_NullSensor.RT_NullSensor()
pressure = RT_BMP180.RT_BMP180()

# Humidity

#humidity = RT_NullSensor.RT_NullSensor()
humidity = RT_HTU21D.RT_HTU21D()

'''
------------------------------------------------------------
    MQTT callbacks
'''

def onConnect(client, userdata, code):
    print('Connected: ' + str(code))
    sys.stdout.flush()

'''
------------------------------------------------------------
    Sensor functions
'''

# global to maintain last sensor read time
lastSensorReadTime = time.time() 


def initSensors():
    accel.enable()
    light.enable()
    temperature.enable()
    pressure.enable()
    humidity.enable()

def readSensors():
    global lastSensorReadTime

    if ((time.time() - lastSensorReadTime) < sampleInterval):
        return
    # call background loops
    if accel.sensorValid:
        accel.background()
    if light.sensorValid:
        light.background()
    if temperature.sensorValid:
        temperature.background()
    if pressure.sensorValid:
        pressure.background()
    if humidity.sensorValid:
        humidity.background()

    # time send send the sensor readings
    lastSensorReadTime = time.time()
    
    sensorDict = {}
    
    sensorDict[SensorJSON.TIMESTAMP] = time.time()
    sensorDict[SensorJSON.DEVICEID] = deviceID
    sensorDict[SensorJSON.TOPIC] = sensorTopic

    if accel.dataValid:
        accelData = accel.readAccel()
        sensorDict[SensorJSON.ACCEL_DATA] = accelData
        
    if light.dataValid:
        lightData = light.readLight()
        sensorDict[SensorJSON.LIGHT_DATA] = lightData

    if temperature.dataValid:
        temperatureData = temperature.readTemperature()
        sensorDict[SensorJSON.TEMPERATURE_DATA] = temperatureData

    if pressure.dataValid:
        pressureData = pressure.readPressure()
        sensorDict[SensorJSON.PRESSURE_DATA] = pressureData
        
    if humidity.dataValid:
        humidityData = humidity.readHumidity()
        sensorDict[SensorJSON.HUMIDITY_DATA] = humidityData

    MQTTClient.publish(sensorTopic, json.dumps(sensorDict))


'''
------------------------------------------------------------
    Main sensor loop loop
'''


def sensorLoop():
    ''' This is the main sensor loop. '''

    while True:
        # see if anything from the sensors
        readSensors()

        # give other things a chance
        time.sleep(0.01)

'''
------------------------------------------------------------
    Main code
'''

deviceID = 'rtsensor'
brokerAddress = 'localhost'
deviceSecret = 'rtsensor'
clientID = 'rtsensorclient'
sampleInterval = 0.1

# process command line args

try:
    opts, args = getopt.getopt(sys.argv[1:], "b:c:d:i:s:")
except:
    print ('RTSensorMQTT.py -b <brokerAddr> -c <clientID> -d <deviceID> -i <interval> -s <secret>')
    print ('\nDefaults:')
    print ('  -b localhost (hostname or IP address)')
    print ('  -c rtsensorClient')
    print ('  -d rtsensor')
    print ('  -i 0.1 (0.1 seconds between samples)')
    print ('  -s rtsensor')
    sys.exit(2)

for opt, arg in opts:
    if opt == '-b':
        brokerAddress = arg
    if opt == '-c':
        clientID = arg
    if opt == '-d':
        deviceID = arg
    if opt == '-i':
        sampleInterval = float(arg)
    if opt == '-s':
        deviceSecret = arg

print("RTSensorMQTT starting...")
sys.stdout.flush()

initSensors()

sensorTopic = deviceID + '/sensors'

MQTTClient = paho.Client(clientID, protocol=paho.MQTTv31)
MQTTClient.on_connect = onConnect

MQTTClient.username_pw_set(deviceID, deviceSecret)

# try to connect

while True:
    try:
        MQTTClient.connect(brokerAddress)
        break
    except:
        print ("waiting to connect to broker",brokerAddress)
        time.sleep(1)

MQTTClient.loop_start()

try:
    sensorLoop()
except:
    pass

# Exiting so clean everything up.

MQTTClient.loop_stop()

print("Exiting")
