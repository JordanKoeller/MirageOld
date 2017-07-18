#ifndef TRACERWINDOW_H
#define TRACERWINDOW_H

#include <QMainWindow>

namespace Ui {
class TracerWindow;
}

class TracerWindow : public QMainWindow
{
    Q_OBJECT

public:
    explicit TracerWindow(QWidget *parent = 0);
    ~TracerWindow();

private:
    Ui::TracerWindow *ui;
};

#endif // TRACERWINDOW_H
