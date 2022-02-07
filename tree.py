#!/usr/bin/env python

from __future__ import print_function

import os, sys

from util import use_pyside2, use_qt5
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

from util import findColor, findIcon, bytearray_to_str

from input import indexToFileName

# --------------------------------------------------------------------------

# class TreeItem
#
#    src_file
#    src_line
#    src_column
#    src_pos
#    src_end
#
#    expand_func
#    expand_data
#
#    obj

# --------------------------------------------------------------------------

# class TreeDataObject
#
#    region_begin
#    region_end
#    region_begin_file
#    region_end_file
#
#    item_icon
#    item_ink
#    item_paper
#    item_tooltip
#
#    item_expand
#    item_transparent
#
#    item_name
#    item_context
#    item_qual
#
#    item_dict
#    item_list
#
#    item_decl
#    item_type
#    item_value
#    item_body
#
#    item_code
#    item_code_decl
#    item_place
#
#    item_ref
#
#    item_label
#    item_block
#
#    jump_table
#    jump_label
#
#    type_name
#    type_decl
#    type_from
#
#    type_const
#    type_volatile
#
#    type_signed
#    type_unsigned
#
#    type_void
#    type_bool
#    type_char
#    type_wchar
#    type_short
#    type_int
#    type_long
#    type_float
#    type_double
#
#    alt_assign
#    alt_connect
#    alt_connect_dcl
#    alt_connect_signal
#    alt_create
#    alt_create_owner
#    alt_create_place
#    alt_ignore
#    alt_setup
#    alt_setup_param
#
#    attr_compile_time
#    attr_field
#    attr_context
#
#    _only_properties_
#    _properties_
#    link_obj
#
#    _fields_
#    items
#
#    description
#
#    method showNavigator ()

# --------------------------------------------------------------------------

# class Editor
#
#    grammar_data
#    compiler_data
#    navigator_data

# --------------------------------------------------------------------------

# Kate/KDevelop syntax highlighting file
#    $HOME/.kdevelop4/share/apps/katepart/syntax/python.xml
#    $HOME/.local/share/org.kde.syntax-highlighting/syntax/python.xml

# --------------------------------------------------------------------------

class TreeItem (QTreeWidgetItem) :
   def __init__ (self, parent, text = "") :
       super (TreeItem, self).__init__ (parent)
       self.setText (0, text)

   def addIcon (self, icon_name) :
       self.setIcon (0, findIcon (icon_name))

   def addToolTip (self, text) :
       self.setToolTip (0, text)

   def setInk (self, color_name) :
       self.setForeground (0, findColor (color_name))

   def setPaper (self, color_name) :
       self.setBackground (0, findColor (color_name))

# --------------------------------------------------------------------------

   def setupTreeItem (self) :
       tree_node = self
       obj = tree_node
       if hasattr (obj, "obj") :
          obj = obj.obj
       if getattr (obj, "item_ref", None) != None : # typically in declarations, there is obj.item_ref
          obj = obj.item_ref
       elif getattr (obj, "item_decl", None) != None : # typically in ident_expr
          obj = obj.item_decl

       if hasattr (obj, "item_icon") :
          if isinstance (obj.item_icon, str) :
             tree_node.setIcon (0, findIcon (obj.item_icon))
          elif isinstance (obj.item_icon, QIcon) :
             tree_node.setIcon (0, obj.item_icon)

       if getattr (obj, "item_tooltip", None != None) :
          tree_node.setToolTip (0, obj.item_tooltip)

       if hasattr (obj, "item_ink") :
          if isinstance (obj.item_ink, str) :
             tree_node.setForeground (0, findColor (obj.item_ink))
          elif obj.item_ink != None :
             tree_node.setForeground (0, obj.item_ink)

       if hasattr (obj, "item_paper") :
          if isinstance (obj.item_paper, str) :
             tree_node.setBackground (0, findColor (obj.item_paper))
          elif obj.item_paper != None :
             tree_node.setBackground (0, obj.item_paper)

# --------------------------------------------------------------------------

def treeItemCoordinates (obj, fileName, line, column, pos) :

    if fileName == None :
       if hasattr (obj, "src_file") :
          fileName = indexToFileName (obj.src_file)
    if line == None :
       if hasattr (obj, "src_line") :
          line = obj.src_line
    if column == None:
       if hasattr (obj, "src_column") :
          column = obj.src_column
    if pos == None :
       if hasattr (obj, "src_pos") :
          pos = obj.src_pos

    return (fileName, line, column, pos)

# --------------------------------------------------------------------------

def treeItemLocation (tree_node) :

    fileName = None
    line = None
    column = None
    pos = None

    "fileName, line, column (from node to root)"
    node = tree_node
    while node != None :
       fileName, line, column, pos = treeItemCoordinates (node, fileName, line, column, pos)
       node = node.parent ()

    "fileName, line, column (inside obj) (from node to root)"
    saveFileName = fileName
    if line == None :
       fileName = None
       line = None
       column = None
       pos = None

       node = tree_node
       while node != None :
          if getattr (node, "obj", None) != None :
             obj = node.obj # coordinates from object
             fileName, line, column, pos = treeItemCoordinates (node.obj, fileName, line, column, pos)
          node = node.parent ()

       if fileName == None :
          fileName = saveFileName
          line = None
          column = None
          pos = None

    return (fileName, line, column, pos)

# --------------------------------------------------------------------------

def treeItemSource (win, node) :
    if win != None :
       fileName, line, column, pos = treeItemLocation (node)
       if fileName != None :

          text = "file: " + fileName
          if line != None :
             text = text + ", line: " + str (line)
             if column != None :
                text = text + ", column: " + str (column)
          win.showStatus ("tree item: " + text)

          edit = win.loadFile (fileName, line, column)
          if edit != None and line == None and pos != None :
             edit.selectLineByPosition (pos)

# --------------------------------------------------------------------------

def treeItemProperties (win, node) :
    if win != None :
       obj = getattr (node, "obj", None)
       if obj != None :
          win.showProperties (obj)
       else :
          win.showProperties (node)

# --------------------------------------------------------------------------

class Tree (QTreeWidget):

    def __init__ (self, win = None) :
        super (Tree, self).__init__ (win)
        self.win = win

        self.header ().hide ()
        self.setAlternatingRowColors (True)

        self.setContextMenuPolicy (Qt.CustomContextMenu)
        self.customContextMenuRequested.connect (self.onContextMenu)

        # self.setDragDropMode (self.DragDrop)
        # self.setDragDropMode (self.InternalMove)

        self.setDragEnabled (True)
        self.viewport().setAcceptDrops (True) # <-- accept draging from another widgets

        self.setDropIndicatorShown (True)
        self.setSelectionMode (QAbstractItemView.SingleSelection)

        self.setAcceptDrops (True)

        self.setExpandsOnDoubleClick (False)
        self.itemExpanded.connect (self.onItemExpanded)
        self.itemSelectionChanged.connect (self.onItemSelectionChanged)
        self.itemActivated.connect (self.onItemActivated) # not used
        self.itemClicked.connect (self.onItemClicked)
        self.itemDoubleClicked.connect (self.onItemDoubleClicked)

    # stackoverflow.com/questions/25222906/how-to-stop-qtreewidget-from-creating-the-item-duplicates-on-drag-and-drop

    def mimeTypes (self) :
        result = QStringList ()
        result.append ("application/x-view-widget")
        return result

    def supportedDropActions (self) :
        return Qt.CopyAction | Qt.MoveAction

    def dropMimeData (self, target, index, mime, action) :
        if mime.hasFormat ("application/x-view-widget") :
           name = bytearray_to_str (mime.data ("application/x-view-widget"))
           print ("drop", name)
           # self.win.builder.addComponent (name, QPoint (0, 0), target)
           # target == None ... top of tree
           return True
        return False

    def onItemExpanded (self, branch) :
        cnt = branch.childCount ()
        for inx in range (cnt) :
            node = branch.child (inx)
            func = getattr (node, "expand_func", None)
            data = getattr (node, "expand_data", None)
            if func != None and data != None :
               node.expand_func = None
               node.expand_data = None
               func (node, data)

    def expandAllItems (self, node) :
        node.setExpanded (True)
        cnt = node.childCount ()
        inx = 0
        while inx < cnt :
           t = node.child (inx)
           self.expandAllItems (t)
           inx = inx + 1

    def expandFirstItems (self, node) :
        cnt = node.childCount ()
        while cnt > 0 :
           node.setExpanded (True)
           node = node.child (0) # first
           cnt = node.childCount ()

    def expandLastItems (self, node) :
        cnt = node.childCount ()
        while cnt > 0 :
           node.setExpanded (True)
           node = node.child (cnt-1) # last
           cnt = node.childCount ()

    """
    def showItem (self, node) :
        if hasattr (node, "obj") :
           self.win.showProperties (node.obj)
        else :
           self.win.showProperties (node)

    def jumpToItem (self, node) :
        if hasattr (node, "obj") :
           treeItemJump (self.win, node.obj)
    """

    def onItemSelectionChanged (self) :
        # keyboard or mouse
        # print ("SELECTION CHANGED")
        for node in self.selectedItems () :
            treeItemProperties (self.win, node)

    def onItemActivated (self, node, column) :
        # only mouse
        # print ("ITEM ACTIVATED")
        pass

    def onItemClicked (self, node, column) :
        # only mouse
        mask = Qt.ShiftModifier | Qt.ControlModifier | Qt.AltModifier | Qt.MetaModifier
        mod = int (QApplication.keyboardModifiers () & mask)
        if mod == Qt.ControlModifier :
           # print ("CONTROL CLICK")
           self.expandFirstItems (node)
        elif mod == Qt.ShiftModifier :
           # print ("SHIFT CLICK")
           self.expandLastItems (node)
        elif mod == int (Qt.ShiftModifier | Qt.ControlModifier ):
           # print ("CONTROL SHIFT CLICK")
           self.expandAllItems (node)
        else :
           # print ("CLICK")
           pass

    def onItemDoubleClicked (self, node, column) :
        # only mouse
        # print ("DOUBLE CLICK")
        treeItemSource (self.win, node)


    def onContextMenu (self, pos) :
        node = self.itemAt (pos)

        menu = QMenu (self)

        act = menu.addAction ("tree node properties")
        act.triggered.connect (lambda param, win=self.win, node=node: win.showProperties (node))

        if hasattr (node, "obj") :
           act = menu.addAction ("obj properties")
           act.triggered.connect (lambda param, win=self.win, node=node: win.showProperties (node.obj))

        if hasattr (node, "obj") :
           act = menu.addAction ("jump to declaration")
           act.triggered.connect (lambda param, win=self.win, node=node: treeItemSource (win, node))

        if hasattr (node, "obj") :
           obj = node.obj
        else :
           obj = node

        # if hasattr (obj, "description") :
        #    act = menu.addAction ("macro description")
        #    act.triggered.connect (lambda param, self=self, obj=obj: self.showDescription (obj))

        # if hasattr (node, "src_file") or hasattr (node, "src_line") :
        #    act = menu.addAction ("jump to")
        #    act.triggered.connect (lambda param, win=self.win, node=node: jumpTo (win, node))

        # jump table

        if hasattr (obj, "jump_table") :
           jump_table = obj.jump_table

           if len (jump_table) != 0 :
              menu.addSeparator ()
              for item in jump_table :
                  text = getattr (item, "jump_label", "")
                  if text == "" :
                     text = str (item)
                  act = menu.addAction ("jump to " + text)
                  act.triggered.connect (lambda param, win=self.win, item=item: treeItemSource (win, item))

        # expand branch

        menu.addSeparator ()

        act = menu.addAction ("expand subitems")
        act.triggered.connect (lambda param, self=self, node=node: self.expandAllItems (node))

        act = menu.addAction ("expand first subitems")
        act.triggered.connect (lambda param, self=self, node=node: self.expandFirstItems (node))

        act = menu.addAction ("expand last subitems")
        act.triggered.connect (lambda param, self=self, node=node: self.expandLastItems (node))

        # show menu

        menu.exec_ (self.mapToGlobal (QPoint (pos)))

    # def showDescription (self, obj) :
    # DescriptionWindow (self.win, obj.description)

# --------------------------------------------------------------------------

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
