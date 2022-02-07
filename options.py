#!/usr/bin/env python

from __future__ import print_function

import sys, os, re

from util import import_qt_modules
import_qt_modules (globals ())

from util import findColor, findIcon, use_new_api, use_new_qt, qstring_to_str, variant_to_str, setResizeMode

import util

from prop import ObjectBrowser

# --------------------------------------------------------------------------

class OptionsBox (QWidget) :
   def __init__ (self) :
       super (OptionsBox, self).__init__ ()
       self.tab_layout = QVBoxLayout ()
       self.setLayout (self.tab_layout)

   def addWidgetItem (self, widget) :
       self.tab_layout.addWidget (widget)

   def addLayoutItem (self, layout) :
       self.tab_layout.addLayout (layout)

# --------------------------------------------------------------------------

class OptionsLineEditBox (QHBoxLayout) :
   def __init__ (self, win, dlg, settings_id, title, default_value, file_dialog = False) :
       super (OptionsLineEditBox, self).__init__ ()
       self.win = win
       self.settings_id = settings_id

       self.label = QLabel ()
       self.label.setText (title)

       self.edit = QLineEdit ()

       self.addWidget (self.label)
       self.addWidget (self.edit)

       self.button = None
       if file_dialog :
          self.button = QPushButton ()
          self.button.setText ("...")
          self.addWidget (self.button)
          self.button.clicked.connect (self.buttonClick)

       # recall value
       value = self.win.settings.string (settings_id)
       if value == "" :
          value = default_value
          self.win.settings.setValue (settings_id, value) # write default value to .ini file
       self.edit.setText (value)

       dlg.accepted.connect (self.storeValue)

   def buttonClick (self) :
       value = str (QFileDialog.getOpenFileName ())
       if value != "" :
          self.edit.setText (value)

   def storeValue (self) :
       value = str (self.edit.text ())
       value = value.strip ()
       self.win.settings.setValue (self.settings_id, value)

# --------------------------------------------------------------------------

class OptionDialog (QDialog) :
   def __init__ (self, win) :
       super (OptionDialog, self).__init__ (win)

       self.win = win
       self.page_count = 0
       self.current_tab = None

       "toolBar with buttons"
       self.toolBar = QToolBar ()
       self.toolBar.setOrientation (Qt.Vertical)

       "stackWidget for option pages"
       self.stackWidget = QStackedWidget ()

       "toolBar and stackWidget - central dialog area"
       self.hlayout = QHBoxLayout ()
       self.hlayout.addWidget (self.toolBar)
       self.hlayout.addWidget (self.stackWidget)

       self.buttonBox = QDialogButtonBox (QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
       self.buttonBox.accepted.connect (self.accept)
       self.buttonBox.rejected.connect (self.reject)

       "ok and cancel at the bottom"
       self.vlayout = QVBoxLayout ()
       self.vlayout.addLayout (self.hlayout)
       self.vlayout.addWidget (self.buttonBox)
       self.setLayout (self.vlayout)

   def addPage (self, name, icon, widget, create_widget = None) :

       if isinstance (icon, str) :
          icon = findIcon (icon)

       if widget != None :
          self.stackWidget.addWidget (widget)

       button = QPushButton ()
       button.setText (name)
       if icon != None :
          button.setIcon (icon)
          button.setIconSize (QSize (24, 24))
       button.setMinimumSize (80, 80)

       button.widget = widget
       button.create_widget = create_widget

       button.clicked.connect (lambda param, self=self, button=button: self.openPage (button))
       self.toolBar.addWidget (button)

   def openPage (self, button) :
       if button.create_widget != None :
          if button.widget == None  :
             button.widget = button.create_widget ()
             self.stackWidget.addWidget (button.widget)
          else :
             self.stackWidget.setCurrentWidget (button.widget) # show empty page
             self.show ()
             button.create_widget (button.widget)
          button.create_widget = None # do not call again
       self.stackWidget.setCurrentWidget (button.widget)

   def addSimplePage (self, name, icon) :
       box = OptionsBox ()
       box.win = self.win
       self.addPage (name, icon, box)
       self.current_page = None
       self.current_tab = box
       return box

   def addTabPage (self, name, icon) :
       page = QTabWidget ()
       self.addPage (name, icon, page)
       self.current_page = page
       self.current_tab = None
       return page

   def addTab (self, name) :
       box = OptionsBox ()
       box.win = self.win
       self.current_page.addTab (box, name)
       self.current_tab = box
       return box

   def addLineEdit (self, settings_id, title, default_value, file_dialog = False) :
       layout = OptionsLineEditBox (self.win, self, settings_id, title, default_value, file_dialog)
       self.current_tab.tab_layout.addLayout (layout)

# --------------------------------------------------------------------------

class Options (OptionDialog) :
   def __init__ (self, win) :
       super (Options, self).__init__ (win)

       self.setWindowTitle ("Options")

       self.examplePage1 ()
       self.examplePage2 ()

   def examplePage1 (self) :

       page = self.addTabPage  ("edit", "edit-undo")

       tab1 = self.addTab  ("first")

       edit = QLineEdit ()
       tab1.addWidgetItem (edit)

       checkBox = QCheckBox ()
       checkBox.setText ("something")
       tab1.addWidgetItem (checkBox)

       tab2 = self.addTab ("second")

   def examplePage2 (self) :
       page = self.addSimplePage ("other", "folder-new")

# --------------------------------------------------------------------------

class Notes (OptionDialog) :
   def __init__ (self, win) :
       super (Notes, self).__init__ (win)

       self.setWindowTitle ("Notes")
       self.buttonBox.setStandardButtons (QDialogButtonBox.Cancel)

       self.shortcutPage ()
       self.colorCachePage ()
       self.colorNamesPage ()
       self.iconCachePage ()
       self.pathPage ()
       self.modulePage ()
       self.toolIniPage ()
       self.iniPage ("view.ini", "clementine", self.win.settings)
       self.iniPage ("edit.ini", "tellico", self.win.session)

   # -----------------------------------------------------------------------

   def pathPage (self) :
       listView = QListWidget ()
       self.addPage ("sys path", "rosegarden", listView)
       for item in sys.path :
          listView.addItem (item)

   def modulePage (self) :
       listView = QListWidget ()
       self.addPage ("modules", "kdf", listView)
       # for item in self.win.loaded_modules :
       #    listView.addItem (item)
       for item in sorted (sys.modules) :
          listView.addItem (item)
       listView.itemDoubleClicked.connect (self.showModule)
       listView.itemClicked.connect (self.alternativeShowModule)

   def showModule (self, item) :
       name = item.text ()
       ObjectBrowser (self.win, sys.modules [name])

   def alternativeShowModule (self, item) :
       mask = Qt.ShiftModifier | Qt.ControlModifier | Qt.AltModifier | Qt.MetaModifier
       mod = int (QApplication.keyboardModifiers () & mask)
       if mod == Qt.ControlModifier :
          # print ("CTRL CLICK")
          self.showModule (item)

   # -----------------------------------------------------------------------

   def resizeFirstColumn (self, treeView) :
       setResizeMode (treeView.header(), 0, QHeaderView.ResizeToContents)

   def resizeSecondColumn (self, treeView) :
       setResizeMode (treeView.header(), 1, QHeaderView.ResizeToContents)

   def colorCachePage (self) :
       treeView = QTreeWidget (self)
       treeView.setHeaderLabels (["Name", "Value"])
       self.resizeFirstColumn (treeView)
       self.addPage ("color cache",  "color-management", treeView)

       for name in util.color_cache :
          self.displayColor (treeView, name, util.color_cache [name])

       treeView.sortByColumn (0, Qt.AscendingOrder)

   def colorNamesPage (self) :
       treeView = QTreeWidget (self)
       treeView.setHeaderLabels (["Name", "Value"])
       self.resizeFirstColumn (treeView)
       self.addPage ("color names", "gimp", treeView)

       for name in util.color_map :
          self.displayColor (treeView, name, util.color_map [name])

       treeView.sortByColumn (0, Qt.AscendingOrder)

   def displayColor (self, branch, name, color) :
       node = QTreeWidgetItem (branch)
       node.setText (0, name)
       node.setToolTip (0, name)
       if color.lightness () < 220 and color.alpha () != 0 :
          node.setForeground (0, color)
       node.setData (0, Qt.DecorationRole, color)
       node.setText (1, str (color.red ()) + ", " + str (color.green ())+ ", " + str (color.blue ()))

   # -----------------------------------------------------------------------

   def iconCachePage (self) :
       treeView = QTreeWidget (self)
       self.addPage ("icon cache", "choqok", treeView)

       for name in util.icon_cache :
           icon = util.icon_cache [name]
           self.displayIcon (treeView, name, icon)

       treeView.sortByColumn (0, Qt.AscendingOrder)

   def displayIcon (self, branch, name, icon) :
       node = QTreeWidgetItem (branch)
       node.setText (0, name)
       node.setToolTip (0, name)
       node.setIcon (0, icon)

   # -----------------------------------------------------------------------

   def iniPage (self, name, icon, ini) :
       treeView = QTreeWidget (self)
       treeView.setHeaderLabels (["Name", "Value"])
       self.resizeFirstColumn (treeView)
       self.addPage (name, icon, treeView)
       for group in ini.childGroups () :
           branch = QTreeWidgetItem (treeView)
           branch.setText (0, "[" + group + "]")
           branch.setIcon (0, findIcon ("folder"))
           ini.beginGroup (group)
           for key in ini.childKeys () :
               value = ini.value (key)
               item = QTreeWidgetItem (branch)
               item.setText (0, key)
               item.setText (1, variant_to_str (value))
           ini.endGroup ()

   # -----------------------------------------------------------------------

   def toolIniPage (self) :
       treeView = QTreeWidget (self)
       treeView.setHeaderLabels (["Name", "Value"])
       self.resizeFirstColumn (treeView)
       self.addPage ("tools.ini", "tools-wizard", treeView)
       ini = self.win.commands
       section = None
       start = ""
       for group in ini.childGroups () :
           m = re.match ("(\w\w*)-.*", group)
           if m :
              new_start = m.group (1)
              if new_start != start :
                 start = new_start
                 section = QTreeWidgetItem (treeView)
                 section.setText (0, start);
                 section.setIcon (0, findIcon ("folder-yellow"))
              branch = QTreeWidgetItem (section)
           else :
              start = ""
              section = None
              branch = QTreeWidgetItem (treeView)

           branch.setText (0, "[" + group + "]")
           branch.setIcon (0, findIcon ("folder"))
           ini.beginGroup (group)
           for key in ini.childKeys () :
               value = ini.value (key)
               item = QTreeWidgetItem (branch)
               item.setText (0, key)
               item.setText (1, variant_to_str (value))
           ini.endGroup ()

# --------------------------------------------------------------------------

   def shortcutPage (self) :

       treeView = QTreeWidget ()
       treeView.setHeaderLabels (["Name", "Shortcut", "Invisible"])
       self.name_column = 0
       self.key_column = 1
       self.invisible_column = 2
       self.resizeFirstColumn (treeView)
       self.resizeSecondColumn (treeView)
       header = treeView.header ()
       header.hideSection (self.invisible_column)
       # name_column = 0
       # header.setSectionResizeMode (name_column, QHeaderView.ResizeToContents)
       self.addPage ("shortcuts", "key-enter", treeView)

       for item in self.win.menuBar().actions() :
           self.displayMainMenuAction (treeView, item)
           prefix = "Menu " + item.text () + " / "
           for action in item.menu().actions() :
               self.displayAction (treeView, action, prefix)

       for action in self.win.actions() :
           self.showItem (branch, action)
       for item in self.win.children() :
           if isinstance (item, QShortcut) :
              self.displayShortcut (treeView, item)

       inx = treeView.topLevelItemCount () - 1
       while inx > 0 :
          item = treeView.topLevelItem (inx)
          if item.text (1) == "" :
             treeView.takeTopLevelItem (inx)
          inx = inx - 1

       self.setKeys (treeView)
       treeView.sortByColumn (self.invisible_column, Qt.AscendingOrder)

   def displayMainMenuAction (self, treeView, item) :
       node = QTreeWidgetItem (treeView)
       text = str (item.text ())
       node.setText (self.name_column, "Menu " +text)
       inx = text.find ('&')
       if inx >= 0 and inx+1 < len (text) :
          c = text [inx+1]
          node.setText (1, "Alt+" + c.upper ())
       icon  = item.icon ()
       node.setIcon (self.name_column, icon)

   def displayAction (self, treeView, action, prefix = "") :
       for shortcut in action.shortcuts () :
           node = QTreeWidgetItem (treeView)
           node.setText (self.name_column, prefix + action.text())
           node.setIcon (self.name_column, action.icon ())
           node.setText (self.key_column,  self.keySequenceToString (shortcut))

   def displayShortcut (self, treeView, shortcut) :
       node = QTreeWidgetItem (treeView)
       node.setText (self.name_column, shortcut.objectName ())
       node.setText (self.key_column,  self.keySequenceToString (shortcut.key()))

   def keySequenceToString (self, shortcut) :
       text = shortcut.toString ()
       text = qstring_to_str (text)
       text = text.replace ("Meta+", "Win+")
       return text

   def setKeys (self, treeView) :
       cnt = treeView.topLevelItemCount ()
       for inx in range (cnt) :
          item = treeView.topLevelItem (inx)
          text = str (item.text (self.key_column))

          key = "T"
          if text == "" :
             key = "Z"

          if text.startswith ("Win+") :
             key = key + "W"
             text = text [4:]
          else :
             key = key + "Z"

          if text.startswith ("Alt+") :
             key = key + "A"
             text = text [4:]
          else :
             key = key + "Z"

          if text.startswith ("Ctrl+") :
             key = key + "C"
             text = text [5:]
          else :
             key = key + "Z"

          if text.startswith ("Shift+") :
             key = key + "S"
             text = text [6:]
          else :
             key = key + "Z"

          if text == "Left" :
             key = key + "a"
          elif text == "Right" :
             key = key + "b"
          elif text == "Up" :
             key = key + "c"
          elif text == "Down" :
             key = key + "d"
          elif text == "Ins" :
             key = key + "e"
          elif text == "Del" :
             key = key + "f"
          elif text == "Home" :
             key = key + "g"
          elif text == "End" :
             key = key + "h"
          elif text == "PgUp" :
             key = key + "i"
          elif text == "PgDown" :
             key = key + "j"
          elif text.startswith ("F") and len (text) > 1 :
             if len (text) == 2 :
                key = key + "l"
             else :
                key = key + "m"
          elif len (text) > 1 :
             key = key + "k" # before F1 and F10
          elif text >= "0" and text <= "9":
             key = key + "o"
          elif text >= "A" and text <= "Z":
             key = key + "p"
          else:
             key = key + "n" # before digits

          key = key + text
          item.setText (self.invisible_column, key)

# --------------------------------------------------------------------------

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
