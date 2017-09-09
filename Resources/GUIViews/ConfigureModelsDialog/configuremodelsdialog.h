#ifndef CONFIGUREMODELSDIALOG_H
#define CONFIGUREMODELSDIALOG_H

#include <QDialog>

namespace Ui {
class ConfigureModelsDialog;
}

class ConfigureModelsDialog : public QDialog
{
    Q_OBJECT

public:
    explicit ConfigureModelsDialog(QWidget *parent = 0);
    ~ConfigureModelsDialog();

private:
    Ui::ConfigureModelsDialog *ui;
};

#endif // CONFIGUREMODELSDIALOG_H
