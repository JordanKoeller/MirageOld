#ifndef BATCHTABLEVIEW_H
#define BATCHTABLEVIEW_H

#include <QWidget>

namespace Ui {
class BatchTableView;
}

class BatchTableView : public QWidget
{
    Q_OBJECT

public:
    explicit BatchTableView(QWidget *parent = 0);
    ~BatchTableView();

private:
    Ui::BatchTableView *ui;
};

#endif // BATCHTABLEVIEW_H
