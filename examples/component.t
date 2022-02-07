
class Item : QLineEdit
{
    public:
       QString value;
};

class Simple : public QPushButton
{
    public:
       bool b;
       char c;
       wchar_t w;
       short s;
       int i;
       long l;
       unsigned int u;
       unsigned long v;
       float f;
       double d;
       string s;
       QString t = "text";

       void add (Item p) { } // !?

};

class Example : public QMainWindow
{
   // this->setWindowTitle ("Example");
   QMenuBar * mainMenu
   {
       QMenu * file
       {
           title = "&File";
           QAction * quit
           {
               text = "&Quit";
               shortcut = "Ctrl+Q";
               triggered () { this->close (); }
           }
       }
   }
   QToolBar * toolbar
   {
       QToolButton * tool_button
       {
           text = "first";
           icon = "weather-clear";
       }
       QToolButton * tool_button_2
       {
           text = "second";
           icon = "applications-toys";
       }
   }

   QVBoxLayout * vlayout
   {
      QHBoxLayout * hlayout
      {
         QPushButton * button
         {
            text = "Abc";
            clicked () { text = "Click"; }
         }
         QCheckBox * check_box
         {
            text = "Check";
            toggled () { if (isChecked ()) text = "On"; else text = "Off"; }
         }
         QLineEdit * edit
         {
            text = "Edit";
         }
      }
      QTreeWidget * tree
      {
         QTreeWidgetItem * branch
         {
            QTreeWidgetItem * node1 { text = "red"; foreground = "red"; }
            QTreeWidgetItem * node2 { text = "green"; foreground = "green"; }
            QTreeWidgetItem * node3 { text = "blue"; foreground = "blue"; }

            text = "tree branch";
            foreground = "brown";
            background = "orange";
            icon = "folder";
            // expanded = true;
         }
         // expandAll ();
      }
   }
   QStatusBar * status
   {
       QLabel * lab
       {
          text = "status bar";
       }
   }
};

int main (int argc, char * * argv)
{
     QApplication * appl = new QApplication (argc, argv);
     QIcon::setThemeName ("oxygen");
     Example * window = new Example;
     window->tree->expandAll ();
     window->show ();
     appl->exec ();
}

// kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
