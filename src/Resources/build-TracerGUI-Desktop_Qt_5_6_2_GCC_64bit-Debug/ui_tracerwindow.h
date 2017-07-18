/********************************************************************************
** Form generated from reading UI file 'tracerwindow.ui'
**
** Created by: Qt User Interface Compiler version 5.6.2
**
** WARNING! All changes made in this file will be lost when recompiling UI file!
********************************************************************************/

#ifndef UI_TRACERWINDOW_H
#define UI_TRACERWINDOW_H

#include <QtCore/QVariant>
#include <QtWidgets/QAction>
#include <QtWidgets/QApplication>
#include <QtWidgets/QButtonGroup>
#include <QtWidgets/QFrame>
#include <QtWidgets/QGridLayout>
#include <QtWidgets/QHBoxLayout>
#include <QtWidgets/QHeaderView>
#include <QtWidgets/QMainWindow>
#include <QtWidgets/QMenu>
#include <QtWidgets/QMenuBar>
#include <QtWidgets/QSplitter>
#include <QtWidgets/QWidget>
#include "pyqtgraph.h"

QT_BEGIN_NAMESPACE

class Ui_TracerWindow
{
public:
    QAction *actionDisplay_Quasar;
    QAction *actionShow_Galaxy;
    QAction *actionLoad;
    QAction *actionRecord;
    QAction *actionPlay;
    QAction *actionRestart;
    QAction *actionExit;
    QWidget *centralWidget;
    QHBoxLayout *horizontalLayout;
    QFrame *frame;
    QGridLayout *gridLayout;
    QSplitter *splitter;
    PlotWidget *plotView;
    GraphicsLayoutWidget *imgView;
    QMenuBar *menuBar;
    QMenu *menuFile;
    QMenu *menuEdit;
    QMenu *menuView;
    QMenu *menuRun;

    void setupUi(QMainWindow *TracerWindow)
    {
        if (TracerWindow->objectName().isEmpty())
            TracerWindow->setObjectName(QStringLiteral("TracerWindow"));
        TracerWindow->resize(489, 367);
        actionDisplay_Quasar = new QAction(TracerWindow);
        actionDisplay_Quasar->setObjectName(QStringLiteral("actionDisplay_Quasar"));
        actionDisplay_Quasar->setCheckable(true);
        actionDisplay_Quasar->setChecked(true);
        actionShow_Galaxy = new QAction(TracerWindow);
        actionShow_Galaxy->setObjectName(QStringLiteral("actionShow_Galaxy"));
        actionShow_Galaxy->setCheckable(true);
        actionShow_Galaxy->setChecked(true);
        actionLoad = new QAction(TracerWindow);
        actionLoad->setObjectName(QStringLiteral("actionLoad"));
        actionRecord = new QAction(TracerWindow);
        actionRecord->setObjectName(QStringLiteral("actionRecord"));
        actionPlay = new QAction(TracerWindow);
        actionPlay->setObjectName(QStringLiteral("actionPlay"));
        actionRestart = new QAction(TracerWindow);
        actionRestart->setObjectName(QStringLiteral("actionRestart"));
        actionExit = new QAction(TracerWindow);
        actionExit->setObjectName(QStringLiteral("actionExit"));
        centralWidget = new QWidget(TracerWindow);
        centralWidget->setObjectName(QStringLiteral("centralWidget"));
        horizontalLayout = new QHBoxLayout(centralWidget);
        horizontalLayout->setSpacing(6);
        horizontalLayout->setContentsMargins(11, 11, 11, 11);
        horizontalLayout->setObjectName(QStringLiteral("horizontalLayout"));
        frame = new QFrame(centralWidget);
        frame->setObjectName(QStringLiteral("frame"));
        frame->setFrameShape(QFrame::NoFrame);
        frame->setFrameShadow(QFrame::Plain);
        gridLayout = new QGridLayout(frame);
        gridLayout->setSpacing(6);
        gridLayout->setContentsMargins(11, 11, 11, 11);
        gridLayout->setObjectName(QStringLiteral("gridLayout"));
        splitter = new QSplitter(frame);
        splitter->setObjectName(QStringLiteral("splitter"));
        splitter->setOrientation(Qt::Vertical);
        plotView = new PlotWidget(splitter);
        plotView->setObjectName(QStringLiteral("plotView"));
        splitter->addWidget(plotView);
        imgView = new GraphicsLayoutWidget(splitter);
        imgView->setObjectName(QStringLiteral("imgView"));
        splitter->addWidget(imgView);

        gridLayout->addWidget(splitter, 0, 0, 1, 1);


        horizontalLayout->addWidget(frame);

        TracerWindow->setCentralWidget(centralWidget);
        menuBar = new QMenuBar(TracerWindow);
        menuBar->setObjectName(QStringLiteral("menuBar"));
        menuBar->setGeometry(QRect(0, 0, 489, 26));
        menuFile = new QMenu(menuBar);
        menuFile->setObjectName(QStringLiteral("menuFile"));
        menuEdit = new QMenu(menuBar);
        menuEdit->setObjectName(QStringLiteral("menuEdit"));
        menuView = new QMenu(menuBar);
        menuView->setObjectName(QStringLiteral("menuView"));
        menuRun = new QMenu(menuBar);
        menuRun->setObjectName(QStringLiteral("menuRun"));
        TracerWindow->setMenuBar(menuBar);

        menuBar->addAction(menuFile->menuAction());
        menuBar->addAction(menuEdit->menuAction());
        menuBar->addAction(menuRun->menuAction());
        menuBar->addAction(menuView->menuAction());
        menuFile->addAction(actionLoad);
        menuFile->addAction(actionRecord);
        menuFile->addSeparator();
        menuFile->addAction(actionExit);
        menuView->addAction(actionDisplay_Quasar);
        menuView->addAction(actionShow_Galaxy);
        menuRun->addAction(actionPlay);
        menuRun->addSeparator();
        menuRun->addAction(actionRestart);

        retranslateUi(TracerWindow);

        QMetaObject::connectSlotsByName(TracerWindow);
    } // setupUi

    void retranslateUi(QMainWindow *TracerWindow)
    {
        TracerWindow->setWindowTitle(QApplication::translate("TracerWindow", "TracerWindow", 0));
        actionDisplay_Quasar->setText(QApplication::translate("TracerWindow", "Show Quasar", 0));
        actionDisplay_Quasar->setShortcut(QApplication::translate("TracerWindow", "Q", 0));
        actionShow_Galaxy->setText(QApplication::translate("TracerWindow", "Show Galaxy", 0));
        actionShow_Galaxy->setShortcut(QApplication::translate("TracerWindow", "G", 0));
        actionLoad->setText(QApplication::translate("TracerWindow", "Load", 0));
        actionLoad->setShortcut(QApplication::translate("TracerWindow", "Ctrl+O", 0));
        actionRecord->setText(QApplication::translate("TracerWindow", "Record", 0));
        actionRecord->setShortcut(QApplication::translate("TracerWindow", "Ctrl+R", 0));
        actionPlay->setText(QApplication::translate("TracerWindow", "Play", 0));
        actionPlay->setShortcut(QApplication::translate("TracerWindow", "Space", 0));
        actionRestart->setText(QApplication::translate("TracerWindow", "Restart", 0));
        actionRestart->setShortcut(QApplication::translate("TracerWindow", "R", 0));
        actionExit->setText(QApplication::translate("TracerWindow", "Exit", 0));
        menuFile->setTitle(QApplication::translate("TracerWindow", "File", 0));
        menuEdit->setTitle(QApplication::translate("TracerWindow", "Edit", 0));
        menuView->setTitle(QApplication::translate("TracerWindow", "View", 0));
        menuRun->setTitle(QApplication::translate("TracerWindow", "Run", 0));
    } // retranslateUi

};

namespace Ui {
    class TracerWindow: public Ui_TracerWindow {};
} // namespace Ui

QT_END_NAMESPACE

#endif // UI_TRACERWINDOW_H
