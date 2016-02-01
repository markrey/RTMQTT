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
import base64
import picamera

sys.path.append('../SensorDrivers')

import SensorJSON

# camera parameters - change as required

CAMERA_INDEX = 0

'''
------------------------------------------------------------
    MQTT callbacks
'''

def onConnect(client, userdata, code):
    print('Connected: ' + str(code))
    sys.stdout.flush()


'''
------------------------------------------------------------
    pi camera functions and main loop
'''

# this is used to track when we have a new frame
piCameraLastFrameIndex = -1

mustExit = False;

def piCameraSendFrameHelper(stream, frame):
    ''' do the actual frame processing '''
    global piCameraLastFrameIndex
    
    # record index of new frame
    piCameraLastFrameIndex = frame.index

    # get the frame data and display it
    stream.seek(frame.position)
    image = stream.read(frame.frame_size)
    binImage = base64.b64encode(image)

    sensorDict = {}
    sensorDict[SensorJSON.TIMESTAMP] = time.time()
    sensorDict[SensorJSON.DEVICEID] = deviceID
    sensorDict[SensorJSON.TOPIC] = videoTopic
    sensorDict[SensorJSON.VIDEO_DATA] = binImage
    sensorDict[SensorJSON.VIDEO_WIDTH] = cameraWidth
    sensorDict[SensorJSON.VIDEO_HEIGHT] = cameraHeight
    sensorDict[SensorJSON.VIDEO_RATE] = cameraRate
    sensorDict[SensorJSON.VIDEO_FORMAT] = 'mjpeg'

    MQTTClient.publish(videoTopic, json.dumps(sensorDict))


def piCameraSendFrame(stream):
    ''' sendFrame checks the circular buffer to see if there is a new frame
    and publish it '''

    global piCameraLastFrameIndex

    with stream.lock:
        if (cameraRate > 10):
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
    ''' This is the main loop. '''

    global mustExit

    # Activate the video stream

    with picamera.PiCamera(CAMERA_INDEX) as camera:
        camera.resolution = (cameraWidth, cameraHeight)
        camera.framerate = (cameraRate, 1)

        # need enough buffering to overcome any latency
        stream = picamera.PiCameraCircularIO(camera, seconds = 1)

        # start recoding in mjpeg mode
        camera.start_recording(stream, format = 'mjpeg')

        try:
            while(True):
                # process any new frames
                camera.wait_recording(0)
                piCameraSendFrame(stream)
                
                #give other things a chance
                time.sleep(0.01)
  
        finally:
            camera.stop_recording()
            mustExit = True

'''
------------------------------------------------------------
    Main code
'''

deviceID = 'rtpicam'
brokerAddress = 'localhost'
deviceSecret = 'rtpicam'
clientID = 'rtpicamclient'
cameraWidth = 1280
cameraHeight = 720
cameraRate = 30

# process command line args

try:
    opts, args = getopt.getopt(sys.argv[1:], "b:c:d:h:r:s:w:")
except:
    print ('RTPiCamMQTT.py -b <brokerAddr> -c <clientID> -d <deviceID> -h <frame_height>')
    print ('      -r <frame_rate> -s <secret> -w <frame_width>')
    print ('\nDefaults:')
    print ('  -b localhost (hostname or IP address)')
    print ('  -c rtsensorClient')
    print ('  -d rtsensor')
    print ('  -h 720')
    print ('  -r 30')
    print ('  -s rtsensor')
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
    if opt == '-r':
        cameraRate = int(arg)
    if opt == '-s':
        deviceSecret = arg
    if opt == '-w':
        cameraWidth = int(arg)

print("RTPiCamMQTT starting...")
sys.stdout.flush()

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
    piCameraLoop()
except:
    if not mustExit:
        print ('No Pi camera found')

# Exiting so clean everything up.

MQTTClient.loop_stop()

print("Exiting")
