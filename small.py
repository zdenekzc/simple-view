#!/usr/bin/env python

from __future__ import print_function

import sys, os, re

from util import use_pyside2, use_qt5, use_new_api
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

from util import findColor, findIcon, Text, setResizeMode, qstringref_to_str, qstringlist_to_list
from tree import Tree, TreeItem
from info import Info
from edit import Editor

from input import fileNameToIndex
from grammar import Grammar, Rule, Expression, Alternative, Ebnf, Nonterminal, Terminal

# --------------------------------------------------------------------------

class IconProvider (QFileIconProvider) :
   def __init__ (self) :
       super (IconProvider, self).__init__ ()
       self.database = None
       try :
          self.database = QMimeDatabase ()
       except :
          pass
       self.formats = QImageReader.supportedImageFormats()

   def icon (self, fileInfo) :
       result = None
       if fileInfo.suffix () in self.formats :
          result = QIcon (fileInfo.filePath ())
       if result == None or result.isNull() :
          if self.database != None :
             info = self.database.mimeTypeForFile (fileInfo)
             result = QIcon.fromTheme (info.iconName ())
          if result == None or result.isNull() :
             result =  super (IconProvider, self).icon (fileInfo)
       return result

class TreeDir (QTreeView):

   def __init__ (self, win) :
       super (TreeDir, self).__init__ (win)
       self.win = win

       path = QDir.currentPath ()
       # path = "/usr/share/icons"

       if 1 :
          model = QDirModel ()
       else :
          model = QFileSystemModel ()
          model.setRootPath (path)

       # model.setReadOnly (True)
       # model.dataChanged.connect (lambda: model.sort (0))
       model.setIconProvider (IconProvider ())

       self.setModel (model)
       self.setCurrentIndex (model.index (path))

       header = self.header ()
       setResizeMode (header, 0, QHeaderView.ResizeToContents)
       setResizeMode (header, 1, QHeaderView.Fixed)
       header.hideSection (2)
       header.hideSection (3)

       self.activated.connect (self.onActivated)

       self.setContextMenuPolicy (Qt.CustomContextMenu)
       self.customContextMenuRequested.connect (self.onContextMenu)

   def onActivated (self, index) :
       if self.win != None :
          fileName = self.model().filePath (index)
          # self.win.showStatus (fileName)
          self.win.loadFile (fileName)

   def onContextMenu (self, pos) :
       menu = QMenu (self)

       dir_list = [ sys.path [0] ]
       dir_list = dir_list + qstringlist_to_list (QIcon.themeSearchPaths())

       for path in dir_list :
          act = menu.addAction (path)
          act.triggered.connect (lambda param, self=self, path=path: self.showPath (path))

       menu.exec_ (self.mapToGlobal (QPoint (pos)))

   def showPath (self, path) :
       model = self.model ()
       inx = model.index (path)
       self.setCurrentIndex (inx)

# --------------------------------------------------------------------------

class Documents (Tree) :
   def __init__ (self, win, toolTabs, editTabs) :
       super (Documents, self).__init__ (win)
       self.active = False
       self.win = win
       self.toolTabs = toolTabs
       self.editTabs = editTabs
       self.toolTabs.currentChanged.connect (self.onToolChanged)
       self.editTabs.currentChanged.connect (self.onEditorChanged)
       self.itemActivated.connect (self.onTreeItemActivated)
       self.header ().hide ()

   def onToolChanged (self) :
       self.active = self.toolTabs.currentWidget () == self
       if self.active :
          self.showData ()

   def onEditorChanged (self) :
       if self.active :
          self.showData ()

   def onTreeItemActivated (self, tree_node) :
       if hasattr (tree_node, "widget") :
          self.editTabs.setCurrentWidget (tree_node.widget)

   def showData (self) :
       self.clear ()
       # print ("showDocuments")
       cnt = self.editTabs.count ()
       for inx in range (cnt) :
           w = self.editTabs.widget (inx)
           if isinstance (w, Editor) :
              fileName = w.getFileName ()
              text = os.path.basename (fileName)
              node = TreeItem (self, text)
              node.setToolTip (0, fileName)
              node.fileName = fileName
              node.setIcon (0, findIcon ("document-open"))
              node.widget = w # !?
           else :
              text = self.editTabs.tabText (inx)
              node = TreeItem (self, text)
              node.setIcon (0, findIcon ("document-closed"))
              node.widget = w

# --------------------------------------------------------------------------

class Bookmarks (Tree) :
   def __init__ (self, win, toolTabs, editTabs) :
       super (Bookmarks, self).__init__ (win)
       self.active = False
       self.win = win
       self.toolTabs = toolTabs
       self.editTabs = editTabs
       self.toolTabs.currentChanged.connect (self.onToolChanged)

   def onToolChanged (self) :
       self.active = self.toolTabs.currentWidget () == self
       if self.active :
          self.showBookmarks ()

   def activate (self) :
       if self.active :
          self.showBookmarks ()

   def showBookmarks (self) :
       self.clear ()
       # print ("showBookmarks")
       cnt = self.editTabs.count ()
       for inx in range (cnt) :
           editor = self.editTabs.widget (inx)
           any = False
           branch = None
           if isinstance (editor, Editor) :
              fileName = editor.getFileName ()
              bookmarks = editor.getBookmarks ()
              document = None
              for bookmark in bookmarks :
                  if branch == None :
                     text = os.path.basename (fileName)
                     # text = text + " in " + os.path.dirname (fileName)
                     branch = TreeItem (self, text)
                     branch.src_file = fileNameToIndex (fileName)
                     branch.setToolTip (0, fileName)
                     branch.setIcon (0, findIcon ("document-open"))
                     branch.setExpanded (True)
                     document = editor.document ()

                  text = document.findBlockByLineNumber (bookmark.line-1).text ()
                  text = "line " + str (bookmark.line) + ": " + text
                  node = TreeItem (branch, text)
                  node.src_file = branch.src_file
                  node.src_line = bookmark.line
                  node.src_column = bookmark.column
                  node.setIcon (0, findIcon ("bookmarks"))

                  index = bookmark.mark
                  if index >= 1 and index <= len (Editor.bookmark_colors) :
                     node.setBackground (0, Editor.bookmark_colors [index-1])

# --------------------------------------------------------------------------

class Navigator (Tree) :
   def __init__ (self, win, toolTabs) :
       super (Navigator, self).__init__ (win)
       self.active = False
       self.win = win
       self.toolTabs = toolTabs
       self.toolTabs.currentChanged.connect (self.onToolChanged)
       self.win.tabChanged.connect (self.onEditorChanged)
       self.keep = False

   def onToolChanged (self) :
       self.active = self.toolTabs.currentWidget () == self
       if self.active :
          self.showNavigator ()

   def onEditorChanged (self) :
       if self.active :
          self.showNavigator ()

   def showNavigator (self) : # called from edit.py
       # print ("show navigator")
       if self.keep :
          self.takeTopLevelItem (0)
          self.keep = False
       else :
          self.clear ()
       self.keep = False
       editor = self.win.getEditor ()
       if editor != None :
          if getattr (editor, "navigator_data", None) != None :
             # print ("showNavigator by navigator_data")
             self.showTreeData (editor.navigator_data)
          else :
             # print ("showNavigator by file name")
             fileName = editor.getFileName ()
             name, ext = os.path.splitext (fileName)
             if ext == ".py" :
                PythonTree (self, editor)
             elif ext == ".g" :
                self.showGrammarRules (editor)
             else :
                self.showTextProperties (editor)
       else :
          w = self.win.getCurrentTab ()
          if hasattr (w, "showNavigator") :
             w.showNavigator ()
          elif hasattr (w, "navigator_data") :
             self.showTreeData (w.navigator_data)

   def showTreeData (self, data) :
       if isinstance (data, QTreeWidgetItem) : # !?
          self.addTopLevelItem (data)
          self.keep = True
       else :
          IdentifierTree (self, data, navig=True)

   def showGrammarRules (self, editor) :
       tree = self
       fileName = editor.getFileName ()
       self.src_file = fileNameToIndex (fileName)
       source = str (editor.toPlainText ())
       lineNum = 0
       for line in source.split ("\n") :
           lineNum = lineNum + 1
           pattern = "(\s*)(\w\w*)\s*(<.*>)\s*:\s*"
           m = re.match (pattern, line)
           if m :
              name = m.group (2)
              node = TreeItem (tree, name)
              node.src_file = self.src_file
              node.src_line = lineNum
              node.addIcon ("class")

   def showTextProperties (self, editor) :
       tree = self
       fileName = editor.getFileName ()
       fileInx = fileNameToIndex (fileName)
       branch = tree
       block = editor.document().firstBlock()
       while block.isValid () :
          iterator = block.begin ()
          while not iterator.atEnd () :
             fragment = iterator.fragment ();
             if fragment.isValid () :
                fmt = fragment.charFormat ()
                if fmt.hasProperty (Text.outlineProperty) :
                   name = str (fmt.stringProperty (Text.outlineProperty))
                   node = TreeItem (branch, name)
                   node.src_file = fileInx
                   node.src_line = block.blockNumber () + 1
                elif fmt.hasProperty (Text.defnProperty) :
                   name = str (fmt.stringProperty (Text.defnProperty))
                   node = TreeItem (branch, name)
                   node.src_file = fileInx
                   node.src_line = block.blockNumber () + 1
             iterator += 1
          block = block.next ()

# --------------------------------------------------------------------------

class Memo (Tree) :
   def __init__ (self, win, toolTabs) :
       super (Memo, self).__init__ (win)
       self.win = win
       self.toolTabs = toolTabs
       self.itemDoubleClicked.connect (self.onItemDoubleClicked)

   def showMemo (self, editor, name) : # called from view.py

       self.toolTabs.setCurrentWidget (self)

       # print ("show memo (1)", name)
       obj = editor.findIdentifier (name)
       if obj != None :
          # print ("show memo (2)", obj.item_name)
          branch = TreeItem (self, obj.item_name)
          branch.obj = obj
          branch.setupTreeItem ()
          branch.setExpanded (True)
          if hasattr (obj, "item_list") :
             for item in obj.item_list :
                 node = TreeItem (branch, item.item_name)
                 node.obj = item
                 node.setupTreeItem ()

   def onItemActivated (self, tree_node, column) :
       pass # do not jump to object declaration

   def onItemDoubleClicked (self, node, column) :
       name = node.text (0)
       editor = self.win.getEditor ()
       cursor = editor.textCursor ()
       cursor.insertText (name)

# --------------------------------------------------------------------------

class References (Tree) :
   def __init__ (self, win, toolTabs) :
       super (References, self).__init__ (win)
       self.win = win
       self.toolTabs = toolTabs

   def showReferences (self, editor, name) : # called from edit.py
       self.clear ()
       fileName = editor.getFileName ()
       fileInx = fileNameToIndex (fileName)
       block = editor.document().firstBlock()
       while block.isValid () :
          iterator = block.begin ()
          while not iterator.atEnd () :
             fragment = iterator.fragment();
             if fragment.isValid () :
                fmt = fragment.charFormat ()
                if fmt.hasProperty (Text.infoProperty) :
                   value = str (fmt.stringProperty (Text.infoProperty))
                   if value == name :
                      line = block.blockNumber() + 1
                      text = str (block.text ())
                      text = "line " + str (line) + ": " + text.strip()
                      node = TreeItem (self, text)
                      node.src_file = fileInx
                      node.src_line = line
             iterator += 1
          block = block.next ()
       self.toolTabs.setCurrentWidget (self)

# --------------------------------------------------------------------------

class Structure (Tree) :
   def __init__ (self, win, toolTabs) :
       super (Structure, self).__init__ (win)

       self.active = False
       self.win = win
       self.toolTabs = toolTabs
       self.toolTabs.currentChanged.connect (self.onToolChanged)
       self.win.tabChanged.connect (self.onEditorChanged)

   def onToolChanged (self) :
       self.active = self.toolTabs.currentWidget () == self
       if self.active :
          self.showData ()

   def onEditorChanged (self) :
       if self.active :
          self.showData ()

   def showData (self) :
       # print ("show structure")
       self.clear ()
       editor = self.win.getCurrentTab ()
       if isinstance (editor, QPlainTextEdit):
          self.showTextDocument (editor)

   def showTextDocument (self, editor) :
       tree = self
       fileName = None
       fileInx = None
       if hasattr (editor, "getFileName") :
          fileName = editor.getFileName ()
          fileInx = fileNameToIndex (fileName)

       branch = TreeItem (tree, "extra selections")
       extraSelections = editor.extraSelections ()
       for selection in extraSelections :
           cursor = selection.cursor
           fmt = selection.format
           line = cursor.blockNumber ()
           node = TreeItem (branch, "block " + str (line))
           node.src_file = fileInx
           node.src_line = line + 1
           self.displayFormat (node, fmt)

       block = editor.document().firstBlock()
       while block.isValid () :
          line = block.blockNumber ()
          branch = TreeItem (tree, "block " + str (line) + " " + block.text ())
          branch.src_file = fileInx
          branch.src_line = line + 1

          fmt = block.blockFormat ()
          self.displayFormat (branch, fmt)
          iterator = block.begin ()
          while not iterator.atEnd () :
             fragment = iterator.fragment ();
             if fragment.isValid () :
                node = TreeItem (branch, "fragment " + fragment.text ())
                fmt = fragment.charFormat ()
                self.displayFormat (node, fmt)
             iterator += 1
          block = block.next ()

   def displayProperty (self, above, fmt, title, property) :
       if fmt.hasProperty (property) :
          TreeItem (above, title + ": " + str (fmt.stringProperty (property)))

   def displayFormat (self, above, fmt) :
       above.setForeground (0, fmt.foreground ())
       above.setBackground (0, fmt.background ())
       if fmt.hasProperty (Text.bookmarkProperty) :
          inx = fmt.intProperty (Text.bookmarkProperty)
          node = TreeItem (above, "bookmark: " +  str (fmt.intProperty (Text.bookmarkProperty)))
          if inx >= 1 and inx <= len (Editor.bookmark_colors) :
             node.setBackground (0, Editor.bookmark_colors [inx-1])
       self.displayProperty (above, fmt, "tooltip", QTextFormat.TextToolTip)
       self.displayProperty (above, fmt, "location", Text.locationProperty)
       self.displayProperty (above, fmt, "info", Text.infoProperty)
       self.displayProperty (above, fmt, "defn", Text.defnProperty)
       self.displayProperty (above, fmt, "open", Text.openProperty)
       self.displayProperty (above, fmt, "close", Text.closeProperty)
       self.displayProperty (above, fmt, "outline", Text.outlineProperty)

# --------------------------------------------------------------------------

def XmlTree (tree, fileName) :
    top = TreeItem (tree)
    fileInx = fileNameToIndex (fileName)

    f = QFile (fileName)
    if f.open (QFile.ReadOnly | QFile.Text) :
       reader = QXmlStreamReader (f)

       fileInfo = QFileInfo (fileName)
       top.setText (0, fileInfo.fileName ())
       top.setForeground (0, findColor ("green"))
       top.setExpanded (True)

       current = top

       while not reader.atEnd() :
          if reader.isStartElement () :
             item = TreeItem (current)
             item.setText (0, qstringref_to_str (reader.name ()))
             item.setForeground (0, findColor ("blue"))
             item.src_file = fileInx
             item.src_line = reader.lineNumber ()
             item.setExpanded (True)
             current = item

             attrs = reader.attributes ()
             cnt = attrs.size ()
             for i in range (cnt) :
                a = attrs.at (i) # QXmlStreamAttribute
                node = TreeItem (item)
                node.setText (0, qstringref_to_str (a.name ()) + " = " + qstringref_to_str (a.value ()))
                node.setForeground (0, findColor ("goldenrod"))

             if qstringref_to_str (reader.name ()) == "widget" :
                decl = TreeItem (top)
                decl.setText (0, qstringref_to_str (attrs.value ("name")) + " : " + qstringref_to_str (attrs.value ("class")))
                decl.setForeground (0, findColor ("orange"))
                decl.src_file = fileInx
                decl.src_line = reader.lineNumber ()

          elif reader.isEndElement () :
             current = current.parent ()

          elif reader.isCharacters () and not reader.isWhitespace () :
             item = TreeItem (current)
             item.setText (0, qstringref_to_str (reader.text ()))
             item.setForeground (0, findColor ("limegreen"))
             item.src_file = fileInx
             item.src_line = reader.lineNumber ()

          reader.readNext ()

       if reader.hasError() :
          item = TreeItem (top)
          item.setText (0, reader.errorString ())
          item.setForeground (0, findColor ("red"))

    f.close()

# --------------------------------------------------------------------------

"Scope of identifiers - win.showClasses () or showNavigator ()"

class IdentifierTree (object) :
   def __init__ (self, tree, data, navig = False) :
       self.navig = navig
       if getattr (data, "item_name", "") == "" :
          self.showScope (tree, data)
       else :
          self.showItem (tree, data)

   def showItem (self, above, data) :
       if getattr (data, "item_transparent", False) :
          node = above
       else :
          name = getattr (data, "item_label", "")
          if name == "" :
             name = getattr (data, "item_name", "")
          node = TreeItem (above, name)
          node.obj = data
          node.setupTreeItem ()

       self.showScope (node, data)

       expand = getattr (data, "item_expand", False)
       if expand :
          node.setExpanded (True)

   def showScope (self, above, data) :
       if hasattr (data, "item_list") :
          for item in data.item_list :
              self.showItem (above, item)
       if self.navig and hasattr (data, "item_block") :
          for item in data.item_block :
              self.showItem (above, item)

# --------------------------------------------------------------------------

"Grammar data - win.displayGrammarData ()"

class GrammarTree (object) :
   def __init__ (self, tree, grammar, fileInx) :
       self.grammar = grammar
       self.fileInx = fileInx
       self.group_branch = None

       self.addSymbols (tree)
       self.addTypes (tree)
       self.addGroups (tree)

       for rule in grammar.rules :
          self.addBranch (tree, rule)

   def addSymbols (self, above) :
       branch = TreeItem (above, "symbols")
       for symbol in self.grammar.symbols :
           TreeItem (branch, str (symbol.inx) + " " + symbol.alias)

   def addTypes (self, above) :
       branch = TreeItem (above, "types")
       for type in self.grammar.type_list :
           node = TreeItem (branch, type.name)
           node.addIcon ("class")
           node.obj = type
           for enum in type.enum_list :
               leaf = TreeItem (node, enum.name)
               leaf.addIcon ("enum")
               leaf.obj = enum
           for field in type.field_list :
               leaf = TreeItem (node, field.name)
               leaf.addIcon ("variable")
               leaf.obj = field

   def addGroups (self, above) :
       self.group_branch = TreeItem (above, "groups")

   def updateGroups (self) :
       branch = self.group_branch
       for group in self.grammar.group_list :
           node = TreeItem (branch, group.group_name)
           node.addIcon ("class")
           node.obj = group
           for rule in self.grammar.rules :
               if rule.hide_group == group :
                  leaf = TreeItem (node, "hide " + rule.name)
                  leaf.addIcon ("flag-red")
                  leaf.obj = rule
           for rule in self.grammar.rules :
               if rule.subst_group == group :
                  leaf = TreeItem (node, "subst " + rule.name)
                  leaf.addIcon ("flag-green")
                  leaf.obj = rule
           for rule in self.grammar.rules :
               if rule.rewrite_group == group or rule.reuse_group == group :
                  leaf = TreeItem (node, rule.name)
                  leaf.addIcon ("flag-blue")
                  leaf.obj = rule

   def addBranch (self, above, data) :
       txt = ""
       if isinstance (data, Rule) :
          txt = data.name
       elif isinstance (data, Expression) :
          txt = "expression"
       elif isinstance (data, Alternative) :
          txt = "alternative"
       elif isinstance (data, Ebnf) :
          txt = "ebnf " + data.mark
       elif isinstance (data, Nonterminal) :
          txt = "nonterminal "
          if data.variable != "" :
             txt = txt + data.variable + ":"
          txt = txt + data.rule_name
       elif isinstance (data, Terminal) :
          if data.multiterminal_name != "" :
             if data.variable != "" :
                txt = txt + data.variable + ":"
             txt = "terminal " + data.multiterminal_name
          else :
             txt = "terminal " + data.text
       else:
          txt = data.__class__.__name__

       node = TreeItem (above, txt)

       # if hasattr (data, "src_line") :
       #    node.src_file = self.fileInx
       #    node.src_line = data.src_line
       node.obj = data

       if isinstance (data, Rule) :
          node.setToolTip (0, "line " + str (data.src_line))
          node.addIcon ("class")
       if isinstance (data, Nonterminal) :
          node.addIcon ("function")
       if isinstance (data, Terminal) :
          node.addIcon ("variable")
       if isinstance (data, Ebnf) :
          node.addIcon ("block")

       if isinstance (data, Rule) :
          if hasattr (data, "first") :
             n = 0
             for inx in range (len (data.first)) :
                 if data.first [inx] :
                    n = n + 1
             if n > 1 :
                node.setForeground (0, QBrush (Qt.green))

       if hasattr (data, "nullable") :
          if data.nullable :
             node.setForeground (0, QBrush (Qt.red))

       self.addInfo (node, data)

       if isinstance (data, Rule) :
          # self.addInfo (node, data)
          self.addBranch (node, data.expr)
       elif isinstance (data, Expression) :
          for t in data.alternatives :
             self.addBranch (node, t)
       elif isinstance (data, Alternative) :
          for t in data.items :
             self.addBranch (node, t)
       elif isinstance (data, Ebnf) :
          self.addBranch (node, data.expr)

   def addInfo (self, above, rule) :
       if hasattr (rule, "first") :
          branch = TreeItem (above, "first")
          branch.addIcon ("info")
          branch.setForeground (0, QBrush (Qt.blue))
          if hasattr (rule, "nullable") and rule.nullable :
             node = TreeItem (branch, "<empty>")
             node.setForeground (0, QBrush (Qt.red))
          for inx in range (len (rule.first)) :
              if rule.first [inx] :
                 name = self.grammar.symbols [inx].alias
                 node = TreeItem (branch, name)
                 node.setForeground (0, QBrush (Qt.blue))
       if hasattr (rule, "follow") :
          branch = TreeItem (above, "follow")
          branch.addIcon ("info")
          branch.setForeground (0, QBrush (Qt.blue))
          for inx in range (len (rule.first)) :
              if rule.follow [inx] :
                 name = self.grammar.symbols [inx].alias
                 node = TreeItem (branch, name)
                 node.setForeground (0, QBrush (Qt.blue))

# --------------------------------------------------------------------------

"Compiler data - win.displayCompilerData ()"

class CompilerTree (object) :
   def __init__ (self, tree, data) :
       self.showStructure (tree, "", data, 1)

   def showStructure (self, above, name, data, level) :
       if name != "" :
          name = name + " : "

       if data == None :
          TreeItem (above, name + "None")
       elif isinstance (data, int) :
          TreeItem (above, name + "int = " + str (data))
       elif isinstance (data, str) :
          TreeItem (above, name + "string = " + data)
       else :
          text = name + "object " + data.__class__.__name__

          if getattr (data, "item_name", None) != None:
             text = text + " (item_name: " + str (data.item_name) + ")"
          if getattr (data, "item_decl", None) != None:
             text = text + " (item_decl: " + str (data.item_decl) + ")"
          if getattr (data, "item_type", None) != None:
             text = text + " (item_type: " + str (data.item_type) + ")"
          if getattr (data, "item_ref", None) != None:
             text = text + " (item_ref: " + str (data.item_ref) + ")"
          if getattr (data, "id", None) != None:
             text = text + " (id: " + str (data.id) + ")" # !? identifiers
          if getattr (data, "item_label", None) != None:
             text = text + " (item_label: " + str (data.item_label) + ")"

          branch = TreeItem (above, text)
          branch.obj = data # show data object in property window
          branch.setupTreeItem ()

          # if level > 1 :
             # branch.expand_func = self.showBranch
             # branch.expand_data = data
          # else :
             #s elf.showBranch (branch, data, level)
          self.showBranch (branch, data, level)

   def showBranch (self, branch, data, level = 1) :
          if hasattr (data, "_fields_") :
             for ident in data._fields_ :
                 if ident != "body" and ident != "ctor_init":
                    self.showStructureItem (branch, data, ident, level)
          # elif hasattr (data, "__dict__") : # !?
          #    for ident in data.__dict__ :
          #        self.showStructureItem (branch, data, ident)

          if hasattr (data, "items") and not isinstance (data, dict) :
             for item in data.items :
                self.showStructure (branch, "", item, level+1)

          if hasattr (data, "ctor_init") :
             self.showStructureItem (branch, data, "ctor_init", level)
          if hasattr (data, "body") :
             self.showStructureItem (branch, data, "body", level)

   def showStructureItem  (self, above, data, ident, level) :
       if ident != "items" :
          if hasattr (data, ident) :
             item = data.__dict__ [ident]
             # print ("showStructure " + ident + " in " + str (item))
             if item == data :
                print ("recursion",  ident, str (item))
                temp = TreeItem (above, "recursion")
                temp.addIcon ("error")
             else :
                self.showStructure (above, ident, item, level+1)

# --------------------------------------------------------------------------

def lookupCompilerData (tree, editor, line, column) :
    if isinstance (editor, QPlainTextEdit) :
       fileName = editor.getFileName ()
       fileInx = fileNameToIndex (fileName)
       # print ("line", line, "column", column)

       iter = QTreeWidgetItemIterator (tree)
       while iter.value () :
          node = iter.value ()
          # print ("compiler data ", node.text (0))
          if hasattr (node, "obj") :
             obj = node.obj
             if hasattr (obj, "src_file") :
                if obj.src_file == fileInx :
                   if hasattr (obj, "src_line") :
                      if hasattr (obj, "src_column") :
                         # print ("obj.src_line", obj.src_line, "obj.src_column", obj.src_column)
                         found = obj.src_line > line or obj.src_line == line and obj.src_column >= column
                      else :
                         found = obj.src_line >= line
                      if found :
                         tree.setCurrentItem (node)
                         tree.scrollToItem (node)
                         node.setExpanded (True)
                         break
          iter += 1

# --------------------------------------------------------------------------

# Python classes and methods - win.displayPythonCode () or showNavigator ()

class PythonTree (object) :
   def __init__ (self, tree, editor) :
       fileName = editor.getFileName ()
       self.src_file = fileNameToIndex (fileName)
       source = str (editor.toPlainText ())

       lineNum = 0
       cls_branch = None
       for line in source.split ("\n") :
           lineNum = lineNum + 1
           pattern = "(\s*)(class|def)\s\s*(\w*)"
           m = re.match (pattern, line)
           if m :
              target = tree
              if m.group (1) != "" and cls_branch != None :
                 target = cls_branch

              is_class = m.group (2) == "class"

              name = m.group (3)
              if is_class :
                 name = "class " + name

              node = TreeItem (target, name)
              node.src_file = self.src_file
              node.src_line = lineNum

              if is_class :
                 node.addIcon ("class")
              else :
                 node.addIcon ("function")

              if is_class :
                 cls_branch = node

# --------------------------------------------------------------------------

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
