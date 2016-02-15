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

import sys
import time
import json
import paho.mqtt.client as paho
import getopt
import base64
import subprocess

sys.path.append('../SensorDrivers')

import SensorJSON

sayString = ""
sayIt = False

'''
------------------------------------------------------------
    MQTT callbacks
'''

def onConnect(client, userdata, code):
    MQTTClient.subscribe(topic, 0)
    print('Connected: ' + str(code))
    sys.stdout.flush()

def onMessage(client, userdata, message):
    global sayString, sayIt
    
    try:
        jsonObj = json.loads(message.payload)
        text = jsonObj['text']
        sayString = jsonObj['say']
        print(text)
        if len(sayString) == 0:
            return
        sayIt = True
    except:
        print ("JSON error", sys.exc_info()[0],sys.exc_info()[1])

'''
------------------------------------------------------------
    Main code
'''

deviceID = 'rtdecodedspeech'
brokerAddress = 'localhost'
deviceSecret = 'rtdecodedspeech'
clientID = 'rtdecodedspeechmqttclient'
topic = 'rtsrserver/decodedspeech'

# process command line args

try:
    opts, args = getopt.getopt(sys.argv[1:], "b:c:d:s")
except:
    print ('RTDecodedSpeechMQTT.py -b <brokerAddr> -c <clientID> -d <deviceID> -s <secret -t <topic>')
    print ('\nDefaults:')
    print ('  -b localhost (hostname or IP address)')
    print ('  -c rtaudiomqttclient')
    print ('  -d rtdecodedspeech')
    print ('  -s rtdecodedspeech')
    print ('  -t rtsrserver/decodedspeech')
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
        topic = arg
        
ttsCompleteTopic = deviceID + '/ttscomplete'

MQTTClient = paho.Client(clientID, protocol=paho.MQTTv31)
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

print("RTDecodedSpeechMQTT starting...")
sys.stdout.flush()
        
try:
    while True:
        if sayIt:
            ttsComplete = {}
            ttsComplete[SensorJSON.TIMESTAMP] = time.time()
            ttsComplete[SensorJSON.DEVICEID] = deviceID
            ttsComplete[SensorJSON.TOPIC] = ttsCompleteTopic
            ttsComplete['complete'] = False
            MQTTClient.publish(ttsCompleteTopic, json.dumps(ttsComplete))   
            time.sleep(2) 	
            subprocess.call(['espeak', "aaa"])
            subprocess.call(['espeak', sayString.encode('utf-8')])
            time.sleep(2)
            ttsComplete['complete'] = True
            MQTTClient.publish(ttsCompleteTopic, json.dumps(ttsComplete))  
            sayIt = False;
        else:
            time.sleep(2)
except:
    pass

# Exiting so clean everything up.   
        
MQTTClient.loop_stop()
print("Exiting")
