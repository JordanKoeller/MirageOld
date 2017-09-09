/********************************************************************************
** Form generated from reading UI file 'preferencesdialog.ui'
**
** Created by: Qt User Interface Compiler version 5.6.2
**
** WARNING! All changes made in this file will be lost when recompiling UI file!
********************************************************************************/

#ifndef UI_PREFERENCESDIALOG_H
#define UI_PREFERENCESDIALOG_H

#include <QtCore/QVariant>
#include <QtWidgets/QAction>
#include <QtWidgets/QApplication>
#include <QtWidgets/QButtonGroup>
#include <QtWidgets/QCheckBox>
#include <QtWidgets/QDialog>
#include <QtWidgets/QDialogButtonBox>
#include <QtWidgets/QFormLayout>
#include <QtWidgets/QFrame>
#include <QtWidgets/QHBoxLayout>
#include <QtWidgets/QHeaderView>
#include <QtWidgets/QLabel>
#include <QtWidgets/QRadioButton>
#include <QtWidgets/QSpinBox>
#include <QtWidgets/QTabWidget>
#include <QtWidgets/QVBoxLayout>
#include <QtWidgets/QWidget>

QT_BEGIN_NAMESPACE

class Ui_Dialog
{
public:
    QVBoxLayout *verticalLayout;
    QTabWidget *tabWidget;
    QWidget *tab_3;
    QVBoxLayout *verticalLayout_3;
    QCheckBox *rayTraceSelector;
    QFrame *rayTraceOptFrame;
    QFormLayout *formLayout_2;
    QLabel *label_2;
    QRadioButton *preciseLightCurveSelector;
    QSpinBox *resolutionBox;
    QLabel *label;
    QSpinBox *frameRateBox;
    QWidget *tab_2;
    QVBoxLayout *verticalLayout_2;
    QCheckBox *animateSelector;
    QFrame *animateOptionsPane;
    QFormLayout *formLayout;
    QCheckBox *displayStarsSelector;
    QCheckBox *traceQuasarSelector;
    QCheckBox *colorImgsSelector;
    QCheckBox *showImgPaneSelector;
    QFrame *line_2;
    QFrame *frame;
    QHBoxLayout *horizontalLayout;
    QDialogButtonBox *okCancel;

    void setupUi(QDialog *Dialog)
    {
        if (Dialog->objectName().isEmpty())
            Dialog->setObjectName(QStringLiteral("Dialog"));
        Dialog->resize(407, 292);
        verticalLayout = new QVBoxLayout(Dialog);
        verticalLayout->setObjectName(QStringLiteral("verticalLayout"));
        tabWidget = new QTabWidget(Dialog);
        tabWidget->setObjectName(QStringLiteral("tabWidget"));
        tabWidget->setEnabled(true);
        tabWidget->setUsesScrollButtons(false);
        tab_3 = new QWidget();
        tab_3->setObjectName(QStringLiteral("tab_3"));
        verticalLayout_3 = new QVBoxLayout(tab_3);
        verticalLayout_3->setObjectName(QStringLiteral("verticalLayout_3"));
        rayTraceSelector = new QCheckBox(tab_3);
        rayTraceSelector->setObjectName(QStringLiteral("rayTraceSelector"));

        verticalLayout_3->addWidget(rayTraceSelector);

        rayTraceOptFrame = new QFrame(tab_3);
        rayTraceOptFrame->setObjectName(QStringLiteral("rayTraceOptFrame"));
        rayTraceOptFrame->setFrameShape(QFrame::StyledPanel);
        rayTraceOptFrame->setFrameShadow(QFrame::Raised);
        formLayout_2 = new QFormLayout(rayTraceOptFrame);
        formLayout_2->setObjectName(QStringLiteral("formLayout_2"));
        label_2 = new QLabel(rayTraceOptFrame);
        label_2->setObjectName(QStringLiteral("label_2"));

        formLayout_2->setWidget(0, QFormLayout::LabelRole, label_2);

        preciseLightCurveSelector = new QRadioButton(rayTraceOptFrame);
        preciseLightCurveSelector->setObjectName(QStringLiteral("preciseLightCurveSelector"));

        formLayout_2->setWidget(2, QFormLayout::LabelRole, preciseLightCurveSelector);

        resolutionBox = new QSpinBox(rayTraceOptFrame);
        resolutionBox->setObjectName(QStringLiteral("resolutionBox"));
        resolutionBox->setMinimum(50);
        resolutionBox->setMaximum(10000);
        resolutionBox->setSingleStep(50);
        resolutionBox->setValue(200);

        formLayout_2->setWidget(1, QFormLayout::LabelRole, resolutionBox);

        label = new QLabel(rayTraceOptFrame);
        label->setObjectName(QStringLiteral("label"));

        formLayout_2->setWidget(3, QFormLayout::LabelRole, label);

        frameRateBox = new QSpinBox(rayTraceOptFrame);
        frameRateBox->setObjectName(QStringLiteral("frameRateBox"));
        frameRateBox->setMinimum(5);
        frameRateBox->setMaximum(100);
        frameRateBox->setSingleStep(5);
        frameRateBox->setValue(15);

        formLayout_2->setWidget(4, QFormLayout::LabelRole, frameRateBox);


        verticalLayout_3->addWidget(rayTraceOptFrame);

        tabWidget->addTab(tab_3, QString());
        tab_2 = new QWidget();
        tab_2->setObjectName(QStringLiteral("tab_2"));
        tab_2->setEnabled(true);
        verticalLayout_2 = new QVBoxLayout(tab_2);
        verticalLayout_2->setObjectName(QStringLiteral("verticalLayout_2"));
        animateSelector = new QCheckBox(tab_2);
        animateSelector->setObjectName(QStringLiteral("animateSelector"));

        verticalLayout_2->addWidget(animateSelector);

        animateOptionsPane = new QFrame(tab_2);
        animateOptionsPane->setObjectName(QStringLiteral("animateOptionsPane"));
        animateOptionsPane->setFrameShape(QFrame::StyledPanel);
        animateOptionsPane->setFrameShadow(QFrame::Raised);
        formLayout = new QFormLayout(animateOptionsPane);
        formLayout->setObjectName(QStringLiteral("formLayout"));
        displayStarsSelector = new QCheckBox(animateOptionsPane);
        displayStarsSelector->setObjectName(QStringLiteral("displayStarsSelector"));

        formLayout->setWidget(1, QFormLayout::FieldRole, displayStarsSelector);

        traceQuasarSelector = new QCheckBox(animateOptionsPane);
        traceQuasarSelector->setObjectName(QStringLiteral("traceQuasarSelector"));

        formLayout->setWidget(2, QFormLayout::FieldRole, traceQuasarSelector);

        colorImgsSelector = new QCheckBox(animateOptionsPane);
        colorImgsSelector->setObjectName(QStringLiteral("colorImgsSelector"));

        formLayout->setWidget(0, QFormLayout::FieldRole, colorImgsSelector);

        showImgPaneSelector = new QCheckBox(animateOptionsPane);
        showImgPaneSelector->setObjectName(QStringLiteral("showImgPaneSelector"));

        formLayout->setWidget(3, QFormLayout::FieldRole, showImgPaneSelector);


        verticalLayout_2->addWidget(animateOptionsPane);

        line_2 = new QFrame(tab_2);
        line_2->setObjectName(QStringLiteral("line_2"));
        line_2->setFrameShape(QFrame::HLine);
        line_2->setFrameShadow(QFrame::Sunken);

        verticalLayout_2->addWidget(line_2);

        tabWidget->addTab(tab_2, QString());

        verticalLayout->addWidget(tabWidget);

        frame = new QFrame(Dialog);
        frame->setObjectName(QStringLiteral("frame"));
        frame->setFrameShape(QFrame::StyledPanel);
        frame->setFrameShadow(QFrame::Raised);
        horizontalLayout = new QHBoxLayout(frame);
        horizontalLayout->setObjectName(QStringLiteral("horizontalLayout"));
        okCancel = new QDialogButtonBox(frame);
        okCancel->setObjectName(QStringLiteral("okCancel"));
        okCancel->setOrientation(Qt::Horizontal);
        okCancel->setStandardButtons(QDialogButtonBox::Cancel|QDialogButtonBox::Ok);

        horizontalLayout->addWidget(okCancel);


        verticalLayout->addWidget(frame);


        retranslateUi(Dialog);
        QObject::connect(okCancel, SIGNAL(accepted()), Dialog, SLOT(accept()));
        QObject::connect(rayTraceSelector, SIGNAL(clicked(bool)), animateSelector, SLOT(setEnabled(bool)));
        QObject::connect(okCancel, SIGNAL(rejected()), Dialog, SLOT(reject()));
        QObject::connect(animateSelector, SIGNAL(clicked(bool)), animateOptionsPane, SLOT(setEnabled(bool)));
        QObject::connect(rayTraceSelector, SIGNAL(clicked(bool)), rayTraceOptFrame, SLOT(setEnabled(bool)));

        tabWidget->setCurrentIndex(0);


        QMetaObject::connectSlotsByName(Dialog);
    } // setupUi

    void retranslateUi(QDialog *Dialog)
    {
        Dialog->setWindowTitle(QApplication::translate("Dialog", "Dialog", 0));
        rayTraceSelector->setText(QApplication::translate("Dialog", "Ray-Trace System upon Initialization", 0));
        label_2->setText(QApplication::translate("Dialog", "Light Curve Resolution", 0));
        preciseLightCurveSelector->setText(QApplication::translate("Dialog", "Precise Light Curve Generation", 0));
        label->setText(QApplication::translate("Dialog", "Export Frame Rate", 0));
        tabWidget->setTabText(tabWidget->indexOf(tab_3), QApplication::translate("Dialog", "General", 0));
        animateSelector->setText(QApplication::translate("Dialog", "Animate", 0));
        displayStarsSelector->setText(QApplication::translate("Dialog", "Display Stars", 0));
        traceQuasarSelector->setText(QApplication::translate("Dialog", "Display Quasar Icon on Magnification Map", 0));
        colorImgsSelector->setText(QApplication::translate("Dialog", "Color Minima/Saddle Points", 0));
        showImgPaneSelector->setText(QApplication::translate("Dialog", "Show Starfield Image Pane", 0));
        tabWidget->setTabText(tabWidget->indexOf(tab_2), QApplication::translate("Dialog", "Animation Preferences", 0));
    } // retranslateUi

};

namespace Ui {
    class Dialog: public Ui_Dialog {};
} // namespace Ui

QT_END_NAMESPACE

#endif // UI_PREFERENCESDIALOG_H
