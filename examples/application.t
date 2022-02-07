
// #include "QApplication"
// #include "QWidget"
// #include "QPushButton"
// #include "QMainWindow"
// #include "QTreeWidget"
// #include "QTreeWidgetItem"

int main (int argc, char * * argv)
{
     QApplication * appl = new QApplication (argc, argv);

     if (false)
     {
        QWidget * window = new QWidget;
        window->resize (320, 240);
        window->show ();

        QPushButton * button = new QPushButton ("Press me", window);
        button->move (100, 100);
        button->show ();
     }
     else
     {
        QMainWindow * window = new QMainWindow;

        QTreeWidget * tree = new QTreeWidget;

        QTreeWidgetItem * root = new QTreeWidgetItem;
        root->setText (0, "root");
        root->setForeground (0, QColor ("brown"));
        tree->addTopLevelItem (root);

        QTreeWidgetItem * branch = new QTreeWidgetItem;
        branch->setText (0, "branch");
        branch->setForeground (0, QColor ("lime"));
        root->addChild (branch);

        for (int i = 1; i <= 3; i += 1)
        {
           QTreeWidgetItem * item = new QTreeWidgetItem;
           item->setText (0, "item " + ::str (i));
           QString color_name = "";
           if (i == 1)
              color_name = "red";
           else if (i == 2)
              color_name = "blue";
           else if (i == 3)
              color_name = "orange";
           QColor color = QColor (color_name);
           item->setForeground (0, color);
           branch->addChild (item);
        }

        tree->expandAll ();
        window->setCentralWidget (tree);
        window->show ();
     }

     appl->exec ();
}
