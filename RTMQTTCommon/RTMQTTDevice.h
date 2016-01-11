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

#ifndef _RTMQTTDEVICE_H
#define _RTMQTTDEVICE_H

#include <qstring.h>
#include <qdatetime.h>
#include <qstringlist.h>
#include <qjsonobject.h>

//  JSON message defs

#define RTMQTTDEVICE_JSON_UPDATELIST      "updateList"
#define RTMQTTDEVICE_JSON_DELTA           "delta"
#define RTMQTTDEVICE_JSON_ALERT           "alert"
#define RTMQTTDEVICE_JSON_SETDEVICELEVEL  "setDeviceLevel"

//  JSON field defs

#define RTMQTTDEVICE_JSON_NAME            "name"
#define RTMQTTDEVICE_JSON_DEVICEID        "deviceID"
#define RTMQTTDEVICE_JSON_STATE           "state"
#define RTMQTTDEVICE_JSON_CURRENTLEVEL    "currentLevel"
#define RTMQTTDEVICE_JSON_NEWLEVEL        "newLevel"

class RTMQTTDevice
{
public:
    RTMQTTDevice();
    RTMQTTDevice(const RTMQTTDevice &rhs);

    bool read(const QString& topic, const QJsonObject& json);
    void write(QJsonObject& json) const;

    bool readNewLevel(const QJsonObject& json);
    void writeNewLevel(QJsonObject& json) const;

    QString controlTopic;
    QString name;
    int deviceID;
    QString state;

    int currentLevel;
    int newLevel;
};

#endif // _RTMQTTDEVICE_H
