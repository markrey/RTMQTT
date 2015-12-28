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

#include "RTUVCCamGlue.h"
#include "RTUVCCamMainConsole.h"
#include "RTUVCCamMainWindow.h"
#include "RTUVCCamArgs.h"

#include <qmutex.h>
#include <qcoreapplication.h>
#include <qapplication.h>

QMutex lockRTUVCCam;

RTUVCCamGlue::RTUVCCamGlue()
{
    m_main = NULL;
}

RTUVCCamGlue::~RTUVCCamGlue()
{
    if (m_main != NULL)
        stopLib();
}

void RTUVCCamGlue::startLib(int& argc, char **argv, bool showWindow)
{
    m_argc = argc;
    m_argv = argv;

    m_daemonMode = RTUVCCamArgs::checkDaemonModeFlag(m_argc, m_argv);

    if (RTUVCCamArgs::checkConsoleModeFlag(m_argc, m_argv)) {
        QCoreApplication a(m_argc, m_argv);
        m_main = new RTUVCCamMainConsole(&a, this);
        a.exec();
    } else {
        QApplication a(m_argc, m_argv);
        m_main = new RTUVCCamMainWindow(this);
        if (showWindow)
            ((RTUVCCamMainWindow *)m_main)->show();
        a.exec();
    }
 }

void RTUVCCamGlue::stopLib()
{
    m_main->stopRunning();
    m_main = NULL;
}

void RTUVCCamGlue::setWindowTitle(char *title)
{
    m_main->setWindowTitle(title);
}

void RTUVCCamGlue::displayImage(unsigned char *image, int length,
                                    int width, int height, char *timestamp)
{
    m_main->displayImage(QByteArray((const char *)image, length), width, height, timestamp);
}

void RTUVCCamGlue::displayJpegImage(unsigned char *image, int length, char *timestamp)
{
    m_main->displayJpegImage(QByteArray((const char *)image, length), timestamp);
}

bool RTUVCCamGlue::vidCapOpen(int cameraNum, int width, int height, int rate)
{
    return m_main->vidCapOpen(cameraNum, width, height, rate);
}

bool RTUVCCamGlue::vidCapClose(int cameraNum)
{
    return m_main->vidCapClose(cameraNum);
}

bool RTUVCCamGlue::vidCapGetFrame(int cameraNum, unsigned char** frame, int& length, bool& jpeg,
                                         int& width, int& height, int& rate)
{
    QByteArray qframe;

    *frame = NULL;

    if (!m_main->vidCapGetFrame(cameraNum, qframe, jpeg, width, height, rate))
        return false;
    *frame = (unsigned char *)malloc(qframe.length());
    memcpy(*frame, qframe.data(), qframe.length());
    length = qframe.length();
    return true;
}

