#!/usr/bin/env python

from __future__ import print_function

import sys, os, importlib

from util import use_pyside2, use_qt5, use_python3, use_simple
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

work_dir = sys.path [0]
module_dirs = ["code", "grm", "cmm", "tutorial", "ev3", "pas", "_output"]
for local_dir in module_dirs :
    sys.path.insert (1, os.path.join (work_dir, local_dir))

from input import indexToFileName, fileNameToIndex

from util import findIcon, findColor, addColors, setApplStyle, resizeMainWindow, columnNumber, use_new_api, set_win, qstring_to_str

from edit import Editor, FindBox, GoToLineBox, Bookmark
from grep import GrepDialog
from options import Options, Notes
from tools import removeItems, setupItems

from tree import Tree, TreeItem
from small import GrammarTree, CompilerTree, lookupCompilerData, IdentifierTree, PythonTree

from window import CentralWindow

import input
import output
from lexer import readEmbeddedOptions

from input_support import Support
from output_sections import Sections

use_pas = False
use_ev3 = False

import gram_plugin

if use_pas :
   import pas_plugin

if use_ev3 :
   import ev3_plugin

import tutorial_plugin

# --------------------------------------------------------------------------

class ViewWindow (CentralWindow):

   def __init__ (self, parent = None) :
       super (ViewWindow, self).__init__ (parent)
       set_win (self) # store main window in util module
       addColors (self)

       self.currentProject = None
       self.loaded_modules = { }

       self.grep_dialog = GrepDialog (self)

       input.supportGenerator = self
       output.sectionGenerator = self

       resizeMainWindow (self)

       # project menu

       self.runMenu = self.menuBar().addMenu ("&Project")
       menu = self.runMenu

       act = QAction ("&Grep", self)
       act.setShortcut ("F2")
       act.setIcon (findIcon ("system-search"))
       act.triggered.connect (self.findInFiles)
       menu.addAction (act)

       act = QAction ("Grep (bottom view)", self)
       act.triggered.connect (self.grepWithOutputToInfo)
       menu.addAction (act)

       menu.addSeparator ()

       act = QAction ("Configure", self)
       act.setIcon (findIcon ("run-build-configure"))
       act.triggered.connect (self.configure)
       menu.addAction (act)

       act = QAction ("&Build", self)
       act.setShortcut ("F7")
       act.setIcon (findIcon ("run-build"))
       act.triggered.connect (self.build)
       menu.addAction (act)

       act = QAction ("&Make", self)
       act.setShortcut ("F8")
       act.triggered.connect (self.make)
       menu.addAction (act)

       act = QAction ("&Run", self)
       act.setIcon (findIcon ("system-run"))
       act.triggered.connect (self.run)
       menu.addAction (act)

       act = QAction ("&Debug", self)
       act.setIcon (findIcon ("debug-step-into"))
       act.triggered.connect (self.debug)
       menu.addAction (act)

       act = QAction ("Install", self)
       act.setIcon (findIcon ("run-build-install"))
       act.triggered.connect (self.install)
       menu.addAction (act)

       act = QAction ("Clean", self)
       act.setIcon (findIcon ("run-build-clean"))
       act.triggered.connect (self.clean)
       menu.addAction (act)

       menu.addSeparator ()

       act = QAction ("Run &Python", self)
       act.triggered.connect (self.run_python)
       act.setShortcut ("Shift+F7")
       menu.addAction (act)

       act = QAction ("Run &C++", self)
       act.triggered.connect (self.run_cpp)
       act.setShortcut ("Shift+F8")
       menu.addAction (act)

       menu.addSeparator ()

       act = QAction ("&Stop", self)
       act.setShortcut ("Ctrl+Esc")
       act.setIcon (findIcon ("process-stop"))
       act.triggered.connect (self.info.stop)
       menu.addAction (act)
       self.info.stopAction = act

       act = QAction ("&Clear output", self)
       act.setIcon (findIcon ("edit-clear"))
       act.triggered.connect (self.info.clearOutput)
       menu.addAction (act)

       # grammar menu

       gram_plugin.GrammarPlugin (self)

       # C -- menu

       # cmm_plugin.Plugin (self)
       self.pluginMenu ("&C--", "cmm_plugin", "Plugin", "cmm")

       # Pascal menu

       if use_pas:
          pas_plugin.PascalPlugin (self)

       # EV3 menu

       if use_ev3:
          ev3_plugin.EV3Plugin (self)

       # tutorial menu

       tutorial_plugin.TutorialPlugin (self)

       # settings menu

       self.settingsMenu = self.menuBar().addMenu ("&Settings")
       menu = self.settingsMenu

       act = QAction ("Re-read settings (view.ini, tools.ini)", self)
       act.setStatusTip ("Re-read settings from view.ini and tools.ini files")
       act.triggered.connect (self.refreshSettings)
       menu.addAction (act)

       act = QAction ("Re-read session (edit.ini)", self)
       act.setStatusTip ("Re-read session from edit.ini file")
       act.triggered.connect (self.reloadSession)
       menu.addAction (act)

       act = QAction ("Notes ...", self)
       act.triggered.connect (self.showNotesDialog)
       menu.addAction (act)

       # window and tabs menu

       self.additionalMenuItems ()

       # tools menu

       self.toolsMenu = self.toolsOrHelpMenu ("&Tools", "tool")
       menu = self.toolsMenu

       # help menu

       self.helpMenu = self.toolsOrHelpMenu ("&Help", "help")
       menu = self.helpMenu

   # Project menu

   def findInFiles (self) :
       self.leftTabs.setCurrentWidget (self.grep)
       self.grep_dialog.openDialog ()

   def grepWithOutputToInfo (self) :
       self.info.setVisible (True)
       self.grep_dialog.openDialog (output_to_info = True)

   def configure (self) :
       self.info.run ("configure")

   def build (self) :
       self.info.run ("build")

   def make (self) :
       self.info.run ("make")

   def run (self) :
       self.info.run ("run")

   def debug (self) :
       self.info.run ("debug")

   def clean (self) :
       self.info.run ("clean")

   def install (self) :
       self.info.run ("install")

   def run_python (self) :
       editor = self.getEditor ()
       self.checkModifiedOnDisk (editor)
       self.info.run ("run-python")

   def run_cpp (self) :
       editor = self.getEditor ()
       self.checkModifiedOnDisk (editor)
       fileName = editor.getFileName ()
       options = readEmbeddedOptions (fileName)
       self.info.clear ()
       self.info.run ("run-cpp", fileName + " " + options)

   # Settings

   def refreshSettings (self) :
       self.settings.sync ()
       self.commands.sync ()
       self.refreshToolsMenu ()
       self.refreshHelpMenu ()

   # Properties

   def showProperties (self, data) :
       self.prop.showProperties (data)
       self.rightTabs.setVisible (True) # !?
       self.rightTabs.setCurrentWidget (self.prop)
       # self.prop.setFocus ()

   def showNotesDialog (self) :
       Notes (self).show ()

   # Project

   def initProject (self, prj) :
       self.info.clearOutput ()
       self.classes.clear ()
       self.tree.clear ()
       if isinstance (prj, Editor) :
          fileName = prj.getFileName ()
          text = os.path.basename (fileName)
          node = TreeItem (self.project, text)
          node.setToolTip (0, fileName)
          node.setIcon (0, findIcon ("folder"))
          node.src_file = fileNameToIndex (fileName)
       elif isinstance (prj, str) :
          node = TreeItem (self.project, prj)
          node.setToolIcon (0, findIcon ("folder"))
       else :
          node = None # !?
       self.currentProject = node

   def joinProject (self, edit) :
       fileName = edit.getFileName ()
       text = os.path.basename (fileName)
       node = TreeItem (self.currentProject, text)
       node.setToolTip (0, fileName)
       node.setIcon (0, findIcon ("document-open"))
       node.src_file = fileNameToIndex (fileName)

   # Clases

   def showClasses (self, data) :
       IdentifierTree (self.classes, data)
       # self.classes.expandAll ()

   # Tree

   def displayFile (self, fileName) :
       branch = TreeItem (self.tree, "output " + os.path.basename (fileName))
       branch.src_file = fileNameToIndex (fileName)
       return branch

   def displayPythonCode (self, editor) :
       fileName =  editor.getFileName ()
       node = TreeItem (self.tree, "Python code " + os.path.basename (fileName))
       node.src_file = fileNameToIndex (fileName)
       node.addIcon ("code")
       PythonTree (node, editor)

   def displayGrammarData (self, editor, grammar) :
       editor.grammar_data = grammar # !?
       fileName =  editor.getFileName ()
       fileInx = fileNameToIndex (fileName)
       node = TreeItem (self.tree, "grammar " + os.path.basename (fileName))
       node.src_file = fileInx
       node.obj = grammar
       return GrammarTree (node, grammar, fileInx)

   def displayCompilerData (self, editor, data) :
       editor.compiler_data = data
       fileName =  editor.getFileName ()
       node = TreeItem (self.tree, "compiler data " + os.path.basename (fileName))
       node.src_file = fileNameToIndex (fileName)
       CompilerTree (node, data)
       return node

   def findCompilerData (self, editor, line, col) :
       self.leftTabs.setCurrentWidget (self.tree)
       lookupCompilerData (self.tree, editor, line, col)

   def displayObject (self, text, data) :
       node = TreeItem (self.tree, text)
       node.obj = data

   # Navigator

   def addNavigatorData (self, editor, data) :
       editor.navigator_data = data

   # Memo and References

   def showMemo (self, editor, name) :
       self.memo.showMemo (editor, name)

   def showReferences (self, editor, name) :
       self.references.showReferences (editor, name)

   # Input files

   def inputFile (self, fileName) :
       edit = self.refreshFile (fileName)
       if edit == None :
          raise  IOError ("File not found: " + fileName)
       # if edit.isModified () :
       #    edit.saveFile ()
       return edit

   def rebuildFile (self, source, target) :
       return not os.path.isfile (target) or os.path.getmtime (source) > os.path.getmtime (target)

   def createSupport (self, parser, fileName) :
       # print ("createSupport", fileName)
       edit = self.inputFile (fileName)

       # reset colors and properties, keep extra selection (bookmarks)
       edit.lastCursor = None
       cursor = edit.textCursor ()
       line = cursor.blockNumber () # remember line and column
       column = columnNumber (cursor)

       cursor.select (QTextCursor.Document) # select all
       cursor.setCharFormat (QTextCharFormat ())
       cursor.clearSelection () # unselect all

       cursor.movePosition (QTextCursor.Start)
       cursor.movePosition (QTextCursor.NextBlock, QTextCursor.MoveAnchor, line) # restore line and column
       cursor.movePosition (QTextCursor.NextCharacter, QTextCursor.MoveAnchor, column)
       edit.setTextCursor (cursor)

       return Support (parser, edit)

   # Output files

   def createDir (self, fileName) :
       dirName = os.path.dirname (fileName)
       if not os.path.isdir (dirName) :
          os.makedirs (dirName)

   def outputFileName (self, fileName, extension = "") :
       fileName = os.path.basename (fileName)
       fileName = os.path.join ("_output", fileName)
       if extension != "" :
          fileName, ext = os.path.splitext (fileName)
          if fileName.find ('-') >= 0 and extension.startswith ('_') :
             extension = extension.replace ('_', '-')
          fileName = fileName + extension
       fileName = os.path.abspath (fileName)
       self.createDir (fileName)
       return fileName

   def createSections (self, outputFileName) :
       outputEdit = self.rewriteFile (outputFileName) # empty output file
       outputEdit.closeWithoutQuestion = True
       # outputEdit.highlighter.enabled = False
       self.joinProject (outputEdit)

       # add node to tree window
       tree_branch = self.displayFile (outputFileName)

       # add node to navigator window
       branch = TreeItem (None)
       branch.setText (0, os.path.basename (outputFileName))
       self.addNavigatorData (outputEdit, branch) # make branch visible in navigator

       # add section nodes to navigator window
       sections = Sections (branch, outputEdit)
       return sections

   # Modules

   def loadModule (self, fileName) :
       module = None
       try :
          fileName = os.path.abspath (fileName)
          dirName = os.path.dirname (fileName)
          # sys.path.insert (0, dirName)
          # print ("LOAD", fileName)
          # for item in sys.path :
          #    print ("SYS PATH", item)
          name, ext = os.path.splitext (os.path.basename (fileName))
          if name in sys.modules :
             # print ("RELOAD", name)
             if use_python3 :
                importlib.reload (sys.modules [name])
             else :
                reload (sys.modules [name])
          module = importlib.import_module (name)
       finally :
          # del sys.path [0]
          pass

       return module

   def loadPlugin (self, module_dir, module_name, func_name) :
       m = self.loadModule (os.path.join (module_dir, module_name))
       f = getattr (m, func_name)
       f (self)

   # Plugin Menu

   def pluginMenu (self, title, module, cls, key = "") :
       menu = self.menuBar().addMenu (title)
       self.showPluginMenu (menu, module, cls, key)
       menu.aboutToShow.connect (lambda : self.showPluginMenu (menu, module, cls, key))

   def showPluginMenu (self, menu, module, cls, key) :
       menu.clear ()
       # menu.addAction ("module: " + module)
       # menu.addAction ("class: " + cls)
       # menu.addSeparator ()
       m = self.loadModule (module)
       c = getattr (m, cls)
       c (self, menu)
       # add menu items from tools.ini
       if key != "" :
          self.commands.sync ()
          setupItems (self, menu, key)

   # Tools or Help Menu

   def toolsOrHelpMenu (self, title, key) :
       menu = self.menuBar().addMenu (title)
       self.showToolsOrHelpMenu (menu, key)
       menu.aboutToShow.connect (lambda : self.showToolsOrHelpMenu (menu, key))
       return menu

   def showToolsOrHelpMenu (self, menu, key) :
       # add menu items from tools.ini
       self.commands.sync ()
       removeItems (self, menu)
       setupItems (self, menu, key)

   def refreshToolsMenu (win) :
       removeItems (win, win.toolsMenu)
       setupItems (win, win.toolsMenu, "tool")

   def refreshHelpMenu (win) :
       removeItems (win, win.helpMenu)
       setupItems (win, win.helpMenu, "help")

   # Plugin interface

   def addView (self, title, widget) :
       inx = self.firstTabWidget.addTab (widget, title)
       self.firstTabWidget.setCurrentIndex (inx)

   def fileNameToIndex (self, fileName) :
       return fileNameToIndex (fileName)

   def readFile (self, fileName) :
       edit = self.loadFile (fileName)
       # edit = self.refreshFile (fileName)
       return qstring_to_str (edit.toPlainText ())

   def treeBranch (self, text = "") :
       node = TreeItem (self.tree, text)
       self.leftTabs.setCurrentWidget (self.tree)
       self.tree.setCurrentItem (node)
       return node

   def treeItem (self, above, text = "") :
       node = TreeItem (above, text)
       return node

   # Utilities

   def runPython (self, fileName) :
       self.info.run ("run-python", fileName)

   def showHtml (self, fileName) :
       self.info.run ("show-html", fileName)

   def showPreview (self, fileName) :
       self.info.run ("show-preview", fileName)

   def showPdf (self, fileName) :
       self.info.run ("show-pdf", fileName)

   def showLout (self, fileName, toPdf = False) :
       # create PDF or PostScript file

       subdir = os.path.dirname (fileName)
       save_dir = os.getcwd ()
       os.chdir (subdir)

       localName = os.path.basename (fileName) # local file name

       if toPdf :

          pdfFileName, ext = os.path.splitext (localName)
          pdfFileName = pdfFileName + ".pdf"

          os.system ("lout" + " " +  localName + " -PDF -o " + pdfFileName)
          self.showPdf (pdfFileName)

       else :

          psFileName, ext = os.path.splitext (localName)
          psFileName = psFileName + ".ps"

          # yum install lout
          os.system ("lout" + " " +  localName + " -o " + psFileName)
          # lout also creates .li file in current directory

          self.showPdf (psFileName)

       os.chdir (save_dir)

# --------------------------------------------------------------------------

if 0 :
   import traceback

   def handle_exception(exc_type, exc_value, exc_traceback):
     """ handle all exceptions """

     filename, line, dummy, dummy = traceback.extract_tb( exc_traceback ).pop()
     filename = os.path.basename( filename )
     error    = "%s: %s" % ( exc_type.__name__, exc_value )

     print ("A critical error has occured. file:", filename, "line: ", line)
     print
     print ("".join(traceback.format_exception(exc_type, exc_value, exc_traceback)))
     # sys.exit(1)

   # install handler for exceptions
   sys.excepthook = handle_exception

# --------------------------------------------------------------------------

app = QApplication (sys.argv)
setApplStyle (app)
win = ViewWindow ()
app.win = win
win.appl = app
win.show ()

win.info.redirectOutput ()

app.exec_ ()

# --------------------------------------------------------------------------

# Fedora: dnf install ...
#   PyQt4 PyQt4-webkit
#   python3-qt5 python3-qt5-webkit python3-qt5-webengine

# Debian: apt-get install ...
#   python-qt4
#   python3-pyqt5

# Archlinux: pacman -S ...
#   python-pyqt5

# --------------------------------------------------------------------------

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
