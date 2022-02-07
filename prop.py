#!/usr/bin/env python

from __future__ import print_function

import sys
import inspect

from util import use_pyside2, use_qt5, use_simple
if use_pyside2 :
   from PySide2.QtCore import *
   from PySide2.QtGui import *
   from PySide2.QtWidgets import *
elif use_qt5 :
   from PyQt5.QtCore import *
   from PyQt5.QtGui import *
   from PyQt5.QtWidgets import *
else :
   from PyQt4.QtCore import *
   from PyQt4.QtGui import *

from util import color_map

# --------------------------------------------------------------------------

# class DataObject
#
#    _only_properties_
#    _properties_
#    link_obj
#

# --------------------------------------------------------------------------

class ItemEditor (QWidget) :
    def __init__ (self, parent = None) :
        super (ItemEditor, self).__init__ (parent)

        self.line_edit = None
        self.combo_box = None
        self.button = None

# --------------------------------------------------------------------------

class ListDelegate (QItemDelegate):

    def __init__ (self, parent=None) :
        super (ListDelegate, self).__init__ (parent)

    def createEditor(self, parent, option, index) :
        editor = ItemEditor (parent)

        layout =  QHBoxLayout (editor)
        layout.setMargin (0)
        layout.setSpacing (0)
        editor.setLayout (layout)

        if True :
           editor.combo_box = QComboBox (editor)
           layout.addWidget (editor.combo_box)
           editor.combo_box.addItems (["abc", "def", "klm"])
        else :
           editor.line_edit = QLineEdit (editor)
           layout.addWidget (editor.line_edit)

        if True :
           print ("Button ...")
           editor.button = QPushButton (editor)
           editor.button.setText ("...")
           editor.button.setMaximumWidth (32)
           layout.addWidget (editor.button)

        return editor

    def setEditorData (self, editor, index) :
        text = index.model().data(index, Qt.DisplayRole).toString()
        if editor.combo_box != None :
           i = editor.combo_box.findText (text)
           if i == -1:
              i = 0
           editor.combo_box.setCurrentIndex (i)

    def setModelData (self, editor, model, index) :
        if editor.combo_box != None :
           model.setData (index, editor.combo_box.currentText())

# --------------------------------------------------------------------------

class Property (QTableWidget) :

   def __init__ (self, win=None, browser=None) :
       super (Property, self).__init__ (win)
       self.win = win
       self.browser = browser
       self.data = None

       self.setColumnCount (2)
       self.setRowCount (6)
       self.setHorizontalHeaderLabels (["Name", "Value"])
       self.horizontalHeader().setStretchLastSection (True)
       self.verticalHeader().setVisible (False)

       self.setContextMenuPolicy (Qt.CustomContextMenu)
       self.customContextMenuRequested.connect (self.onContextMenu)

       header = self.horizontalHeader()
       header.setContextMenuPolicy (Qt.CustomContextMenu)
       header.customContextMenuRequested.connect (self.onContextMenu)

       self.setAlternatingRowColors (True)
       self.setEditTriggers (QTableWidget.AllEditTriggers)
       self.setSelectionBehavior (QTableWidget.SelectItems)
       self.setSelectionMode (QTableWidget.SingleSelection)

       # self.example ()

   def example (self) :

       # self.setItemDelegate (ListDelegate ())
       self.setItemDelegateForRow (5, ListDelegate ())

       item = QTableWidgetItem ()
       item.setText ("First")
       self.setItem (0, 0, item)

       item = QTableWidgetItem ()
       item.setText ("one")
       self.setItem (0, 1, item)

       item = QTableWidgetItem ()
       item.setText ("Second")
       # item.setData (Qt.BackgroundRole, QColor ("yellow"))
       # item.setData (Qt.ForegroundRole, QColor ("blue"))
       # item.setData (Qt.FontRole, QFont ("Courier", 16))
       self.setItem (1, 0, item)

       item = QTableWidgetItem ()
       item.setText ("two")
       # item.setData (Qt.EditRole, QColor ("yellow"))
       item.setData (Qt.DecorationRole, QColor ("yellow"))
       item.setData (Qt.CheckStateRole, Qt.Checked)
       self.setItem (1, 1, item)

       item = QTableWidgetItem ()
       item.setText ("Boolean")
       self.setItem (2, 0, item)

       item = QTableWidgetItem ()
       # item.setData (Qt.EditRole, QVariant (True))
       item.setData (Qt.EditRole, True)
       self.setItem (2, 1, item)

       item = QTableWidgetItem ()
       item.setText ("Integer")
       self.setItem (3, 0, item)

       item = QTableWidgetItem ()
       item.setData (Qt.EditRole, 1)
       item.setData (Qt.DisplayRole, 100)
       self.setItem (3, 1, item)

       item = QTableWidgetItem ()
       item.setText ("Double")
       self.setItem (4, 0, item)

       item = QTableWidgetItem ()
       item.setData (Qt.EditRole, 3.14)
       self.setItem (4, 1, item)

       item = QTableWidgetItem ()
       item.setText ("List")
       self.setItem (5, 0, item)

       item = QTableWidgetItem ()
       item.setData (Qt.EditRole, QColor ("yellow"))
       item.setData (Qt.EditRole, "klm")
       self.setItem (5, 1, item)

   def showProperty (self, inx, key, value) :

       if isinstance (key, QByteArray) :
          key = str (key)

       link_value = None
       if value != None and not isinstance (value, int) and not isinstance(value, float) and not isinstance (value, str) :
          link_value = value

       item = QTableWidgetItem ()
       item.setText (key)
       item.link_obj = link_value
       item.setFlags (item.flags () & ~ Qt.ItemIsEditable)
       self.setItem (inx, 0, item)

       item = QTableWidgetItem ()
       item.setText (str (value))
       item.link_obj = link_value
       self.setItem (inx, 1, item)

       if isinstance (value, QVariant) :
          value = value.toString();
          item.setText (value) # again

       if isinstance (value, QPen) :
          value = value.color ()
       #if isinstance (value, QBrush) :
          value = value.color ()
       if isinstance (value, QColor) :
          item.setData (Qt.DecorationRole, value)
          text = value.name ()
          for name in color_map :
             if color_map [name] == value :
                text = name
          item.setText (text) # again
       if isinstance (value, bool) :
          if value :
             state = Qt.Checked
          else :
             state = Qt.Unchecked
          item.setData (Qt.CheckStateRole, state)

       if isinstance (value, dict) :
          txt = "";
          for k in value :
             if len (txt) != 0 :
                txt = txt + ", "
             txt = txt + str (k)
          txt = "{ " + txt + " }"
          item.setText (txt) # again

       if inspect.isfunction (value) :
          text = item.text ()
          text = text + " " + str (inspect.signature (value))
          item.setText (text) # again

   def showDictionary (self, data) :
       cnt = len (data.keys ())
       self.setRowCount (cnt)
       inx = 0
       for key in data :
           self.showProperty (inx, key, data [key])
           inx = inx + 1

   def showList (self, data) :
       cnt = len (data)
       self.setRowCount (cnt)
       inx = 0
       for value in data :
           self.showProperty (inx, str (inx), value)
           inx = inx + 1

   def showQtProperties (self, data) :
       typ = data.metaObject ()
       cnt = typ.propertyCount ()
       self.setRowCount (cnt)
       for inx in range (cnt) :
           prop = typ.property (inx)
           name = prop.name ()
           value = prop.read (data)
           self.showProperty (inx, name, value)

   def showClass (self, data) :
       prop = { }

       if hasattr (data, "_only_properties_") : # !?
          for key in data._only_properties_ :
              value = getattr (data, key)
              prop [key] = value

       else :

          if hasattr (data, "__dict__") :
             for key in data.__dict__ :
                 value = data.__dict__ [key]
                 prop [key] = value

          if hasattr (data, "_properties_") :
             for key in data._properties_ :
                 value = getattr (data, key)
                 value = value ()
                 prop [key] = value

       last = [ "src_file", "src_line", "src_column", "src_pos", "src_end",
                "region_begin", "region_end", "region_begin_file", "region_end_file",
                "item_icon", "item_ink", "item_paper", "item_tooltip",
                "item_expand", "item_transparent",
                "item_name", "item_context", "item_qual",
                "item_dict", "item_list",
                "item_decl", "item_type", "item_value", "item_body",
                "item_code", "item_code_decl", "item_place",
                "item_ref", "item_label", "item_block",
                "jump_table", "jump_label",
                "type_name", "type_decl", "type_args", "type_from",
                "type_const", "type_volatile", "type_signed", "type_unsigned",
                "type_void", "type_bool", "type_char", "type_wchar",
                "type_short", "type_int", "type_long", "type_float", "type_double",
                "alt_assign",
                "alt_connect", "alt_connect_dcl", "alt_connect_signal",
                "alt_create", "alt_create_owner", "alt_create_place",
                "alt_ignore",
                "alt_setup", "alt_setup_param",
                "attr_compile_time", "attr_field", "attr_context" ]

       names = [ ]

       keys = prop.keys ()
       # keys.sort () # exception in Python 3
       keys = sorted (keys)
       for key in keys :
          if key not in last :
             names.append (key)

       for key in last :
           if key in keys :
              names.append (key)

       cnt = len (names)
       self.setRowCount (cnt)
       inx = 0
       for key in names :
           value = prop [key]
           self.showProperty (inx, key, value)
           inx = inx + 1

   def showText (self, data) :
       cnt = 1
       self.setRowCount (cnt)
       inx = 0
       self.showProperty (inx, "", str (data))

   def showObject (self, data) :
       if data != None :
          if isinstance (data, list) :
             self.showList (data)
          elif isinstance (data, dict) :
             self.showDictionary (data)
          elif isinstance (data, QColor) :
             self.showText (data)
          elif hasattr (data, "_only_properties_") : # !?
             self.showClass (data)
          # elif hasattr (data, "metaObject") and not hasattr (data, "__bases__") :
          #   self.showQtProperties (data)
          else :
             self.showClass (data)

   def showProperties (self, data) :
       self.data = data
       self.showObject (data)

   def changeObject (self, data) :
       if self.browser == None :
          ObjectBrowser (self.win, data) # create new object browser
       else :
          self.browser.changeObject (data)

   def mousePressEvent (self, e) :
       mask = Qt.ShiftModifier | Qt.ControlModifier | Qt.AltModifier | Qt.MetaModifier
       mod = int (e.modifiers () & mask)
       button = e.button ()

       if mod == Qt.ControlModifier and button == Qt.LeftButton:
          # print ("CTRL CLICK")
          item = self.itemAt (e.pos ())
          if item != None :
             obj = getattr (item, "link_obj", None)
             if obj != None :
                self.changeObject (obj)

       if mod == Qt.ControlModifier + Qt.ShiftModifier :
          # print ("CTRL SHIFT CLICK")
          if self.browser == None :
             self.changeObject (self.data)

   def onContextMenu (self, pos) :
       item = self.itemAt (pos)
       menu = QMenu (self)
       any = False

       if self.browser == None :
          act = menu.addAction ("show this object")
          act.triggered.connect (lambda param, self=self, data=self.data: self.changeObject (data))
          any = True

       if getattr (item, "link_obj", None) != None :
          act = menu.addAction ("show this item")
          act.triggered.connect (lambda param, self=self, data=item.link_obj: self.changeObject (data))
          any = True

       if any :
          menu.exec_ (self.mapToGlobal (QPoint (pos)))

# --------------------------------------------------------------------------

class ObjectBrowser (QDialog) :

   def __init__ (self, win = None, data = None) :
       super (ObjectBrowser, self).__init__ (win)
       self.win = win

       self.treeView = QTreeWidget ()
       self.treeView.currentItemChanged.connect (self.onCurrentItemChanged)
       self.treeView.setHeaderHidden (True)

       self.propView = Property (win = self, browser = self)

       self.splitter = QSplitter ()
       self.splitter.addWidget(self.treeView)
       self.splitter.addWidget(self.propView)
       self.splitter.setStretchFactor (0, 1)
       self.splitter.setStretchFactor (1, 2)

       self.layout = QVBoxLayout ()
       self.layout.addWidget (self.splitter)
       self.setLayout (self.layout)

       self.setWindowTitle ("Object browser")
       self.changeObject (data)

       if not use_simple :
          self.resize (400, 520)
       self.show ()

   def onCurrentItemChanged(self, current, previous) :
       self.propView.showProperties (current.data)

   def changeObject (self, data) :

       target = self.treeView.currentItem ()
       if target != None :
          node = QTreeWidgetItem (target)
          target.setExpanded (True)
       else :
          node = QTreeWidgetItem (self.treeView)

       text = str (data)
       if text.find ("\n") >= 0 :
          text = " ".join (text.splitlines ())
       if text == "" :
          text = "object"

       type_info = str (type (data))
       text = text + " : " +  type_info

       node.setText (0, text)
       node.setToolTip (0, type_info)
       node.data = data
       self.treeView.setCurrentItem (node)

       self.propView.showProperties (data)

# --------------------------------------------------------------------------

if __name__ == '__main__' :
   app = QApplication (sys.argv)
   window = Property ()
   window.show ()
   app.exec_ ()

# --------------------------------------------------------------------------

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
