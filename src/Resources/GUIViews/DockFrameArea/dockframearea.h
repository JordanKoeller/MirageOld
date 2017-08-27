#ifndef DOCKFRAMEAREA_H
#define DOCKFRAMEAREA_H

#include <QMainWindow>

namespace Ui {
class DockFrameArea;
}

class DockFrameArea : public QMainWindow
{
    Q_OBJECT

public:
    explicit DockFrameArea(QWidget *parent = 0);
    ~DockFrameArea();

private:
    Ui::DockFrameArea *ui;
};

#endif // DOCKFRAMEAREA_H
