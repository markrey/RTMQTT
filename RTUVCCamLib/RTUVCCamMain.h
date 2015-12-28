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
//  SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE. IN CONNECTION WITH THE
//  SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

#ifndef RTUVCCAMMAIN_H
#define RTUVCCAMMAIN_H

#include <QThread>
#include <qdialog.h>
#include <qmutex.h>
#include <qbytearray.h>
#include <qqueue.h>

class RTUVCCamClient;
class RTUVCCamGlue;
class RTUVCCamVidCap;

typedef struct
{
    RTUVCCamVidCap *vidCap;
    QString status;
    QQueue <QByteArray> frameQueue;
    int cameraNum;
    int width;
    int height;
    int rate;
    bool jpeg;
} RTUVCCAM_CAPTURE;

class RTUVCCamMain
{
public:
    RTUVCCamMain(RTUVCCamGlue *glue);
    virtual ~RTUVCCamMain();

    virtual void setWindowTitle(char *title) = 0;           // sets the window title in GUI mode
    virtual void displayImage(QByteArray image, int width, int height, QString timestamp) = 0; // displays an image in GUI mode
    virtual void displayJpegImage(QByteArray image, QString timestamp) = 0; // displays a Jpeg image in GUI mode

    virtual void stopRunning() = 0;

    bool vidCapOpen(int cameraNum, int width, int height, int rate);
    bool vidCapClose(int cameraNum);
    bool vidCapGetFrame(int cameraNum, QByteArray& frame, bool& jpeg,
                                             int& width, int& height, int& rate);
    virtual void addVidCapSignal(RTUVCCamVidCap *vidCap) = 0;   // adds signal for captured frames


protected:
    void addFrameToQueue(int cameraNum, const QByteArray& frame, bool jpeg, int width, int height, int rate);

    RTUVCCamGlue *m_glue;
    bool m_mustExit;

private:
    void removeVidCap(int cameraNum);
    QMutex m_vidCapLock;
    QList<RTUVCCAM_CAPTURE *> m_vidCaps;
};
#endif // RTUVCCAMMAIN_H

