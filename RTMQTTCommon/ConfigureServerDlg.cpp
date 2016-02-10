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

#include <QLineEdit>
#include <QCheckBox>

#include "RTControllerMQTT.h"
#include "ConfigureServerDlg.h"

ConfigureServerDlg::ConfigureServerDlg(QWidget *parent)
    : QDialog(parent)
{
    layoutWindow();
    setWindowTitle("Configure MQTT device servers");
    connect(m_buttons1, SIGNAL(accepted()), this, SLOT(onOk()));
    connect(m_buttons1, SIGNAL(rejected()), this, SLOT(onCancel()));
    m_changed = false;
}


void ConfigureServerDlg::onOk()
{
    int settingsRow;

    QSettings settings;

    if (!m_changed) {
        int	size = settings.beginReadArray(RTCONTROLLER_PARAMS_SERVERS);

        m_changed = size != m_serverTable->rowCount();		// entry must have been added or deleted
        if (!m_changed) {
            for (int row = 0; row < size; row++) {
                settings.setArrayIndex(row);
                if (((QLineEdit *)(m_serverTable->cellWidget(row, 1)))->text() != settings.value(RTCONTROLLER_PARAMS_SERVERID).toString()) {
                    m_changed = true;
                    break;
                }
            }
        }
        settings.endArray();
    }
    if (m_changed) {
        settings.remove(RTCONTROLLER_PARAMS_SERVERS);      // clear old entries
        settingsRow = 0;
        settings.beginWriteArray(RTCONTROLLER_PARAMS_SERVERS);
        for (int row = 0; row < m_serverTable->rowCount(); row++) {
            settings.setArrayIndex(settingsRow);
            if (((QLineEdit *)(m_serverTable->cellWidget(row, 1)))->text().length() > 0) {
                settings.setValue(RTCONTROLLER_PARAMS_SERVERID, ((QLineEdit *)(m_serverTable->cellWidget(row, 1)))->text());
                settingsRow++;
            }
        }
        settings.endArray();
        accept();
        return;
    } else {
        reject();
    }

}

void ConfigureServerDlg::onCancel()
{
    reject();
}

void ConfigureServerDlg::layoutWindow()
{
    QWidget *centralWidget = new QWidget(this);
    QVBoxLayout *verticalLayout = new QVBoxLayout(centralWidget);
    setMinimumSize(560, 500);
    centralWidget->setMinimumSize(550, 490);
    verticalLayout->setSpacing(6);
    verticalLayout->setContentsMargins(10, 5, 10, 5);


    m_serverTable = new QTableWidget();
    m_serverTable->setColumnCount(2);
    m_serverTable->setColumnWidth(0, 50);
    m_serverTable->setColumnWidth(1, 450);

    m_serverTable->setHorizontalHeaderLabels(QStringList() << "Select" << tr("Stream path"));
    m_serverTable->setSelectionMode(QAbstractItemView::NoSelection);

    verticalLayout->addWidget(m_serverTable);

    QSettings settings;

    int	size = settings.beginReadArray(RTCONTROLLER_PARAMS_SERVERS);
    for (int row = 0; row < size; row++) {
        settings.setArrayIndex(row);
        insertTableRow(row, settings.value(RTCONTROLLER_PARAMS_SERVERID).toString());
    }
    settings.endArray();

    m_buttons0 = new QDialogButtonBox(Qt::Horizontal);
    m_buttons0->setCenterButtons(true);

    m_buttonAddRow = m_buttons0->addButton("Insert", QDialogButtonBox::ActionRole);
    m_buttonAppendRow = m_buttons0->addButton("Append", QDialogButtonBox::ActionRole);
    m_buttonDeleteRow = m_buttons0->addButton("Delete", QDialogButtonBox::ActionRole);
    verticalLayout->addWidget(m_buttons0);

    m_buttons1 = new QDialogButtonBox(QDialogButtonBox::Ok | QDialogButtonBox::Cancel, Qt::Horizontal);
    m_buttons1->setCenterButtons(true);
    verticalLayout->addWidget(m_buttons1);

    connect(m_buttons0, SIGNAL(clicked(QAbstractButton *)), this, SLOT(buttonClicked(QAbstractButton *)));
    connect(m_buttons1, SIGNAL(clicked(QAbstractButton *)), this, SLOT(buttonClicked(QAbstractButton *)));
}

void ConfigureServerDlg::buttonClicked(QAbstractButton *button)
{
    int row;
    int newRow;

    if (button == m_buttonDeleteRow) {
        row = 0;

        while (row < m_serverTable->rowCount()) {
            if (((QCheckBox *)(m_serverTable->cellWidget(row, 0)))->checkState() == Qt::Checked) {
                for (newRow = row; newRow < (m_serverTable->rowCount() - 1); newRow++) {	// move other entries up
                    ((QCheckBox *)(m_serverTable->cellWidget(newRow, 0)))->setCheckState(
                            ((QCheckBox *)(m_serverTable->cellWidget(newRow + 1, 0)))->checkState());
                    ((QLineEdit *)(m_serverTable->cellWidget(newRow, 1)))->setText(
                            ((QLineEdit *)(m_serverTable->cellWidget(newRow + 1, 1)))->text());
                }
                m_serverTable->setRowCount(m_serverTable->rowCount() - 1);
            } else {
                row++;
            }
        }

    } else if (button == m_buttonAppendRow) {
        insertTableRow(m_serverTable->rowCount(), "");
    } else if (button == m_buttonAddRow) {
        row = 0;
        while (row < m_serverTable->rowCount()) {
            if (((QCheckBox *)(m_serverTable->cellWidget(row, 0)))->checkState() == Qt::Checked) {
                insertTableRow(row, "");
                row++;
            }
            row++;
        }
    }
}

void ConfigureServerDlg::insertTableRow(int row, QString value)
{
    m_serverTable->insertRow(row);
    m_serverTable->setRowHeight(row, 20);

    QCheckBox *checkBox = new QCheckBox(m_serverTable);
    m_serverTable->setCellWidget(row, 0, checkBox);

    QLineEdit *lineEdit = new QLineEdit(value, this);
    m_serverTable->setCellWidget(row, 1, lineEdit);
}

