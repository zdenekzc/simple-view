
// #include "QApplication"
// #include "QPushButton"

class MyWindow : public QWidget
{
public:
    QPushButton * button
    {
        text = "Button";
        move (100, 100);
        clicked () { text = "Click"; }
    }

    MyWindow ()
    {
        resize (320, 240);
        show ();
    }
};

int main (int argc, char * * argv)
{
     QApplication * appl = new QApplication (argc, argv);
     MyWindow * window = new MyWindow;
     window->show ();
     appl->exec ();
}

// kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
