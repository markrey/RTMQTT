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

#ifndef _CONFIGURESERVERDLG_H
#define _CONFIGURESERVERDLG_H

#include <qdialog.h>
#include <qtablewidget.h>
#include <qdialogbuttonbox.h>
#include <qpushbutton.h>


class ConfigureServerDlg : public QDialog
{
    Q_OBJECT

public:
    ConfigureServerDlg(QWidget *parent);

public slots:
    void onOk();
    void onCancel();
    void buttonClicked(QAbstractButton * button);

private:
    void layoutWindow();
    void insertTableRow(int row, QString value);

    QTableWidget *m_serverTable;
    QDialogButtonBox *m_buttons0;
    QDialogButtonBox *m_buttons1;
    QPushButton *m_buttonAddRow;
    QPushButton *m_buttonAppendRow;
    QPushButton *m_buttonDeleteRow;

    bool m_changed;

};


#endif // CONFIGURESERVERDLG_H
