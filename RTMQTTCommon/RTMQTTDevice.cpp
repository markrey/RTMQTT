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

#include "RTMQTTDevice.h"
#include <qjsonvalue.h>

RTMQTTDevice::RTMQTTDevice()
{
    deviceID = 0;
    currentLevel = 0;
    newLevel = 0;
}

RTMQTTDevice::RTMQTTDevice(const RTMQTTDevice &rhs)
{
    controlTopic = rhs.controlTopic;
    name = rhs.name;
    state = rhs.state;
    deviceID = rhs.deviceID;
    currentLevel = rhs.currentLevel;
    newLevel = rhs.newLevel;
}

bool RTMQTTDevice::read(const QString& topic, const QJsonObject& json)
{
    controlTopic = topic;

    if (!json.contains(RTMQTTDEVICE_JSON_NAME))
        return false;
    name = json[RTMQTTDEVICE_JSON_NAME].toString();

    if (!json.contains(RTMQTTDEVICE_JSON_DEVICEID))
        return false;
    deviceID = json[RTMQTTDEVICE_JSON_DEVICEID].toDouble();

    if (json.contains(RTMQTTDEVICE_JSON_CURRENTLEVEL))
        currentLevel = json[RTMQTTDEVICE_JSON_CURRENTLEVEL].toDouble();

    if (json.contains(RTMQTTDEVICE_JSON_STATE))
        state = json[RTMQTTDEVICE_JSON_STATE].toString();

    return true;
}


void RTMQTTDevice::write(QJsonObject& json) const
{
    json[RTMQTTDEVICE_JSON_NAME] = name;
    json[RTMQTTDEVICE_JSON_DEVICEID] = (int)deviceID;
    json[RTMQTTDEVICE_JSON_CURRENTLEVEL] = currentLevel;
    json[RTMQTTDEVICE_JSON_STATE] = state;
}

bool RTMQTTDevice::readNewLevel(const QJsonObject& json)
{
    if (!json.contains(RTMQTTDEVICE_JSON_DEVICEID))
        return false;
    deviceID = json[RTMQTTDEVICE_JSON_DEVICEID].toDouble();

    if (json.contains(RTMQTTDEVICE_JSON_NEWLEVEL))
        newLevel = json[RTMQTTDEVICE_JSON_NEWLEVEL].toDouble();

    return true;
}

void RTMQTTDevice::writeNewLevel(QJsonObject& json) const
{
    json[RTMQTTDEVICE_JSON_DEVICEID] = (int)deviceID;
    json[RTMQTTDEVICE_JSON_NEWLEVEL] = newLevel;
}
