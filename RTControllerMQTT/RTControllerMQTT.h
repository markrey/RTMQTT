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

#ifndef _RTCONTROLLERMQTT_H
#define _RTCONTROLLERMQTT_H

#include <QtGui>
#include <qgridlayout.h>
#include <qmainwindow.h>
#include <qstatusbar.h>
#include <qprogressbar.h>
#include <qjsonobject.h>
#include <qtoolbar.h>
#include <qlabel.h>

#include "ControllerClient.h"
#include "RTMQTTDevice.h"

//  Server settings keys

#define RTCONTROLLER_PARAMS_SERVERS         "servers"
#define RTCONTROLLER_PARAMS_SERVERID        "serverID"

#define RTCONTROLLER_SERVER_STATUS_TOPIC    "status"
#define RTCONTROLLER_SERVER_CONTROL_TOPIC   "control"

class MainTable;


class RTControllerMQTT : public QMainWindow
{
    Q_OBJECT

public:
    RTControllerMQTT();

public slots:
    void onExit();
    void onConfigure();
    void onConfigureServers();
    void clientConnected();
    void clientDisconnected();
    void newUpdate(QString, QJsonObject update);
    void cellClicked(int row, int col);
    void tapAndHold();

signals:
    void setDeviceLevel(QString, QJsonObject);
    void newSize(QSize);
    void clientRestart();

protected:
    void closeEvent(QCloseEvent *event);
    void resizeEvent(QResizeEvent *);

private:
    void layoutWindow();
    void initStatusBar();
    void saveWindowState();
    void restoreWindowState();

    ControllerClient *m_client;

    QLabel *m_brokerStatus;
    QAction *m_configure;
    QAction *m_configureServers;

    MainTable *m_table;
    QStatusBar *m_statusBar;
    QToolBar *m_toolBar;

    QMap<int, RTMQTTDevice> m_deviceMap;                    // map from deviceID to device object
    QMap<int, int>m_gridMap;                                // map from deviceID to display row

    bool m_tapSeen;

    bool m_connected;
};

#endif // _RTCONTROLLERMQTT_H
