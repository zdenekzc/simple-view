#!/usr/bin/env python

from __future__ import print_function

import sys

try :
   from PyQt5.QtCore import *
   from PyQt5.QtGui import *
   from PyQt5.QtWidgets import *
except :
   from PyQt4.QtCore import *
   from PyQt4.QtGui import *

from mini_lexer import Lexer, LexerException

# --------------------------------------------------------------------------

class Highlighter (QSyntaxHighlighter) :
    def __init__ (self, parent = None) :
        super (Highlighter, self).__init__ (parent)
        self.lexer = Lexer ()

        self.identifierFormat = QTextCharFormat ()
        self.identifierFormat.setForeground (Qt.darkRed)
        self.identifierFormat.setToolTip ("identifier")

        self.numberFormat = QTextCharFormat ()
        self.numberFormat.setForeground (Qt.cyan)

        self.realFormat = QTextCharFormat ()
        self.realFormat.setForeground (Qt.magenta)

        self.characterFormat = QTextCharFormat ()
        self.characterFormat.setForeground (QColor ("cornflowerblue"))

        self.stringFormat = QTextCharFormat ()
        self.stringFormat.setForeground (Qt.blue)

        self.separatorFormat = QTextCharFormat ()
        self.separatorFormat.setForeground (QColor ("orange"))

        self.commentFormat = QTextCharFormat ()
        self.commentFormat.setForeground (Qt.gray)

    def highlightBlock (self, text) :
        try :
           lexer = self.lexer
           lexer.openString (text)
           while not lexer.isEndOfSource () :
              index = lexer.tokenByteOfs - 1
              length = lexer.charByteOfs - lexer.tokenByteOfs
              if lexer.token == lexer.identifier :
                 self.setFormat (index, length, self.identifierFormat)
              elif lexer.token == lexer.number :
                 self.setFormat (index, length, self.numberFormat)
              elif lexer.token == lexer.real_number :
                 self.setFormat (index, length, self.realFormat)
              elif lexer.token == lexer.character_literal :
                 self.setFormat (index, length, self.characterFormat)
              elif lexer.token == lexer.string_literal :
                 self.setFormat (index, length, self.stringFormat)
              elif lexer.token == lexer.separator :
                 self.setFormat (index, length, self.separatorFormat)
              else : # !?
                 self.setFormat (index, length, self.commentFormat)
              lexer.nextToken ()
        except :
           pass

# --------------------------------------------------------------------------

class Edit (QTextEdit) :
    def __init__ (self, parent=None) :
        super (Edit, self).__init__ (parent)
        self.highlighter = Highlighter (self.document ())

    def selectLine (self, line) :
        cursor = self.textCursor ()
        cursor.movePosition (QTextCursor.Start)
        cursor.movePosition (QTextCursor.Down, QTextCursor.MoveAnchor, line-1)
        cursor.movePosition (QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
        self.setTextCursor (cursor)

    def select (self, line, col, stop_line, stop_col):
        cursor = self.textCursor ()

        cursor.movePosition (QTextCursor.Start)
        cursor.movePosition (QTextCursor.Down, QTextCursor.MoveAnchor, line-1)
        cursor.movePosition (QTextCursor.Right, QTextCursor.MoveAnchor, col-1)

        if stop_line == line :
           cursor.movePosition (QTextCursor.Right, QTextCursor.KeepAnchor, stop_col-col)
        else :
           cursor.movePosition (QTextCursor.Down, QTextCursor.KeepAnchor, stop_line-line)
           cursor.movePosition (QTextCursor.StartOfLine, QTextCursor.KeepAnchor)
           cursor.movePosition (QTextCursor.Right, QTextCursor.KeepAnchor, stop_col)

        self.setTextCursor (cursor)

# --------------------------------------------------------------------------

def findIcon (icon_name) :
    return QIcon.fromTheme (icon_name)

class TreeItem (QTreeWidgetItem) :
    def __init__ (self, parent, text) :
        super (TreeItem, self).__init__ (parent)
        self.setText (0, text)
        self.setForeground (0, QColor ("blue"))

    def addIcon (self, icon_name) :
        self.setIcon (0, findIcon (icon_name))

class TreeView (QTreeWidget) :
    def __init__ (self, parent=None) :
        super (TreeView, self).__init__ (parent)
        self.setColumnCount (1)
        self.header ().hide ()
        self.setEditTriggers (QAbstractItemView.SelectedClicked)
        self.setIndentation (8)

# --------------------------------------------------------------------------

class MainWin (QMainWindow) :

    def __init__ (self, parent=None) :
        super (MainWin, self).__init__ (parent)

        self.current = None
        self.last = None

        self.resize (640, 480)

        self.split = QSplitter ()
        self.setCentralWidget (self.split)

        self.tree = TreeView ()
        self.split.addWidget (self.tree)

        self.tree.itemActivated.connect (self.onItemActivated)

        self.edit = Edit ()
        self.split.addWidget (self.edit)
        self.edit.setLineWrapMode (QTextEdit.NoWrap) # otherwise selectLine is not exact

        fileMenu = self.menuBar().addMenu ("&File")

        act = QAction ("&Open...", self)
        act.setShortcut ("Ctrl+O")
        act.triggered.connect (self.openFile)
        fileMenu.addAction (act)

        act = QAction ("&Run", self)
        act.setShortcut ("Ctrl+R")
        act.triggered.connect (self.run)
        fileMenu.addAction (act)

        act = QAction ("&Quit", self)
        act.setShortcut ("Ctrl+Q")
        act.triggered.connect (self.close)
        fileMenu.addAction (act)

    def onItemActivated (self, item, column) :
        if hasattr (item, "line") :
           self.edit.selectLine (item.line)

    def clearTree (self) :
        self.tree.clear ()
        self.current = None
        self.last = None

    def readFile (self, fileName) :
        f = open (fileName, "r")
        source = f.read ()
        self.edit.setPlainText (source)
        self.clearTree()

    def openFile (self) :
        fileName = QFileDialog.getOpenFileName (self, "Open File") [0]
        if fileName :
           self.readFile (fileName)

    def openBranch (self, txt) :
        above = self.current
        if above == None :
           above = self.tree
        self.last = TreeItem (above, txt)
        self.current = self.last

    def closeBranch (self) :
        if self.current != None :
           self.current = self.current.parent()

    def put (self, txt) :
        self.openBranch (txt)
        self.closeBranch ()

    def setLine (self, lexer) :
        if self.last != None :
           self.last.line = lexer.tokenLineNum

    # ----------------------------------------------------------------------

    # simple statements

    def readIdent (self, lexer) :
        result = lexer.tokenText
        if not lexer.isIdentifier () :
           lexer.error ("Identifier expected")
        lexer.nextToken ()
        return result

    def parseExpr (self, lexer) :
        a = self.readIdent (lexer)
        self.put ("expression " + a )

    def parseSimpleStat (self, lexer) :
        a = self.readIdent (lexer)
        lexer.checkSeparator ('=')
        b = self.readIdent (lexer)
        lexer.checkSeparator (';')
        self.put ("simple " + a + " = " + b)

    def parseWhile (self, lexer) :
        self.openBranch ("while")
        self.setLine (lexer)
        lexer.checkKeyword ("while")
        lexer.checkSeparator ('(')
        self.parseExpr (lexer)
        lexer.checkSeparator (')')
        self.parseStat (lexer)
        self.closeBranch ()

    def parseIf (self, lexer) :
        self.openBranch ("if")
        self.setLine (lexer)
        lexer.checkKeyword ("if")
        lexer.checkSeparator ('(')
        self.parseExpr (lexer)
        lexer.checkSeparator (')')

        self.openBranch ("then")
        self.parseStat (lexer)
        self.closeBranch ()

        if lexer.isKeyword ("else") :
           lexer.nextToken () # preskoc else
           self.openBranch ("else")
           self.parseStat (lexer)
           self.closeBranch ()
        self.closeBranch ()

    def parseStat (self, lexer) :
        if lexer.isKeyword ("if") :
           self.parseIf (lexer)
        elif lexer.isKeyword ("while") :
           self.parseWhile (lexer)
        else :
           self.parseSimpleStat (lexer)

    # ----------------------------------------------------------------------

    # Table

    def parseValue (self, lexer) :
        lexer.nextToken () # skip name
        lexer.checkSeparator ('=')
        if lexer.token == lexer.string_literal :
           result = lexer.tokenText
           lexer.nextToken () # skip string
        else :
           lexer.error ("Value expected (as string)");

        # lexer.checkSeparator (';')

        # if lexer.isSeparator (';') :
        #    lexer.nextToken ()

        if not lexer.isSeparator ('}') :
           lexer.checkSeparator (';')

        return result

    def parseColumn (self, lexer) :
        self.openBranch ("Column")
        self.setLine (lexer)
        lexer.nextToken () # skip column
        lexer.checkSeparator ('{')
        while not lexer.isSeparator ('}') :
            if lexer.isKeyword ("name") :
               name = self.parseValue (lexer)
               self.put ("Name " + name)
            elif lexer.isKeyword ("type") :
               type = self.parseValue (lexer)
               self.put ("Type " + type)
            else :
               lexer.error ("Unknown column statement");
        lexer.checkSeparator ('}')
        self.closeBranch ()

    def parseTable (self, lexer) :
        self.openBranch ("Table")
        self.setLine (lexer)
        lexer.nextToken () # skip table
        lexer.checkSeparator ('{')
        while not lexer.isSeparator ('}') :
            if lexer.isKeyword ("name") :
               name = self.parseValue (lexer)
               self.put ("Name " + name)
            elif lexer.isKeyword ("column") :
               self.parseColumn (lexer)
            else :
               lexer.error ("Unknown table statement");

        lexer.checkSeparator ('}')
        self.closeBranch ()

    # ----------------------------------------------------------------------

    # run example

    def run (self) :
        try :
           self.clearTree ()
           source = self.edit.toPlainText ()

           lexer = Lexer ()
           lexer.openString (source)

           if 0 :
              self.openBranch ("tokens")
              while not lexer.isEndOfSource () :
                 self.put (lexer.tokenText)
                 lexer.nextToken ()
              self.closeBranch ()

           if 1:
              while not lexer.isEndOfSource () :
                 if lexer.isKeyword ("table") :
                    self.parseTable (lexer)
                 else :
                    self.parseStat (lexer)

        except LexerException as e :
           print ("ERROR", str (e))
        # except LexerException as e :
        #    print ("ERROR")

# --------------------------------------------------------------------------

app = QApplication (sys.argv)
QIcon.setThemeName ("oxygen")
win = MainWin ()
# win.edit.setFont (QFont ("Sans Serif", 16))
# win.tree.setFont (win.edit.font ())
win.show ()
win.readFile ("mini_input.txt")
# win.readFile ("mini_table.txt")
win.run ()
app.exec_ ()

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
