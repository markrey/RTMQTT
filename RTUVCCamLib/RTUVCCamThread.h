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

#ifndef _RTUVCCAMTHREAD_H_
#define _RTUVCCAMTHREAD_H_

#include <qthread.h>

class InternalThread : public QThread
{
    Q_OBJECT

public:
    inline void msleep(unsigned long msecs) { QThread::msleep(msecs); }
};

class RTUVCCamThread : public QObject
{
    Q_OBJECT

public:
    RTUVCCamThread();

    //  resumeThread() is called when init is complete

    virtual void resumeThread();

    //  exitThread is called to terminate and delete the thread

    virtual void exitThread() { emit internalEndThread(); }

    InternalThread *thread() { return m_thread; }

public slots:
    //	Qt threading stuff

    void internalRunLoop() { initThread(); emit running();}
    void cleanup() {finishThread(); emit internalKillThread(); }

signals:
    //  Qt threading stuff

    void running();											// emitted when everything set up and thread active
    void internalEndThread();								// this to end thread
    void internalKillThread();								// tells the QThread to quit

protected:
    virtual void initThread();
    virtual void finishThread();

    //  overrides that must be provided by the subclass

    virtual void initModule() = 0;                          // performs all module-specific initialization
    virtual void stopModule() = 0;                          // closes down module

    InternalThread *m_thread;
};

#endif // _RTUVCCANTHREAD_H_
