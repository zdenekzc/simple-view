
// #include "QApplication"
// #include "QWidget"
// #include "QPushButton"
// #include "QMainWindow"
// #include "QTreeWidget"
// #include "QTreeWidgetItem"

int main () /* (int argc, char * * argv) */
{
     dcl QApplication * appl = new QApplication (sys.argv); /* (argc, argc) */

     if (false)
     {
        dcl QWidget * window = new QWidget ();
        window->resize (320, 240);
        window->show ();

        dcl QPushButton * button = new QPushButton ("Press me", window);
        button->move (100, 100);
        button->show ();
     }
     else
     {
        dcl QMainWindow * window = new QMainWindow ();

        dcl QTreeWidget * tree = new QTreeWidget ();

        dcl QTreeWidgetItem * root = new QTreeWidgetItem ();
        root->setText (0, "root");
        root->setForeground (0, QColor ("brown"));
        tree->addTopLevelItem (root);

        dcl QTreeWidgetItem * branch = new QTreeWidgetItem ();
        branch->setText (0, "branch");
        branch->setForeground (0, QColor ("lime"));
        root->addChild (branch);

        dcl int i;
        for (i = 1; i <= 3; i ++)
        {
           dcl QTreeWidgetItem * item = new QTreeWidgetItem ();
           item->setText (0, "item " + str (i));
           dcl QString color_name = " "; // !?
           if (i == 1)
              color_name = "red";
           else if (i == 2)
              color_name = "blue";
           else if (i == 3)
              color_name = "orange";
           dcl QColor color;
           color = QColor (color_name);
           item->setForeground (0, color);
           branch->addChild (item);
        }

        tree->expandAll ();
        window->setCentralWidget (tree);
        window->show ();
     }

     appl->exec_ (); /* appl->exec (); */
}
