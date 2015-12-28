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

# camera parameters - change as required

# Now onto the real stuff

import RTUVCCam
import sys
import time
import json
import paho.mqtt.client as paho
import binascii
import getopt

sys.path.append('../SensorDrivers')

import SensorJSON

'''
------------------------------------------------------------
    MQTT callbacks
'''

def onConnect(client, userdata, code):
    print('Connected: ' + str(code))
    sys.stdout.flush()

'''
------------------------------------------------------------
    Main code
'''

deviceID = 'rtuvccam'
brokerAddress = 'localhost'
deviceSecret = 'rtuvccammqtt'
clientID = 'rtuvccammqttclient'
cameraIndex = 0
cameraWidth = 1280
cameraHeight = 720
cameraRate = 30

# process command line args

try:
    opts, args = getopt.getopt(sys.argv[1:], "b:c:d:h:i:r:s:w:xy")
except:
    print ('RTUVCCamMQTT.py -b <brokerAddr> -c <clientID> -d <deviceID> -h <height> -r <rate> -s <secret>')
    print ('  -w <width> -x -y')
    print ('\n  -x = console mode')
    print ('  -y = daemon mode')
    print ('\nDefaults:')
    print ('  -b localhost (hostname or IP address)')
    print ('  -c pisensorClient')
    print ('  -d pisensor')
    print ('  -h 720')
    print ('  -i 0')
    print ('  -r 30')
    print ('  -s pisensor')
    print ('  -w 1280')
    sys.exit(2)

for opt, arg in opts:
    if opt == '-b':
        brokerAddress = arg
    if opt == '-c':
        clientID = arg
    if opt == '-d':
        deviceID = arg
    if opt == '-h':
        cameraHeight = int(arg)
    if opt == '-i':
        cameraindex = int(arg)
    if opt == '-r':
        cameraRate = int(arg)
    if opt == '-s':
        deviceSecret = arg
    if opt == '-w':
        cameraWidth = int(arg)

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

# start RTUVCCamLib running
RTUVCCam.start(sys.argv, True)

# this delay is necessary to allow Qt startup to complete
time.sleep(1)

# Open the camera device
if (not RTUVCCam.vidCapOpen(cameraIndex, cameraWidth, cameraHeight, cameraRate)):
    print("Failed to open vidcap")
    RTUVCCam.stop()
    sys.exit()

# set the title if in GUI mode
RTUVCCam.setWindowTitle("camera stream")

# wake up the console
print("RTUVCCamMQTT starting...")
sys.stdout.flush()

while(True):
    try:
        # give other things a chance
        time.sleep(0.02)
        # get a frame from the camera
        ret, frame, jpeg, width, height, rate = RTUVCCam.vidCapGetFrame(cameraIndex)
        if (ret):            
            # and display it
            if (jpeg):
                RTUVCCam.displayJpegImage(frame, "")
            else:
                RTUVCCam.displayImage(frame, width, height, "")
            
            binImage = binascii.hexlify(frame)

            sensorDict = {}
            sensorDict[SensorJSON.TIMESTAMP] = time.time()
            sensorDict[SensorJSON.DEVICEID] = deviceID
            sensorDict[SensorJSON.TOPIC] = videoTopic
            sensorDict[SensorJSON.VIDEO_DATA] = binImage
            sensorDict[SensorJSON.VIDEO_WIDTH] = width
            sensorDict[SensorJSON.VIDEO_HEIGHT] = height
            sensorDict[SensorJSON.VIDEO_RATE] = rate
            if jpeg:
                sensorDict[SensorJSON.VIDEO_FORMAT] = 'mjpeg'
            else:
                sensorDict[SensorJSON.VIDEO_FORMAT] = 'raw'

            MQTTClient.publish(videoTopic, json.dumps(sensorDict))        
        
    except:
        break
        
# Exiting so clean everything up.    

RTUVCCam.vidCapClose(cameraIndex)
RTUVCCam.stop()
MQTTClient.loop_stop()
print("Exiting")
