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

# Now do the imports

import sys

# add the sensor driver directory
sys.path.append('../SensorDrivers')

import paho.mqtt.client as paho
import binascii
import getopt
import time
import json

import SensorJSON
import SensorPlot
import SensorRecords


# The topic map contains the mapping between topic and sensor object

topicMap = {}


'''
------------------------------------------------------------
    MQTT callbacks
'''

def onConnect(client, userdata, code):
    MQTTClient.subscribe(sensorTopic, 0)
    print('Connected: ' + str(code))
    sys.stdout.flush()

def onSubscribe(client, data, mid, grantedQos):
    print('Subscribed: ' + str(mid))
    sys.stdout.flush()

def onMessage(client, userdata, message):
    global topicMap
    try:
        topicMap[sensorTopic].newJSONData(message.payload)

    except:
        print ("JSON error", sys.exc_info()[0],sys.exc_info()[1])



'''
------------------------------------------------------------
    Main code
'''

deviceID = 'rtsensorview'
deviceSecret = 'rtsensorview'
brokerAddress = 'localhost'
clientID = 'rtsensorviewclient'
sensorTopic = "rtsensor/sensors"
plotInterval = 1.0

# process command line args

try:
    opts, args = getopt.getopt(sys.argv[1:], "b:c:d:p:s:t:")
except:
    print ('RTSensorViewMQTT.py -b <brokerAddr> -c <clientID> -d <deviceID> -p <plotInterval>')
    print ('          -s <secret> -t <sensorTopic')
    print ('\nDefaults:')
    print ('  -b localhost (hostname or IP address)')
    print ('  -c rtsensorviewclient')
    print ('  -d rtsensorview')
    print ('  -p 1.0')
    print ('  -s rtsensorview')
    print ('  -t rtsensor/sensors')
    sys.exit(2)

for opt, arg in opts:
    if opt == '-b':
        brokerAddress = arg
    if opt == '-c':
        clientID = arg
    if opt == '-d':
        deviceID = arg
    if opt == '-p':
        plotInterval = float(arg)
    if opt == '-s':
        deviceSecret = arg
    if opt == '-t':
        sensorTopic = arg

print("RTSensorViewMQTT starting...")
sys.stdout.flush()

topicMap[sensorTopic] = SensorRecords.SensorRecords(sensorTopic, plotInterval)

# start up the plotter

sensorPlot = SensorPlot.SensorPlot()

# lastPlotTime is used to control plot updates
lastPlotTime = time.time() - plotInterval


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

MQTTClient.loop_start()

try:
    while True:
        if (time.time() - lastPlotTime) >= plotInterval:
            lastPlotTime = time.time()
            sensorPlot.plot(topicMap.values())
        time.sleep(0.05)
except:
    pass

# Exiting so clean everything up.

MQTTClient.loop_stop()
print("Exiting")

