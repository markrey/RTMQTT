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

#ifndef RTUVCCAMMAINWINDOW_H
#define RTUVCCAMMAINWINDOW_H

#include <qmainwindow.h>
#include <qlabel.h>

#include "RTUVCCamMain.h"

class RTUVCCamMainWindow : public QMainWindow, public RTUVCCamMain
{
    Q_OBJECT

public:
    RTUVCCamMainWindow(RTUVCCamGlue *glue);

    void setWindowTitle(char *title);
    void displayImage(QByteArray image, int width, int height, QString timestamp);
    void displayJpegImage(QByteArray image, QString timestamp);

    bool sendAVData(int servicePort, unsigned char *videoData, int videoLength,
                        unsigned char *audioData, int audioLength); // sends an AV data message
    bool sendJpegAVData(int servicePort, unsigned char *videoData, int videoLength,
                        unsigned char *audioData, int audioLength); // sends an AV data message
    bool sendSensorData(int servicePort, unsigned char *data, int dataLength); // sends a sensor multicast message
    bool sendMulticastData(int servicePort, unsigned char *data, int dataLength); // sends a generic multicast message
    bool sendE2EData(int servicePort, unsigned char *data, int dataLength); // sends a generic E2E message

    void stopRunning();

public slots:
    void newFrame(int cameraNum, QByteArray frame, bool jpeg, int width, int height, int rate);

private slots:
    void windowTitleSlot(QString title);
    void displayImageSlot(QByteArray image, int width, int height, QString timestamp);
    void displayJpegImageSlot(QByteArray image, QString timestamp);

signals:
    void windowTitleSignal(QString title);
    void displayImageSignal(QByteArray image, int width, int height, QString timestamp);
    void displayJpegImageSignal(QByteArray image, QString timestamp);
    void clientSendAVData(int servicePort, QByteArray video, QByteArray audio);
    void clientSendJpegAVData(int servicePort, QByteArray video, QByteArray audio);
    void clientSendSensorData(int servicePort, QByteArray data);
    void clientSendMulticastData(int servicePort, QByteArray data);
    void clientSendE2EData(int servicePort, QByteArray data);

protected:
    void addVidCapSignal(RTUVCCamVidCap *vidCap);

private:
    void displayPixmap(const QImage& image, const QString& timestamp);
    QLabel *m_imageView;
};

#endif // RTUVCCAMMAINWINDOW_H

