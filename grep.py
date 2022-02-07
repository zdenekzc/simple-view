#!/usr/bin/env python

import os, sys

from util import use_pyside2, use_qt5, simple_bytearray_to_str, qstring_to_str
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

# --------------------------------------------------------------------------

class GrepDialog (QDialog) :

    def __init__ (self, win, output_to_info = False) :
        super (GrepDialog, self).__init__ (win)

        self.win = win
        self.output_to_info = output_to_info

        self.setWindowTitle ("Find in Files")

        layout = QGridLayout ()
        self.setLayout (layout)

        label = QLabel ("Find:")
        layout.addWidget (label, 0, 0)

        self.pattern = QLineEdit ()
        layout.addWidget (self.pattern, 0, 1)

        label = QLabel ("Case Sensitive:")
        layout.addWidget (label, 1, 0)

        self.caseSensitive = QCheckBox ()
        layout.addWidget (self.caseSensitive, 1, 1)

        label = QLabel ("Whole words:")
        layout.addWidget (label, 2, 0)

        self.wholeWords = QCheckBox ()
        layout.addWidget (self.wholeWords, 2, 1)

        label = QLabel ("Regular expression:")
        layout.addWidget (label, 3, 0)

        self.regularExpression = QCheckBox ()
        layout.addWidget (self.regularExpression, 3, 1)

        label = QLabel ("Directory:")
        layout.addWidget (label, 4, 0)

        self.directory = QComboBox ()
        self.directory.setEditable (True)
        self.directory.insertItem (0, ".")
        self.directory.insertItem (1, "..")
        layout.addWidget (self.directory, 4, 1)

        box = QDialogButtonBox (QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addWidget (box, 5, 1)

        box.accepted.connect (self.search)
        box.rejected.connect (self.reject)

    def openDialog (self, output_to_info = False) :
        self.output_to_info = output_to_info
        self.pattern.selectAll ()
        self.show ()

    def search (self) :
        params = self.pattern.text ()
        params = qstring_to_str (params)
        params.strip ()
        if self.win != None and params != "" :
           if not self.caseSensitive.isChecked () :
              params = "-i " + params
           if self.wholeWords.isChecked () :
              params = "-w " + params
           if not self.regularExpression.isChecked () :
              params = "-F " + params
           path = self.directory.currentText ()
           path = qstring_to_str (path)
           path.strip ()
           if path == "" :
              path = "."
           params = params + " -R " + path
           self.accept ()
           if self.output_to_info :
              # grep with output to info window
              self.win.info.grep (params)
           else :
              # grep with output to tree
             self.win.grep.grep (params)

# --------------------------------------------------------------------------

class GrepWin (QWidget) :

    def __init__ (self, win) :
        super (GrepWin, self).__init__ (win)

        self.win = win
        self.initVariables ()

        layout = QVBoxLayout ()
        self.setLayout (layout)

        self.tree = QTreeWidget ()
        self.tree.header ().hide ()
        self.tree.itemActivated.connect (self.onItemActivated)
        layout.addWidget (self.tree)

        self.stopButton = QPushButton ()
        self.stopButton.setText ("stop")
        self.stopButton.setEnabled (False)
        self.stopButton.clicked.connect (self.stopProcess)
        layout.addWidget (self.stopButton)

    def initVariables (self) :
        self.lastFileName = ""
        self.branch = None
        self.initLineVariables ()

    def initLineVariables (self,) :
        self.startLine = True
        self.middle = False
        self.fileName = ""
        self.lineNum = 0
        self.text = ""

    def showItem (self) :
        if self.text != "" :
           if self.fileName != self.lastFileName :
              self.branch = None
           if self.branch == None :
              self.branch = QTreeWidgetItem ()
              self.branch.setText (0, self.fileName)
              self.branch.setForeground (0, QColor (Qt.darkGreen))
              self.branch.fileName = os.path.abspath (self.fileName)
              self.tree.addTopLevelItem (self.branch)
              self.lastFileName = self.fileName
           node = QTreeWidgetItem ()
           node.setText (0, "Line " + str (self.lineNum) + ": " + self.text)
           node.src_line = self.lineNum
           self.branch.addChild (node)

    def dataReady (self) :
        data = simple_bytearray_to_str (self.process.readAll ())
        for c in data :
           if c == '\n' :
              self.showItem ()
              self.initLineVariables ()
           elif self.startLine :
              if c != ':' :
                 self.fileName = self.fileName + c
              else :
                 self.startLine = False
                 self.middle = True
           elif self.middle :
              if c != ':' :
                 if c >= '0' and c <= '9' :
                    self.lineNum = 10 * self.lineNum + ord (c) - ord ('0')
              else :
                 self.middle = False
           else :
              self.text = self.text + c

    def stopProcess (self) :
        self.process.terminate ()

    def onItemActivated (self, node, column) :
        fileName = ""
        line = 0

        if hasattr (node, "src_line") :
           line = node.src_line

        while fileName == "" and node != None :
           if hasattr (node, "fileName") :
              fileName = node.fileName
           node = node.parent ()

        if fileName != None :
           if self.win != None :
              self.win.loadFile (fileName, line)

    def grep (self, params) :
        self.tree.clear ()
        self.initVariables ()

        self.process = QProcess (self)
        self.process.setProcessChannelMode (QProcess.MergedChannels)
        self.process.readyRead.connect (self.dataReady)
        self.process.started.connect (lambda: self.stopButton.setEnabled (True))
        self.process.finished.connect (lambda: self.stopButton.setEnabled (False))
        params = "-n " + params # line numbers
        self.process.start ("/bin/sh", [ "-c", "grep " + params + " -r ." ] )

# http://stackoverflow.com/questions/22069321/realtime-output-from-a-subprogram-to-stdout-of-a-pyqt-widget

# --------------------------------------------------------------------------

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
