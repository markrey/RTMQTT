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

#include "ControllerClient.h"
#include "RTControllerMQTT.h"
#include "RTMQTTDevice.h"
#include "RTMQTTLog.h"

#define TAG "ControllerClient"

ControllerClient::ControllerClient() : RTMQTTClient(0)
{

}
void ControllerClient::clientInit()
{
    QSettings settings;

    int count = settings.beginReadArray(RTCONTROLLER_PARAMS_SERVERS);

    for (int i = 0; i < count; i++) {
        settings.setArrayIndex(i);
        QString serverID = settings.value(RTCONTROLLER_PARAMS_SERVERID).toString();
        addSubTopic(serverID + "/" + RTCONTROLLER_SERVER_STATUS_TOPIC);
      }
    settings.endArray();
}

void ControllerClient::clientStop()
{
}

void ControllerClient::clientTimer(QTimerEvent *)
{

}

void ControllerClient::clientProcessReceivedMessage(QString topic, QJsonObject json)
{
    emit newUpdate(topic, json);
}

void ControllerClient::setDeviceLevel(QString topic, QJsonObject newDeviceLevel)
{
    publish(topic, newDeviceLevel);
}
