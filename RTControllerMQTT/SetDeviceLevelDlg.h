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

#ifndef SETDEVICELEVEL_DLG_H
#define SETDEVICELEVEL_DLG_H

#include <qdialog.h>
#include <qpushbutton.h>
#include <qdial.h>
#include <qlabel.h>
#include <qprogressbar.h>

class SetDeviceLevelDlg : public QDialog
{
    Q_OBJECT

public:
    SetDeviceLevelDlg(QWidget *parent, QString name, int level);

    int newLevel();

public slots:
    void onClicked(bool);
    void offClicked(bool);
    void valueChanged(int);

private:
    void layoutWindow(QString name, int level);
    int m_parentWidth;
    int m_parentHeight;

    QDial *m_level;
    QPushButton *m_on;
    QPushButton *m_off;
    QProgressBar *m_value;

    QPushButton *m_okButton;
    QPushButton *m_cancelButton;
};

#endif // SETDEVICELEVEL_DLG_H
