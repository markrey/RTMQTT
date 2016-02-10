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

# variables used in JSON sensor records

DEVICEID = 'deviceID'                   # id of device
TOPIC = 'topic'                         # original message topic
TIMESTAMP = 'timestamp'                 # seconds since epoch
ACCEL_DATA = 'accel'                    # accelerometer x, y, z data in gs
LIGHT_DATA = 'light'                    # light data in lux
TEMPERATURE_DATA = 'temperature'        # temperature data in degrees C
PRESSURE_DATA = 'pressure'              # pressure in Pa
HUMIDITY_DATA = 'humidity'              # humidity in %RH

# variables used in JSON video records

VIDEO_DATA = 'video'                    # video data in hex
VIDEO_WIDTH = 'vwidth'                  # video frame width
VIDEO_HEIGHT = 'vheight'                # video frame height
VIDEO_RATE = 'vrate'                    # video frame rate
VIDEO_FORMAT = 'vformat'                # video frame format (eg mjpeg)

# variables used in JSON audio records

AUDIO_DATA = 'audio'                    # audio data in hex
AUDIO_RATE = 'arate'                    # audio sample rate
AUDIO_CHANNELS = 'achannels'            # number of audio channels
AUDIO_SAMPTYPE = 'asamptype'            # sample type (eg int16)
AUDIO_FORMAT = 'aformat'

# variables using in JSON decode speech records

DECODEDSPEECH_TEXT = 'text'             # the decoded speech as text
DECODEDSPEECH_SAY = 'say'               # what should be said
