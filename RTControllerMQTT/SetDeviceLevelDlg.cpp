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

#include <qlabel.h>
#include <qboxlayout.h>
#include <qformlayout.h>
#include <qvalidator.h>
#include <qscreen.h>
#include <qguiapplication.h>
#include <qscreen.h>

#include "SetDeviceLevelDlg.h"

SetDeviceLevelDlg::SetDeviceLevelDlg(QWidget *parent, QString name, int level)
    : QDialog(parent, Qt::WindowCloseButtonHint | Qt::WindowTitleHint)
{
    m_parentWidth = parent->width();
    m_parentHeight = parent->height();
    layoutWindow(name, level);
#if defined(Q_OS_IOS) || defined(Q_OS_ANDROID)
    setWindowState(Qt::WindowFullScreen);
#endif

    connect(m_okButton, SIGNAL(clicked()), this, SLOT(accept()));
    connect(m_cancelButton, SIGNAL(clicked()), this, SLOT(reject()));
    connect(m_on, SIGNAL(clicked(bool)), this, SLOT(onClicked(bool)));
    connect(m_off, SIGNAL(clicked(bool)), this, SLOT(offClicked(bool)));
    connect(m_level, SIGNAL(valueChanged(int)), this, SLOT(valueChanged(int)));
}

int SetDeviceLevelDlg::newLevel()
{
    return m_level->value();
}

void SetDeviceLevelDlg::valueChanged(int value)
{
    m_value->setValue(value);
}

void SetDeviceLevelDlg::onClicked(bool)
{
    m_level->setValue(255);
}

void SetDeviceLevelDlg::offClicked(bool)
{
    m_level->setValue(0);
}

void SetDeviceLevelDlg::layoutWindow(QString name, int level)
{
    QLabel *label;
    QVBoxLayout *vLayout = new QVBoxLayout();
    QList<QScreen *> screen = QGuiApplication::screens();

    if (screen.at(0)->isPortrait(screen.at(0)->orientation())) {
        label = new QLabel("Set device level:");
        label->setAlignment(Qt::AlignLeft);
        label->setStyleSheet("QLabel {font-size: 30px}");
        vLayout->addWidget(label);
        label = new QLabel(name);
        label->setAlignment(Qt::AlignLeft);
        label->setIndent(10);
        label->setStyleSheet("QLabel {font-size: 30px}");
        vLayout->addWidget(label);
    } else {
        label = new QLabel("Set device level: " + name);
        label->setAlignment(Qt::AlignLeft);
        label->setStyleSheet("QLabel {font-size: 30px}");
        vLayout->addWidget(label);
    }

    vLayout->addSpacing(10);

    //  Add dial

    m_level = new QDial();
    m_level->setMinimumSize(200, 200);

#if defined(Q_OS_IOS)
    if (m_parentHeight > m_parentWidth)
        m_level->setMinimumSize(m_parentWidth / 3, m_parentWidth / 3);
    else
        m_level->setMinimumSize(m_parentHeight / 3, m_parentHeight / 3);
#endif

#if defined(Q_OS_ANDROID)
    if (m_parentHeight > m_parentWidth)
        m_level->setMinimumSize(m_parentWidth, m_parentWidth);
    else
        m_level->setMinimumSize(m_parentHeight, m_parentHeight);
#endif

    m_level->setRange(0, 255);
    if ((level >= 0) && (level <= 255))
        m_level->setValue(level);
    else
        m_level->setValue(0);
    m_level->setNotchesVisible(true);
    vLayout->addWidget(m_level);

    vLayout->addSpacing(10);

    //  Add progress bar

    m_value = new QProgressBar();
    m_value->setMinimum(0);
    m_value->setMaximum(255);
    m_value->setAlignment(Qt::AlignHCenter);
    m_value->setMinimumHeight(30);
    m_value->setValue(level);
    vLayout->addWidget(m_value);

    vLayout->addSpacing(10);

    //  Add on and off buttons

    QHBoxLayout *levelBox = new QHBoxLayout();
    m_on = new QPushButton("On");
    m_on->setStyleSheet("QPushButton {font-size: 30px; }");
    m_on->setMinimumWidth(120);
    m_on->setMinimumHeight(40);
    m_off = new QPushButton("Off");
    m_off->setStyleSheet("QPushButton {font-size: 30px; }");
    m_off->setMinimumWidth(120);
    m_off->setMinimumHeight(40);

    levelBox->addStretch();
    levelBox->addWidget(m_off);
    levelBox->addStretch();
    levelBox->addWidget(m_on);
    levelBox->addStretch();
    vLayout->addLayout(levelBox);

    vLayout->addSpacing(20);

    //  Add ok and cancel

    QHBoxLayout *hLayout = new QHBoxLayout();

    m_okButton = new QPushButton("OK");
    m_okButton->setStyleSheet("QPushButton {font-size: 30px; }");
    m_okButton->setMinimumWidth(120);
    m_okButton->setMinimumHeight(40);

    m_cancelButton = new QPushButton("Cancel");
    m_cancelButton->setStyleSheet("QPushButton {font-size: 30px; }");
    m_cancelButton->setMinimumWidth(120);
    m_cancelButton->setMinimumHeight(40);

    hLayout->addStretch();
    hLayout->addWidget(m_cancelButton);
    hLayout->addStretch();
    hLayout->addWidget(m_okButton);
    hLayout->addStretch();
    vLayout->addLayout(hLayout);

    setLayout(vLayout);
};
