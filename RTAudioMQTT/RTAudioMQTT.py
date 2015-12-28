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

import pyaudio
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
    pyaudio callbacks
'''
def callback(samples, frame_count, time_info, status):

    binSamples = binascii.hexlify(str(samples))

    sensorDict = {}
    sensorDict[SensorJSON.TIMESTAMP] = time.time()
    sensorDict[SensorJSON.DEVICEID] = deviceID
    sensorDict[SensorJSON.TOPIC] = audioTopic
    sensorDict[SensorJSON.AUDIO_DATA] = binSamples
    sensorDict[SensorJSON.AUDIO_CHANNELS] = audioChannels
    sensorDict[SensorJSON.AUDIO_RATE] = audioRate
    sensorDict[SensorJSON.AUDIO_SAMPTYPE] = 'int16'
    sensorDict[SensorJSON.AUDIO_FORMAT] = 'pcm'

    MQTTClient.publish(audioTopic, json.dumps(sensorDict))        
    return (None, pyaudio.paContinue)


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

deviceID = 'rtaudio'
brokerAddress = 'localhost'
deviceSecret = 'rtaudiomqtt'
clientID = 'rtaudiomqttclient'
audioIndex = 0
audioRate = 8000
audioChannels = 2

# process command line args

try:
    opts, args = getopt.getopt(sys.argv[1:], "b:c:d:h:r:s:y")
except:
    print ('RTAudioMQTT.py -b <brokerAddr> -c <clientID> -d <deviceID> -h <channels>')
    print ('  -r <rate> -s <secret> -y')
    print ('  -y = daemon mode')
    print ('\nDefaults:')
    print ('  -b localhost (hostname or IP address)')
    print ('  -c pisensorClient')
    print ('  -d pisensor')
    print ('  -h 2')
    print ('  -r 8000')
    print ('  -s pisensor')
    sys.exit(2)

for opt, arg in opts:
    if opt == '-a':
        audioCard = int(arg)
    if opt == '-b':
        brokerAddress = arg
    if opt == '-c':
        clientID = arg
    if opt == '-d':
        deviceID = arg
    if opt == '-h':
        audioChannels = int(arg)
    if opt == '-j':
        audioDevice = int(arg)
    if opt == '-r':
        audioRate = int(arg)
    if opt == '-s':
        deviceSecret = arg
        
        
# start up the audio device

audioDevice = pyaudio.PyAudio()
audioBlockSize = audioRate / 20
audioStream = audioDevice.open(stream_callback = callback, format=pyaudio.paInt16, channels = audioChannels, 
                        rate=audioRate, input=True, output=False, frames_per_buffer=audioBlockSize)

audioTopic = deviceID + '/audio'

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

print("RTAudioMQTT starting...")
sys.stdout.flush()

audioStream.start_stream()
        
while audioStream.is_active():
    time.sleep(0.1) 

# Exiting so clean everything up.   
        
audioStream.stop_stream()
audioStream.close()
audioDevice.terminate()
MQTTClient.loop_stop()
print("Exiting")
