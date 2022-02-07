
# cmm_follow.py

from __future__ import print_function

import os, sys, traceback

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

from input import fileNameToIndex, indexToFileName, quoteString
from lexer import Lexer, MonitorClass

from tree import TreeItem
# from small import Description
from util import findColor, Text

# --------------------------------------------------------------------------

class Monitor (MonitorClass) :

   def __init__ (self, win) :
       self.win = win
       self.lexer = None

       self.description_stack = [ ]
       self.include_stack = [ ]
       self.debug_incl_files = { }

       self.showComments = True
       self.showTokens = True
       self.showTokensInTree = True
       self.showUnusedTokens = True

       self.showLinearInclude = False

       target = self.win.tree

       self.incl_dir_branch = TreeItem (target, "include directories")

       self.incl_branch = TreeItem (target, "include files")

       self.already_incl_branch = TreeItem (target, "already included files")

       self.ignored_incl_branch = TreeItem (target, "ignored include files")

       self.missing_incl_branch = TreeItem (target, "missing included files")

       self.guard_branch = TreeItem (target, "guard map")

       self.missing_guard_branch = TreeItem (target, "missing guard")

       self.macro_branch = TreeItem (target, "defined symbols")

       self.decl_branch = TreeItem (self.win.tree, "declarations")
       self.decl_map = { }

       self.object_branch = TreeItem (target, "parser objects")

       self.top = TreeItem (self.win.tree, "lexer data")
       self.current = self.top

       self.red = findColor ("red")
       self.blue = findColor ("blue")
       self.green = findColor ("green")
       self.orange = findColor ("orange")
       self.brown = findColor ("peru")
       self.gray = findColor ("gray")

       self.cornflowerblue = findColor ("cornflowerblue")
       self.lime = findColor ("lime")
       self.limegreen = findColor ("limegreen")
       self.plum = findColor ("plum")
       self.blueviolet = findColor ("blueviolet")

       # self.yellow = findColor ("yellow").lighter (160)
       # self.blue = findColor ("blue").lighter (160)
       # self.red = findColor ("red").lighter (160)

   def disableDebug (self) :
       self.showComments = False
       self.showTokens = False
       self.showTokensInTree = False
       self.showUnusedTokens = False
       self.showLinearInclude = False

   def enableDebug (self) :
       # self.lexer.debug = True
       self.showComments = True
       self.showTokens = True
       self.showTokensInTree = False
       self.showUnusedTokens = True
       self.showLinearInclude = True

   def debugIncl (self, fileName) :
       self.debug_incl_files [fileName] = 1

   # -- utilities --

   def showStatus (self, text) :
       # print (text)
       QCoreApplication.processEvents ()

   # -- tree --

   def openBranch (self, text) :
       item = TreeItem (self.current, text)
       self.current = item
       return item

   def closeBranch (self) :
       if self.current != None :
          item = self.current.parent ()
          if item != None :
             self.current = item

   def addItem (self, text) :
       item = TreeItem (self.current, text)
       return item

   # -- editor --

   def getEditor (self, fileInx) :
       fileName = indexToFileName (fileInx)
       edit = None
       if fileName in self.win.editors :
          edit = self.win.editors [fileName]
       return edit

   def openSource (self) :
       fileName = self.lexer.getFileName ()
       edit = self.win.reloadFile (fileName)

   def markText (self, color, begin_pos, end_pos, tooltip = None) :
       "set color in source window"
       lexer = self.lexer
       edit = self.getEditor (lexer.tokenFileInx)
       if edit != None :
          cursor = edit.textCursor ()
          cursor.setPosition (begin_pos)
          cursor.setPosition (end_pos, QTextCursor.KeepAnchor)
          format = cursor.charFormat ()
          format.setForeground (color)
          format.setProperty (Text.infoProperty, "") # no highlighting
          if tooltip != None :
             format.setToolTip (tooltip)
          cursor.setCharFormat (format)

   def markDeclaration (self, color, decl) :
       "set color in source window"
       lexer = self.lexer
       edit = self.getEditor (decl.src_file)
       if edit != None :
          cursor = edit.textCursor ()
          cursor.setPosition (decl.src_pos)
          cursor.select (QTextCursor.WordUnderCursor)
          format = cursor.charFormat ()
          format.setForeground (color)
          format.setProperty (Text.infoProperty, "") # no highlighting
          cursor.setCharFormat (format)

   def markDirective (self, color) :
       self.markText (color, self.directiveByteOfs, self.lexer.charByteOfs)

   def markToken (self, color) :
       self.markText (color, self.lexer.tokenByteOfs, self.lexer.charByteOfs)

   def markExpansion (self, defn) :
       self.markText (self.red, self.lexer.tokenByteOfs, self.lexer.charByteOfs)

   def markComment (self) :
       self.markText (self.plum, self.comment_location, self.lexer.charByteOfs)

   # -- tree --

   def treePosition (self, item, char_pos = False, directive_pos = False) :
       lexer = self.lexer
       if directive_pos :
          item.src_file = self.directiveFileInx
          item.src_line = self.directiveLineNum
          item.src_column = self.directiveColNum
          item.src_pos = self.directiveByteOfs
       elif char_pos :
          item.src_file = lexer.charFileInx
          item.src_line = lexer.charLineNum
          item.src_column = lexer.charColNum
          item.src_pos = lexer.charByteOfs
       else :
          item.src_file = lexer.tokenFileInx
          item.src_line = lexer.tokenLineNum
          item.src_column = lexer.tokenColNum
          item.src_pos = lexer.tokenByteOfs

   def treeToken (self, text, color) :
       "add token information into tree"
       lexer = self.lexer
       if lexer.token == lexer.eos :
          name = "< end of source >"
       else :
          name = lexer.tokenText

       item = self.addItem (text + " " + name)
       item.setInk (color)
       self.treePosition (item)

   # -- tree and editor --

   def putToken (self, cursor, color) :
       "add token to text document"
       format = cursor.charFormat ()
       format.setForeground (color)
       cursor.setCharFormat (format)
       cursor.insertText (self.lexer.tokenText)

   def openDirective (self, text, color) :
       "add directive into tree (and set color in source window)"
       item = self.openBranch (text)
       item.setInk (color)
       self.treePosition (item, directive_pos = True )

       # also mark directive in source text
       self.markDirective (color)
       return item

   def insertDirective (self, text, color) :
       item = self.openDirective (text, color)
       self.closeBranch ()
       return item

   # -- follow --

   def start (self, lexer) :
       self.lexer = lexer
       self.openSource ()

   def oneCharacter (self) :
       if 0 :
          lexer = self.lexer
          c = lexer.ch
          if c >= ' ' :
             txt = str (c)
             txt = quoteString (c, "'")
          else :
             txt = "ascii (" + str (ord (c)) + ")"
          item = self.addItem ("char " + txt)
          item.setInk (self.cornflowerblue)
          self.treePosition (item, char_pos = True)

   def whiteSpace (self) :
       if 0 :
          self.oneCharacter ()

   def startComment (self, delta) :
       if self.showComments :
          self.comment_location = self.lexer.charByteOfs - delta

   def comment (self) :
       if self.showComments :
          self.markComment ()

   def unusedToken (self) :
       if self.showUnusedTokens :
          # tree
          if self.showTokensInTree :
             self.treeToken ("unused token", self.gray)
          # source
          if 1 :
             self.markToken (self.gray)

   def oneToken (self, repeat = False) :
       if self.showTokens or len (self.description_stack) != 0 :
          # tree
          if self.showTokensInTree :
             self.treeToken ("token", self.brown)

          # source
          if 1 :
             self.markToken (self.brown)

          # macro expansion
          if len (self.description_stack) != 0 :
             desc = self.description_stack [-1]
             self.putToken (desc.source_cursor, self.brown)

          for desc in self.description_stack :
             self.putToken (desc.result_cursor, self.brown)

   def mark (self) :
       if 1 :
          stack = traceback.extract_stack()
          inx = len (stack) -3
          text = ""
          while inx > 0 :
             func_name = stack[inx][2]
             text = text + " " + func_name
             inx = inx - 1
          item = TreeItem (self.object_branch, "mark" + text)
          item.setInk (self.cornflowerblue)
          self.treePosition (item)

       if 1 :
          item = self.addItem ("mark")
          item.setInk (self.cornflowerblue)
          self.treePosition (item)

   def rewind (self) :
       if 1 :
          item = TreeItem (self.object_branch, "rewind")
          item.setInk (self.cornflowerblue)
          self.treePosition (item)

       if 1 :
          item = self.addItem ("rewind")
          item.setInk (self.cornflowerblue)
          self.treePosition (item)

   # -- directives --

   def startDirective (self) :
       self.directiveFileInx = self.lexer.tokenFileInx
       self.directiveLineNum = self.lexer.tokenLineNum
       self.directiveColNum = self.lexer.tokenColNum
       self.directiveByteOfs = self.lexer.tokenByteOfs

   def endDirective (self) :
       # self.markText (self.directiveByteOfs, self.lexer.charByteOfs, self.yellow)
       pass

   def unusedDirective (self) :
       if 1 :
          self.insertDirective ("unused directive", self.gray)

   def ifDirective (self) :
       if 1 :
          self.openDirective ("#if" + " " + str (self.lexer.use_input), self.green)

   def ifdefDirective (self) :
       if 1 :
          self.openDirective ("#ifdef" + " " + str (self.lexer.use_input), self.green)

   def ifndefDirective (self) :
       if 1 :
          self.openDirective ("#ifndef" + " " + str (self.lexer.use_input), self.green)

   def elifDirective (self) :
       if 1 :
          self.closeBranch ()
          self.openDirective  ("#elif" + " " + str (self.lexer.use_input), self.green)

   def elseDirective (self) :
       if 1 :
          self.closeBranch ()
          self.openDirective ("#else" + " " + str (self.lexer.use_input),  self.green)

   def endifDirective (self) :
       if 1 :
          self.closeBranch ()
          self.insertDirective ("#endif", self.green)

   def warningDirective (self, text) :
       if 1 :
          self.insertDirective ("#warning " + text, self.orange)

   def errorDirective (self, text) :
       if 1 :
          self.insertDirective ("#error " + text, self.red)

   def pragmaDirective (self, name) :
       if 1 :
          self.insertDirective ("#pragma " + name, self.orange)

   # -- include --

   def openInclude (self) :
       if 1 :
          self.openSource ()

          fileName = self.lexer.getFileName ()

          baseName = os.path.basename (fileName)
          if baseName in self.debug_incl_files :
             self.enableDebug ()

          if 1 :
             item = TreeItem (self.incl_branch, "include " + fileName)
             self.treePosition (item, directive_pos = True)
             item.setInk (self.green)

          self.openDirective ("#include " + fileName, self.green)
          self.showStatus (self.lexer.getFileName ())

          if self.showLinearInclude :
             self.include_stack.append (self.current)
             self.current = self.top
             item = self.openDirective ("#include " + fileName, self.limegreen)
             self.treePosition (item, directive_pos = True )

   def closeInclude (self) :
       if 1 :
          if self.showLinearInclude :
             self.closeBranch ()
             self.current = self.include_stack.pop ()
          self.closeBranch ()
          self.showStatus (self.lexer.getFileName ())

   def addIncludeDir (self, path) :
       TreeItem (self.incl_dir_branch, path)

   def skipMissingInclude (self, fileName) :
       if 1 :
          item = TreeItem (self.missing_incl_branch, fileName)
          self.treePosition (item, directive_pos = True)
       if 1 :
          item = self.addItem ("skip missing include " + fileName)
          item.setInk (self.orange)

   def skipKnownInclude (self, fileName) :
       if 1 :
          item = self.addItem ("skip known include " + fileName)
          item.setInk (self.orange)

   def skipIgnoredInclude (self, fileName) :
       if 1 :
          item = TreeItem (self.ignored_incl_branch, fileName)
          self.treePosition (item, directive_pos = True)
       if 1 :
          item = self.addItem ("skip ignored include " + fileName)
          item.setInk (self.orange)

   def alreadyIncluded (self, fileName) :
       if 1 :
          item = TreeItem (self.already_incl_branch, fileName)
          self.treePosition (item, directive_pos = True)
       if 1 :
          item = self.addItem ("already included " + fileName)
          item.setInk (self.orange)

   def storeGuard (self, key, value) :
       if 1 :
          node = TreeItem (self.guard_branch, key + " -> " + value)
          node.src_file = fileNameToIndex (key)
       if 1 :
          item = self.addItem ("guard " + key + " -> " + value)
          item.setInk (self.lime)

   def missingGuard (self) :
       fileName = self.lexer.getFileName ()
       if 1 :
          node = TreeItem (self.missing_guard_branch, fileName)
          node.src_file = fileNameToIndex (fileName)
       if 1 :
          item = self.addItem ("missing guard " + fileName)
          item.setInk (self.red)

   # -- define --

   def addMacro (self, defn) :
       if 1 :
          text = "define " + defn.name + " = " + defn.code
          node = TreeItem (self.macro_branch, text)
          node.src_file = defn.fileInx
          node.src_line = defn.lineNum
          node.setInk (self.blue)

   def undefMacro (self, name) :
       if 1 :
          item = TreeItem (self.macro_branch, "undef " + name)

   def defineDirective (self, defn) :
       if 1 :
          text = "define " + defn.name + " = " + defn.code
          node = TreeItem (self.macro_branch, text)
          node.src_file = defn.fileInx
          node.src_line = defn.lineNum
          node.setInk (self.blue)

       if 1 :
          self.openDirective ("#define " + defn.name, self.blue)
          if defn.params != None :
             for param in defn.params :
                item = self.addItem ("parameter " + param)
                item.setInk (self.blue)
          self.closeBranch ()

   def undefDirective (self, name) :
       if 1 :
          item = TreeItem (self.macro_branch, "undef " + name)
          self.treePosition (item, directive_pos = True)
          item.setInk (self.red)

       if 1 :
          self.insertDirective ("#undef " + name, self.blue)

   # -- expand macro --

   def expandMacro (self, defn) :
       if 1 :
          item = self.openBranch ("expand " + defn.name)
          item.setInk (self.red)
          self.treePosition (item)

          if len (self.description_stack) != 0 :
             desc = self.description_stack [-1]
             self.putToken (desc.source_cursor, self.red)

          # item.description = Description ()
          # item.description.defn_ref = defn
          # self.description_stack.append (item.description)
          # self.putToken (item.description.invoke_cursor, self.blue)

          self.markExpansion (defn)

   def closeExpand (self) :
       if 1 :
          self.closeBranch ()
          if len (self.description_stack) != 0 :
             self.description_stack.pop ()

   def openParameters (self) :
       if 1 :
          item = self.openBranch ("parameters")
          item.setInk (self.red)

          if len (self.description_stack) != 0 :
             desc = self.description_stack [-1]
             desc.in_parameters = True

   def closeParameters (self) :
       if 1 :
          self.closeBranch ()

          if len (self.description_stack) != 0 :
             desc = self.description_stack [-1]
             desc.in_parameters = False

   def openParam (self, param) :
       if 1 :
          item = self.openBranch ("parameter " + param)
          item.setInk (self.red)
          self.treePosition (item)

   def paramToken (self) :
       if 1 :
          # tree
          if 1 :
             self.treeToken ("parameter token", self.brown)

          # source
          if 1 :
             self.markToken (self.brown)

          # macro expansion
          if len (self.description_stack) != 0 :
             desc = self.description_stack [-1]
             self.putToken (desc.invoke_cursor, self.brown)

   def closeParam (self) :
       if 1 :
          self.closeBranch ()

   # -- objects --

   def openObject (self, data) :
       text = "object " + data.__class__.__name__
       if hasattr (data, "item_name") :
          text = text + " (" + data.item_name + ")"
       elif hasattr (data, "item_label") :
          text = text + " (" + data.item_label + ")"

       item = TreeItem (self.object_branch, text)
       item.obj = data # show data object in property window
       # self.treePosition (item)
       self.object_branch = item

   def reopenObject (self, data) :
       self.openObject (data)

   def closeObject (self) :
       self.object_branch = self.object_branch.parent ()

   # -- declarations --

   def declaration (self, decl) :
       if 1 :
          item = TreeItem (self.decl_branch, decl.item_name)
          item.setInk (self.blueviolet)
          item.obj = decl
          item.setupTreeItem ()
       if 1 :
          item = self.addItem ("declaration " + decl.item_name)
          item.setInk (self.blueviolet)
          item.obj = decl
          item.setupTreeItem ()
       if 1 :
          self.markDeclaration (self.blueviolet, decl)

   # -----------------------------------------------------------------------

   def compare (self) :
       lexer = self.lexer

       toFirst = False
       toSecond = False
       first = [ ]
       second = [ ]

       while not lexer.isEndOfSource () :
          if lexer.isKeyword ("@clear") :
             lexer.macros = { }
          elif lexer.isKeyword ("@start") :
             toFirst = True
             toSecond = False
             first = [ ]
             item = self.openBranch ("first")
             item.setInk (self.orange)
          elif lexer.isKeyword ("@compare") :
             toFirst = False
             toSecond = True
             second = [ ]
             self.closeBranch()
             item = self.openBranch ("second")
             item.setInk (self.orange)
          elif lexer.isKeyword ("@stop") :
             toFirst = False
             toSecond = False
             self.closeBranch()
             print ("FIRST  ", first)
             print ("SECOND", second)
             ok = len (first) == len (second)
             if ok :
                for inx in range (len (first)) :
                   if first [inx] != second [inx] :
                      ok = False
             if ok :
                item = self.addItem ("O.K.")
                item.setInk (self.lime)
                lexer.info ("O.K.")
             else  :
                item = self.addItem ("BAD")
                item.setInk (self.red)
                lexer.warning ("BAD")
          else :
             if toFirst :
                first.append (lexer.tokenToText ())
             if toSecond :
                second.append (lexer.tokenToText ())

          lexer.nextToken ()

# --------------------------------------------------------------------------

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
