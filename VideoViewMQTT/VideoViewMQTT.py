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

import pygame
import sys
import paho.mqtt.client as paho
import binascii
import cStringIO
import getopt
import time

'''
------------------------------------------------------------
    MQTT callbacks
'''

def onConnect(client, userdata, code):
    print('Connected: ' + str(code))
    sys.stdout.flush()

def onSubscribe(client, data, mid, grantedQos):
    print('Subscribed: ' + str(mid))
    sys.stdout.flush()

def onMessage(client, userdata, message):
    try:
        image = binascii.unhexlify(message.payload)
        imageFile = cStringIO.StringIO(image)
        imageSurface = pygame.image.load(imageFile)
        screen.blit(imageSurface, (0, 0))
        pygame.display.flip()
    except:
        print ("data error", sys.exc_info()[0],sys.exc_info()[1])

'''
------------------------------------------------------------
    Main code
'''

deviceID = 'videoview'
deviceSecret = 'videoview'
brokerAddress = 'localhost'
videoTopic = 'pisensor/video'
clientID = 'videoviewclient'

# process command line args

try:
    opts, args = getopt.getopt(sys.argv[1:], "b:c:d:s:t:")
except:
    print ('VideoViewMQTT.py -b <brokerAddr> -c <clientID> -d <deviceID> -s <secret> -t topic')
    print ('Defaults:')
    print ('  -b localhost (hostname or IP address)')
    print ('  -c videoviewclient')
    print ('  -d videoview')
    print ('  -s videoview')
    print ('  -t pisensor/video')
    sys.exit(2)

for opt, arg in opts:
    if opt == '-b':
        brokerAddress = arg
    if opt == '-c':
        clientID = arg
    if opt == '-d':
        deviceID = arg
    if opt == '-s':
        deviceSecret = arg
    if opt == '-t':
        videoTopic = arg

print("VideoViewMQTT starting...")
sys.stdout.flush()

MQTTClient = paho.Client(clientID, protocol=paho.MQTTv31)

MQTTClient.on_subscribe = onSubscribe
MQTTClient.on_connect = onConnect
MQTTClient.on_message = onMessage

MQTTClient.username_pw_set(deviceID, deviceSecret)

# try to connect

while True:
    try:
        MQTTClient.connect(brokerAddress)
        break
    except:
        print ("waiting to connect to broker",brokerAddress)
        time.sleep(1)

pygame.init()
w = 640
h = 480
size=(w,h)
screen = pygame.display.set_mode(size)

MQTTClient.subscribe(videoTopic, 0)

MQTTClient.loop_start()

try:
    while True:
        # could add some extra functionality here if required
        time.sleep(1)
        pass
except:
    pass

# Exiting so clean everything up.

MQTTClient.loop_stop()
print("Exiting")
