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

#include <qheaderview.h>
#include <qevent.h>
#include <qdebug.h>
#include <qscrollbar.h>

#include "MainTable.h"

MainTable::MainTable(QWidget *parent) :
    QTableWidget(parent)
{
    setColumnCount(2);
    setHorizontalScrollBarPolicy(Qt::ScrollBarAlwaysOff);
    verticalScrollBar()->setVisible(false);
    resize(parent->width(), parent->height());
    setColumnWidth(0, width() / 2);
    setColumnWidth(1, width() / 2);
    verticalHeader()->setVisible(false);
    setHorizontalHeaderLabels(QStringList() << tr("Device") << tr("State") );
    setContentsMargins(10, 10, 10, 10);

    m_currentDelta = 0;
    viewport()->grabGesture(Qt::PanGesture);
    viewport()->grabGesture(Qt::SwipeGesture);
    viewport()->grabGesture(Qt::PinchGesture);
    viewport()->grabGesture(Qt::TapGesture);
    viewport()->grabGesture(Qt::TapAndHoldGesture);

 //   setAttribute(Qt::WA_AcceptTouchEvents);
 }


bool MainTable::viewportEvent(QEvent *event)
{
    switch (event->type()) {
    case QEvent::Gesture:
        processGesture((QGestureEvent *)event);
        return true;

    case QEvent::TouchBegin:
        touchBegin((QTouchEvent *)event);
        return false;

    case QEvent::TouchUpdate:
        touchUpdate((QTouchEvent *)event);
        return false;

    case QEvent::TouchEnd:
        touchEnd((QTouchEvent *)event);
        return false;

    case QEvent::TouchCancel:
        touchCancel((QTouchEvent *)event);
        return false;

     default:
        return QAbstractScrollArea::viewportEvent(event);
    }
}


void MainTable::newSize(QSize theSize)
{
    theSize.setHeight(theSize.height() - 100);
    resize(theSize);
    setColumnWidth(0, (theSize.width() - 40) / 2);
    setColumnWidth(1, (theSize.width() - 40) / 2);
}


void MainTable::touchBegin(QTouchEvent *event)
{
    QList<QTouchEvent::TouchPoint> tpList = event->touchPoints();
    if (tpList.count() != 1)
        return;

    qDebug() << "touch begin";
}

void MainTable::touchUpdate(QTouchEvent *event)
{
    int sliderDelta = 0;

    QList<QTouchEvent::TouchPoint> tpList = event->touchPoints();
    if (tpList.count() != 1)
        return;

    qDebug() << "touch update";

    QTouchEvent::TouchPoint tp = tpList.first();
    int delta = tp.pos().y() - tp.lastPos().y();
    m_currentDelta -= delta;
    if (m_currentDelta > MAINTABLE_ROW_HEIGHT) {
        m_currentDelta = 0;
        sliderDelta = 1;
    } else {
        if (m_currentDelta < -MAINTABLE_ROW_HEIGHT) {
            m_currentDelta = 0;
            sliderDelta = -1;
        }
    }
    verticalScrollBar()->setValue(verticalScrollBar()->value() + sliderDelta);
    update();
}

void MainTable::touchEnd(QTouchEvent *event)
{
    QList<QTouchEvent::TouchPoint> tpList = event->touchPoints();
    if (tpList.count() != 1)
        return;

    qDebug() << "touch end";

}

void MainTable::touchCancel(QTouchEvent *event)
{
    QList<QTouchEvent::TouchPoint> tpList = event->touchPoints();
    if (tpList.count() != 1)
        return;

    qDebug() << "touch cancel";

}


bool MainTable::processGesture(QGestureEvent *event)
{
    QGesture *gesture;
    qDebug() << "processGesture";
    if ((gesture = event->gesture(Qt::SwipeGesture)))
        swipe((QSwipeGesture *)gesture);
    else if ((gesture = event->gesture(Qt::PanGesture)))
        pan((QPanGesture *)gesture);
    else if ((gesture = event->gesture(Qt::PinchGesture)))
        pinch((QPinchGesture *)gesture);
    else if ((gesture = event->gesture(Qt::TapGesture)))
        tap((QTapGesture *)gesture);
    else if ((gesture = event->gesture(Qt::TapAndHoldGesture)))
        return tapAndHold((QTapAndHoldGesture *)gesture);
    return true;
}

void MainTable::swipe(QSwipeGesture *gesture)
{
    qDebug() << "swipe " << gesture->swipeAngle();
}

void MainTable::pan(QPanGesture *gesture)
{
   qDebug() << "pan " << gesture->delta();
   verticalScrollBar()->setValue(verticalScrollBar()->value() - gesture->delta().y() / 2);
   update();

}

void MainTable::pinch(QPinchGesture *gesture)
{
   qDebug() << "pinch " << gesture->centerPoint();
}

void MainTable::tap(QTapGesture *gesture)
{
   qDebug() << "tap " << gesture->position();
}

bool MainTable::tapAndHold(QTapAndHoldGesture *gesture)
{
   qDebug() << "tapAndHold " << gesture->gestureType();
   emit tapAndHold();
   return false;
}


