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

#ifndef MAINTABLE_H
#define MAINTABLE_H

#include <QTableWidget>
#include <QGestureEvent>

#define MAINTABLE_ROW_HEIGHT 70

class MainTable : public QTableWidget
{
    Q_OBJECT
public:
    explicit MainTable(QWidget *parent = 0);

signals:
    void tapAndHold();

public slots:
    void newSize(QSize);

protected:

    bool viewportEvent(QEvent *event);

private:
    void touchBegin(QTouchEvent *event);
    void touchUpdate(QTouchEvent *event);
    void touchEnd(QTouchEvent *event);
    void touchCancel(QTouchEvent *event);
    bool processGesture(QGestureEvent *event);
    void swipe(QSwipeGesture *gesture);
    void pan(QPanGesture *gesture);
    void pinch(QPinchGesture *gesture);
    void tap(QTapGesture *gesture);
    bool tapAndHold(QTapAndHoldGesture *gesture);

    int m_currentDelta;
 };

#endif // MAINTABLE_H
