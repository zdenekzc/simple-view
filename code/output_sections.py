
# sections.py

from __future__ import print_function

import sys, os

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

from util import findColor, findIcon, Text
from input import fileNameToIndex
from tree import TreeItem

# --------------------------------------------------------------------------

class Sections (object) :
   def __init__ (self, branch, edit) :
       self.branch = branch
       self.edit = edit
       self.cursor = self.edit.textCursor ()
       self.fileInx = fileNameToIndex (self.edit.getFileName ())
       self.shortFileName = os.path.basename (self.edit.getFileName ())

   # text output

   def open (self) :
       self.edit.clear () # empty file

   def close (self) :
       self.edit.saveFile () # flush

   def write (self, txt) :
       self.cursor.insertText (txt)

   # sections

   def openSection (self, obj) :
       # print ("Sections.openSection " + str (obj))
       text = ""
       if hasattr (obj, "item_name") :
          text = obj.item_name
       else :
          text = str (obj)

       new_branch = TreeItem (self.branch, text)
       new_branch.obj = obj
       new_branch.src_file = self.fileInx
       new_branch.src_line = self.cursor.blockNumber () + 1
       new_branch.setupTreeItem ()
       self.branch = new_branch

       if hasattr (obj, "item_name") :
          self.cursor.select (QTextCursor.WordUnderCursor)
          fmt = self.cursor.charFormat ()
          fmt.setProperty (Text.openProperty, obj.item_name)
          self.cursor.setCharFormat (fmt)

       if not hasattr (obj, "jump_table") :
          obj.jump_table = [ ]
       obj.jump_table.append (self.branch)
       self.branch.jump_label = self.shortFileName

   def closeSection (self) :
       # if self.branch != None :
       if isinstance (self.branch, QTreeWidgetItem) :
          obj = self.branch.obj
          if hasattr (obj, "item_name") :
             self.cursor.select (QTextCursor.WordUnderCursor)
             fmt = self.cursor.charFormat ()
             fmt.setProperty (Text.closeProperty, obj.item_name)
             self.cursor.setCharFormat (fmt)

          above = self.branch.parent ()
          # if above != None :
          if isinstance (above, QTreeWidgetItem) :
             self.branch = above

   def simpleSection (obj) :
       self.openSection (obj)
       self.closeSection ()

   # ink, paper, ...

   def setInk (self, ink) :
       if isinstance (ink, str) :
          ink = findColor (ink)
       fmt = self.cursor.charFormat ()
       if ink == None :
          fmt.clearForeground ()
       else :
          fmt.setForeground (ink)
       fmt.setProperty (Text.infoProperty, "") # no highlighting
       self.cursor.setCharFormat (fmt)

   def setPaper (self, paper) :
       if isinstance (paper, str) :
          paper = findColor (paper)
       fmt = self.cursor.charFormat ()
       if paper == None :
          fmt.clearBackground ()
       else :
          fmt.setBackground (paper)
       fmt.setProperty (Text.infoProperty, "") # no highlighting
       self.cursor.setCharFormat (fmt)

   def addToolTip (self, text, tooltip) :
       fmt = self.cursor.charFormat ()
       fmt.setToolTip (tooltip)
       self.cursor.setCharFormat (fmt)
       self.cursor.insertText (text)
       fmt.clearProperty (QTextFormat.TextToolTip)
       self.cursor.setCharFormat (fmt)

   def addDefinition (self, text, defn) :
       fmt = self.cursor.charFormat ()
       fmt.setProperty (Text.defnProperty, defn)
       fmt.setProperty (Text.infoProperty, defn)
       self.cursor.setCharFormat (fmt)
       self.cursor.insertText (text)
       fmt.clearProperty (Text.defnProperty)
       fmt.clearProperty (Text.infoProperty)
       self.cursor.setCharFormat (fmt)

   def addUsage (self, text, usage) :
       fmt = self.cursor.charFormat ()
       fmt.setProperty (Text.infoProperty, usage)
       self.cursor.setCharFormat (fmt)
       self.cursor.insertText (text)
       fmt.clearProperty (Text.infoProperty)
       self.cursor.setCharFormat (fmt)

# --------------------------------------------------------------------------

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
