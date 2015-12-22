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

# check if picamera is available

cameraPresent = True

try:
    import picamera
except:
    cameraPresent = False

# camera parameters - change as required

CAMERA_INDEX = 0
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
CAMERA_RATE = 10

# import the sensor drivers

sys.path.append('SensorDrivers')

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
    pi camera functions and main loop
'''

# this is used to track when we have a new frame
piCameraLastFrameIndex = -1

def piCameraSendFrameHelper(stream, frame):
    ''' do the actual frame processing '''
    global piCameraLastFrameIndex
    
    # record index of new frame
    piCameraLastFrameIndex = frame.index

    # get the frame data and display it
    stream.seek(frame.position)
    image = stream.read(frame.frame_size)
    binImage = binascii.hexlify(image)
    MQTTClient.publish(videoTopic, binImage)


def piCameraSendFrame(stream):
    ''' sendFrame checks the circular buffer to see if there is a new frame
    and publish it '''

    global piCameraLastFrameIndex

    with stream.lock:
        if (CAMERA_RATE > 10):
            for frame in stream.frames:
                if (frame.index > piCameraLastFrameIndex):
                    piCameraSendFrameHelper(stream, frame)
        else:
            # skip to last frame in iteration
            frame = None
            for frame in stream.frames:
                pass
 
            if (frame is None):
                return
         
            # check to see if this is new
            if (frame.index == piCameraLastFrameIndex):
                return
            piCameraSendFrameHelper(stream, frame)
        
 
def piCameraLoop():
    ''' This is the main loop when the pi camera is enabled. '''
    # Activate the video stream

    with picamera.PiCamera(CAMERA_INDEX) as camera:
        camera.resolution = (CAMERA_WIDTH, CAMERA_HEIGHT)
        camera.framerate = (CAMERA_RATE, 1)

        # need enough buffering to overcome any latency
        stream = picamera.PiCameraCircularIO(camera, seconds = 1)

        # start recoding in mjpeg mode
        camera.start_recording(stream, format = 'mjpeg')

        try:
            while(True):
                # process any new frames
                camera.wait_recording(0)
                piCameraSendFrame(stream)
                
                # see if anythng new from the sensors
                readSensors()

                #give other things a chance
                time.sleep(0.01)
  
        finally:
            camera.stop_recording()

'''
------------------------------------------------------------
    No camera main loop
'''


def noCameraLoop():
    ''' This is the main loop when no camera is running. '''

    while True:
        # see if anything from the sensors
        readSensors()

        # give other things a chance
        time.sleep(0.01)

'''
------------------------------------------------------------
    Main code
'''

deviceID = 'pisensor'
brokerAddress = 'localhost'
deviceSecret = 'pisensor'
clientID = 'pisensorclient'
sampleInterval = 0.1

# process command line args

try:
    opts, args = getopt.getopt(sys.argv[1:], "b:c:d:i:s:")
except:
    print ('PiSensorMQTT.py -b <brokerAddr> -c <clientID> -d <deviceID> -i <interval> -s <secret>')
    print ('Defaults:')
    print ('  -b localhost (hostname or IP address)')
    print ('  -c pisensorClient')
    print ('  -d pisensor')
    print ('  -i 0.1 (0.1 seconds between samples)')
    print ('  -s pisensor')
    sys.exit(2)

for opt, arg in opts:
    if opt == '-b':
        brokerAddress = arg
    if opt == '-c':
        clientID = arg
    if opt == '-d':
        deviceID = arg
    if opt == '-r':
        sampleInterval = float(arg)
    if opt == '-s':
        deviceSecret = arg

print("PiSensorMQTT starting...")
sys.stdout.flush()

initSensors()

sensorTopic = deviceID + '/sensors'
videoTopic = deviceID + '/video'

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
    if cameraPresent:
        try:
            piCameraLoop()
        except:
            print ('No Pi camera found - continuing without video')
            noCameraLoop()
    else:
        noCameraLoop()
except:
    pass

# Exiting so clean everything up.

MQTTClient.loop_stop()

print("Exiting")
