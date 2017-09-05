CONFIG      += plugin debug_and_release
TARGET      = $$qtLibraryTarget(viewsplugin)
TEMPLATE    = lib

HEADERS     = parametersviewplugin.h imgoptionsviewplugin.h lightcurveoptionsviewplugin.h magmapoptionsviewplugin.h views.h
SOURCES     = parametersviewplugin.cpp imgoptionsviewplugin.cpp lightcurveoptionsviewplugin.cpp magmapoptionsviewplugin.cpp views.cpp
RESOURCES   = icons.qrc
LIBS        += -L. 

greaterThan(QT_MAJOR_VERSION, 4) {
    QT += designer
} else {
    CONFIG += designer
}

target.path = $$[QT_INSTALL_PLUGINS]/designer
INSTALLS    += target

include(parametersview.pri)
include(magmapoptionsview.pri)
include(lightcurveoptionsview.pri)
include(imgoptionsview.pri)
