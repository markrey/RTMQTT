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

#include "RTUVCCamMainConsole.h"
#include "RTUVCCamGlue.h"
#include "RTUVCCamVidCap.h"

#include <qcoreapplication.h>

RTUVCCamMainConsole::RTUVCCamMainConsole(QObject *parent, RTUVCCamGlue *glue)
    : QThread(parent), RTUVCCamMain(glue)
{
    start();
}

void RTUVCCamMainConsole::addVidCapSignal(RTUVCCamVidCap *vidCap)
{
    connect(vidCap, SIGNAL(newFrame(int,QByteArray,bool,int,int,int)), this, SLOT(newFrame(int,QByteArray,bool,int,int,int)));
}

void RTUVCCamMainConsole::newFrame(int cameraNum, QByteArray frame, bool jpeg, int width, int height, int rate)
{
    addFrameToQueue(cameraNum, frame, jpeg, width, height, rate);
}


void RTUVCCamMainConsole::run()
{
    while(!m_mustExit) {
        msleep(10);
    }

    QCoreApplication::exit();
}

