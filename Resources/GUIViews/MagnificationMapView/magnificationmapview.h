#ifndef MAGNIFICATIONMAPVIEW_H
#define MAGNIFICATIONMAPVIEW_H

#include <QWidget>

namespace Ui {
class MagnificationMapView;
}

class MagnificationMapView : public QWidget
{
    Q_OBJECT

public:
    explicit MagnificationMapView(QWidget *parent = 0);
    ~MagnificationMapView();

private:
    Ui::MagnificationMapView *ui;
};

#endif // MAGNIFICATIONMAPVIEW_H
