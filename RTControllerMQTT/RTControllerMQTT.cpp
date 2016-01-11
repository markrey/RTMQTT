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

#include "RTControllerMQTT.h"
#include "MainTable.h"
#include "SetDeviceLevelDlg.h"
#include "ConfigureDlg.h"
#include "ConfigureServerDlg.h"
#include "RTMQTTArgs.h"

#include <qheaderview.h>
#include <qboxlayout.h>
#include <qaction.h>
#include <QMessageBox>
#include <qdir.h>
#include <QStyleFactory>
#include <QApplication>

RTControllerMQTT::RTControllerMQTT()
    : QMainWindow()
{
    QApplication::setStyle(QStyleFactory::create("windows"));

    layoutWindow();
    restoreWindowState();
    initStatusBar();

    m_client = new ControllerClient();

    connect(m_client, SIGNAL(clientConnected()), this, SLOT(clientConnected()));
    connect(m_client, SIGNAL(clientDisconnected()), this, SLOT(clientDisconnected()));
    connect(this, SIGNAL(clientRestart()), m_client, SLOT(clientRestart()));
    connect(m_client, SIGNAL(newUpdate(QString, QJsonObject)), this, SLOT(newUpdate(QString, QJsonObject)));
    connect(this, SIGNAL(setDeviceLevel(QString, QJsonObject)), m_client, SLOT(setDeviceLevel(QString, QJsonObject)));
    connect(this, SIGNAL(newSize(QSize)), m_table, SLOT(newSize(QSize)));

    m_client->resumeThread();

    setWindowTitle("RTControllerMQTT");

    m_tapSeen = false;
    m_connected = false;
}

void RTControllerMQTT::closeEvent(QCloseEvent *)
{
    if (m_client) {
        m_client->exitThread();
        m_client->thread()->wait(2000);
        m_client = NULL;
    }

    saveWindowState();
}

void RTControllerMQTT::resizeEvent(QResizeEvent *)
{
    emit newSize(size());
}


void RTControllerMQTT::clientConnected()
{
    m_connected = true;
    QSettings settings;

    settings.beginGroup(RTMQTTCLIENT_PARAMS_GROUP);

    m_brokerStatus->setText("Connected to " + settings.value(RTMQTTCLIENT_PARAMS_BROKERADDRESS).toString());

    settings.endGroup();
}

void RTControllerMQTT::clientDisconnected()
{
    m_connected = false;
    m_brokerStatus->setText("Disconnected");
}

void RTControllerMQTT::newUpdate(QString topic, QJsonObject update)
{
    if (!m_connected)
        return;

    if (!update.contains(RTMQTTDEVICE_JSON_UPDATELIST))
        return;

    QJsonArray jsa = update[RTMQTTDEVICE_JSON_UPDATELIST].toArray();
    for (int i = 0; i < jsa.count(); i++) {
        QJsonObject params = jsa[i].toObject();

        RTMQTTDevice dev;

        //  convert status topic to control topic

        QStringList parts = topic.split("/");
        parts.removeLast();
        parts.append(RTCONTROLLER_SERVER_CONTROL_TOPIC);

        if (!dev.read(parts.join('/'), params))
            continue;

        if (!m_deviceMap.contains(dev.deviceID)) {
            int row = m_table->rowCount();
            m_table->insertRow(row);
            m_table->setRowHeight(row, MAINTABLE_ROW_HEIGHT);
            QLabel *label = new QLabel();
            label->setAttribute(Qt::WA_TransparentForMouseEvents, true);
            label->setIndent(20);
            m_table->setCellWidget(row, 0, label);

            QProgressBar *pb = new QProgressBar();
            pb->setMinimum(0);
            pb->setMaximum(255);
            pb->setAttribute(Qt::WA_TransparentForMouseEvents, true);
            m_table->setCellWidget(row, 1, pb);

            m_deviceMap.insert(dev.deviceID, dev);
            m_gridMap.insert(dev.deviceID, row);
        } else {
            m_deviceMap.insert(dev.deviceID, dev);
        }

        int gridSlot = m_gridMap.value(dev.deviceID);
        ((QLabel *)m_table->cellWidget(gridSlot, 0))->setText(dev.name);
        ((QProgressBar *)m_table->cellWidget(gridSlot, 1))->setValue(dev.currentLevel);
        m_table->update();
    }
}

void RTControllerMQTT::layoutWindow()
{
    QAction *action;

    QWidget *centralWidget = new QWidget(this);
    setCentralWidget(centralWidget);
    centralWidget->setContentsMargins(0, 0, 0, 0);

    m_toolBar = new QToolBar(this);
    addToolBar(Qt::TopToolBarArea, m_toolBar);
    m_toolBar->setObjectName("Toolbar");
    m_toolBar->setMinimumHeight(50);

    m_configure = new QAction("Configure MQTT broker", this);
    connect(m_configure, SIGNAL(triggered()), this, SLOT(onConfigure()));
    m_toolBar->addAction(m_configure);

    m_toolBar->addSeparator();

    m_configureServers = new QAction("Configure MQTT servers", this);
    connect(m_configureServers, SIGNAL(triggered()), this, SLOT(onConfigureServers()));
    m_toolBar->addAction(m_configureServers);

    m_toolBar->addSeparator();

    action = new QAction("Exit", this);
    connect(action, SIGNAL(triggered()), this, SLOT(onExit()));
    m_toolBar->addAction(action);

    QVBoxLayout *vl = new QVBoxLayout();
    centralWidget->setLayout(vl);

    m_table = new MainTable(this);
    m_table->setSelectionMode(QAbstractItemView::NoSelection);
    vl->addWidget(m_table);
    m_statusBar = new QStatusBar(this);
    setStatusBar(m_statusBar);

    connect(m_table, SIGNAL(cellClicked(int,int)), this, SLOT(cellClicked(int,int)));
    connect(m_table, SIGNAL(tapAndHold()), this, SLOT(tapAndHold()));
}

void RTControllerMQTT::tapAndHold()
{
    m_tapSeen = true;
}

void RTControllerMQTT::cellClicked(int row, int /* col */)
{
 #if defined(Q_OS_ANDROID) || defined(Q_OS_IOS)
    if (!m_tapSeen)
        return;
#endif
    m_tapSeen = false;
    QString name = ((QLabel *)m_table->cellWidget(row, 0))->text();
    int level = ((QProgressBar *)m_table->cellWidget(row, 1))->value();
    SetDeviceLevelDlg dlg(this, name, level);

    if (dlg.exec() == QDialog::Accepted) {
        foreach(RTMQTTDevice dev, m_deviceMap) {
            if (dev.name == name) {
                QJsonArray jsa;
                QJsonObject jso;
                dev.newLevel = dlg.newLevel();
                dev.writeNewLevel(jso);
                jsa.append(jso);
                QJsonObject jsonNewLevel;
                jsonNewLevel[RTMQTTDEVICE_JSON_SETDEVICELEVEL] = jsa;
                emit setDeviceLevel(dev.controlTopic, jsonNewLevel);
                return;
            }
        }
    }
}

void RTControllerMQTT::initStatusBar()
{
    m_brokerStatus = new QLabel(this);
    m_brokerStatus->setAlignment(Qt::AlignLeft);
    m_statusBar->addWidget(m_brokerStatus, 1);
}

void RTControllerMQTT::saveWindowState()
{
    QSettings settings;

    settings.beginGroup("Window");
    settings.setValue("Geometry", saveGeometry());
    settings.setValue("State", saveState());
    settings.endGroup();

}

void RTControllerMQTT::restoreWindowState()
{
    QSettings settings;

    settings.beginGroup("Window");
    restoreGeometry(settings.value("Geometry").toByteArray());
    restoreState(settings.value("State").toByteArray());

    settings.endGroup();

}

void RTControllerMQTT::onExit()
{
    emit close();
}

void RTControllerMQTT::onConfigure()
{
    ConfigureDlg dlg(this);

    if (dlg.exec() == QDialog::Accepted) {
        clientDisconnected();
        emit clientRestart();
        while (m_table->rowCount() > 0)
            m_table->removeRow(0);
        m_gridMap.clear();
        m_deviceMap.clear();
    }
}

void RTControllerMQTT::onConfigureServers()
{
    ConfigureServerDlg dlg(this);

    if (dlg.exec() == QDialog::Accepted) {
        clientDisconnected();
        emit clientRestart();
        while (m_table->rowCount() > 0)
            m_table->removeRow(0);
        m_gridMap.clear();
        m_deviceMap.clear();
    }
}
