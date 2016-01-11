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

#include <qboxlayout.h>
#include <qformlayout.h>

#include "ConfigureDlg.h"
#include "RTControllerMQTT.h"
#include "RTMQTTDevice.h"
#include "RTMQTTClient.h"

ConfigureDlg::ConfigureDlg(QWidget *parent)
    : QDialog(parent, Qt::WindowCloseButtonHint | Qt::WindowTitleHint)
{
    layoutWindow();
    setWindowTitle("Configure RTControllerMQTT");
    connect(m_buttons, SIGNAL(accepted()), this, SLOT(saveData()));
    connect(m_buttons, SIGNAL(rejected()), this, SLOT(reject()));
}

void ConfigureDlg::saveData()
{
    QSettings settings;

    bool changed = false;

    settings.beginGroup(RTMQTTCLIENT_PARAMS_GROUP);
    if (m_brokerAddress->text() != settings.value(RTMQTTCLIENT_PARAMS_BROKERADDRESS).toString()) {
        changed = true;
        settings.setValue(RTMQTTCLIENT_PARAMS_BROKERADDRESS, m_brokerAddress->text());
    }
    if (m_clientID->text() != settings.value(RTMQTTCLIENT_PARAMS_CLIENTID).toString()) {
        changed = true;
        settings.setValue(RTMQTTCLIENT_PARAMS_CLIENTID, m_clientID->text());
    }
    if (m_clientSecret->text() != settings.value(RTMQTTCLIENT_PARAMS_CLIENTSECRET).toString()) {
        changed = true;
        settings.setValue(RTMQTTCLIENT_PARAMS_CLIENTSECRET, m_clientSecret->text());
    }
    settings.endGroup();

    if (changed)
        accept();
    else
        reject();
}

void ConfigureDlg::layoutWindow()
{
    QSettings settings;

    setModal(true);

    QVBoxLayout *centralLayout = new QVBoxLayout(this);
    centralLayout->setSpacing(20);
    centralLayout->setContentsMargins(11, 11, 11, 11);

    QFormLayout *formLayout = new QFormLayout();
    formLayout->setSpacing(16);
    formLayout->setFieldGrowthPolicy(QFormLayout::AllNonFixedFieldsGrow);

    settings.beginGroup(RTMQTTCLIENT_PARAMS_GROUP);
    m_brokerAddress = new QLineEdit();
    m_brokerAddress->setText(settings.value(RTMQTTCLIENT_PARAMS_BROKERADDRESS).toString());
    m_brokerAddress->setToolTip("The MQTT broker address (e.g. tcp://localhost:1883");
    m_brokerAddress->setMinimumWidth(200);
    formLayout->addRow(tr("MQTT broker address:"), m_brokerAddress);

    m_clientID = new QLineEdit();
    m_clientID->setText(settings.value(RTMQTTCLIENT_PARAMS_CLIENTID).toString());
    m_clientID->setToolTip("The client ID is used to sign on to the NQTT broker");
    m_clientID->setMinimumWidth(200);
    formLayout->addRow(tr("MQTT client ID:"), m_clientID);

    m_clientSecret = new QLineEdit();
    m_clientSecret->setText(settings.value(RTMQTTCLIENT_PARAMS_CLIENTSECRET).toString());
    m_clientSecret->setToolTip("The client secret may be used to sign on to the NQTT broker");
    m_clientSecret->setMinimumWidth(200);
    m_clientSecret->setEchoMode(QLineEdit::Password);
    formLayout->addRow(tr("MQTT client secret:"), m_clientSecret);

    settings.endGroup();

    centralLayout->addLayout(formLayout);

    m_buttons = new QDialogButtonBox(QDialogButtonBox::Ok | QDialogButtonBox::Cancel, Qt::Horizontal, this);
    m_buttons->setCenterButtons(true);

    centralLayout->addWidget(m_buttons);
}
