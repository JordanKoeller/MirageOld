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
#include <QtWidgets/QHeaderView>
#include <QtWidgets/QMainWindow>
#include <QtWidgets/QMenu>
#include <QtWidgets/QMenuBar>
#include <QtWidgets/QSplitter>
#include <QtWidgets/QStatusBar>
#include <QtWidgets/QVBoxLayout>
#include <QtWidgets/QWidget>
#include "pyqtgraph.h"

QT_BEGIN_NAMESPACE

class Ui_TracerWindow
{
public:
    QAction *showQuasarAction;
    QAction *showGalaxyAction;
    QAction *actionLoad;
    QAction *recordAction;
    QAction *playPauseAction;
    QAction *resetAction;
    QAction *actionExit;
    QAction *actionLightCurve;
    QAction *actionPreferences;
    QWidget *centralWidget;
    QVBoxLayout *verticalLayout;
    QFrame *tracerFrame;
    QGridLayout *gridLayout;
    QSplitter *splitter;
    PlotWidget *plotView;
    GraphicsLayoutWidget *imgView;
    GradientWidget *gradientSelector;
    QMenuBar *menuBar;
    QMenu *menuFile;
    QMenu *menuEdit;
    QMenu *menuView;
    QMenu *menuRun;
    QStatusBar *statusBar;

    void setupUi(QMainWindow *TracerWindow)
    {
        if (TracerWindow->objectName().isEmpty())
            TracerWindow->setObjectName(QStringLiteral("TracerWindow"));
        TracerWindow->resize(489, 367);
        showQuasarAction = new QAction(TracerWindow);
        showQuasarAction->setObjectName(QStringLiteral("showQuasarAction"));
        showQuasarAction->setCheckable(true);
        showQuasarAction->setChecked(true);
        showGalaxyAction = new QAction(TracerWindow);
        showGalaxyAction->setObjectName(QStringLiteral("showGalaxyAction"));
        showGalaxyAction->setCheckable(true);
        showGalaxyAction->setChecked(true);
        actionLoad = new QAction(TracerWindow);
        actionLoad->setObjectName(QStringLiteral("actionLoad"));
        recordAction = new QAction(TracerWindow);
        recordAction->setObjectName(QStringLiteral("recordAction"));
        playPauseAction = new QAction(TracerWindow);
        playPauseAction->setObjectName(QStringLiteral("playPauseAction"));
        resetAction = new QAction(TracerWindow);
        resetAction->setObjectName(QStringLiteral("resetAction"));
        actionExit = new QAction(TracerWindow);
        actionExit->setObjectName(QStringLiteral("actionExit"));
        actionLightCurve = new QAction(TracerWindow);
        actionLightCurve->setObjectName(QStringLiteral("actionLightCurve"));
        actionPreferences = new QAction(TracerWindow);
        actionPreferences->setObjectName(QStringLiteral("actionPreferences"));
        centralWidget = new QWidget(TracerWindow);
        centralWidget->setObjectName(QStringLiteral("centralWidget"));
        verticalLayout = new QVBoxLayout(centralWidget);
        verticalLayout->setSpacing(6);
        verticalLayout->setContentsMargins(11, 11, 11, 11);
        verticalLayout->setObjectName(QStringLiteral("verticalLayout"));
        tracerFrame = new QFrame(centralWidget);
        tracerFrame->setObjectName(QStringLiteral("tracerFrame"));
        tracerFrame->setFrameShape(QFrame::NoFrame);
        tracerFrame->setFrameShadow(QFrame::Plain);
        gridLayout = new QGridLayout(tracerFrame);
        gridLayout->setSpacing(6);
        gridLayout->setContentsMargins(11, 11, 11, 11);
        gridLayout->setObjectName(QStringLiteral("gridLayout"));
        splitter = new QSplitter(tracerFrame);
        splitter->setObjectName(QStringLiteral("splitter"));
        splitter->setOrientation(Qt::Vertical);
        plotView = new PlotWidget(splitter);
        plotView->setObjectName(QStringLiteral("plotView"));
        splitter->addWidget(plotView);
        imgView = new GraphicsLayoutWidget(splitter);
        imgView->setObjectName(QStringLiteral("imgView"));
        splitter->addWidget(imgView);

        gridLayout->addWidget(splitter, 1, 0, 1, 1);


        verticalLayout->addWidget(tracerFrame);

        gradientSelector = new GradientWidget(centralWidget);
        gradientSelector->setObjectName(QStringLiteral("gradientSelector"));

        verticalLayout->addWidget(gradientSelector);

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
        statusBar = new QStatusBar(TracerWindow);
        statusBar->setObjectName(QStringLiteral("statusBar"));
        TracerWindow->setStatusBar(statusBar);

        menuBar->addAction(menuFile->menuAction());
        menuBar->addAction(menuEdit->menuAction());
        menuBar->addAction(menuRun->menuAction());
        menuBar->addAction(menuView->menuAction());
        menuFile->addAction(actionLoad);
        menuFile->addAction(recordAction);
        menuFile->addSeparator();
        menuFile->addAction(actionLightCurve);
        menuFile->addSeparator();
        menuFile->addAction(actionExit);
        menuFile->addSeparator();
        menuFile->addAction(actionPreferences);
        menuView->addAction(showQuasarAction);
        menuView->addAction(showGalaxyAction);
        menuRun->addAction(playPauseAction);
        menuRun->addSeparator();
        menuRun->addAction(resetAction);

        retranslateUi(TracerWindow);

        QMetaObject::connectSlotsByName(TracerWindow);
    } // setupUi

    void retranslateUi(QMainWindow *TracerWindow)
    {
        TracerWindow->setWindowTitle(QApplication::translate("TracerWindow", "TracerWindow", 0));
        showQuasarAction->setText(QApplication::translate("TracerWindow", "Show Quasar", 0));
        showQuasarAction->setShortcut(QApplication::translate("TracerWindow", "Q", 0));
        showGalaxyAction->setText(QApplication::translate("TracerWindow", "Show Galaxy", 0));
        showGalaxyAction->setShortcut(QApplication::translate("TracerWindow", "G", 0));
        actionLoad->setText(QApplication::translate("TracerWindow", "Load", 0));
        actionLoad->setShortcut(QApplication::translate("TracerWindow", "Ctrl+O", 0));
        recordAction->setText(QApplication::translate("TracerWindow", "Record", 0));
        recordAction->setShortcut(QApplication::translate("TracerWindow", "Ctrl+R", 0));
        playPauseAction->setText(QApplication::translate("TracerWindow", "Play", 0));
        playPauseAction->setShortcut(QApplication::translate("TracerWindow", "Space", 0));
        resetAction->setText(QApplication::translate("TracerWindow", "Restart", 0));
        resetAction->setShortcut(QApplication::translate("TracerWindow", "R", 0));
        actionExit->setText(QApplication::translate("TracerWindow", "Exit", 0));
        actionLightCurve->setText(QApplication::translate("TracerWindow", "Export Light Curve", 0));
        actionLightCurve->setShortcut(QApplication::translate("TracerWindow", "Ctrl+L", 0));
        actionPreferences->setText(QApplication::translate("TracerWindow", "Preferences", 0));
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
