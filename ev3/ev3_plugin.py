
# ev3_plugin.py

from __future__ import print_function

import os, sys, importlib # , traceback

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

from input import fileNameToIndex
from grammar import Grammar
from toparser  import ToParser
from toproduct import ToProduct

from tree import TreeItem

# --------------------------------------------------------------------------

class EV3Plugin (QObject) :

   def __init__ (self, main_window) :
       super (EV3Plugin, self).__init__ (main_window)
       self.win = main_window

       self.pluginMenu = self.win.menuBar().addMenu ("EV3")
       self.pluginMenu.aboutToShow.connect (self.onShowMenu)

       act = QAction ("Pascal &Make", self.win)
       # act.setShortcut ("Shift+F11")
       act.triggered.connect (self.pascalCompile)
       self.pluginMenu.addAction (act)

       act = QAction ("Pascal &Build", self.win)
       # act.setShortcut ("Shift+F12")
       act.triggered.connect (self.pascalBuild)
       self.pluginMenu.addAction (act)

   def onShowMenu (self) :
       pass

   def pascalCompile (self) :
       self.build (rebuild = False)

   def pascalBuild (self) :
       self.build (rebuild = True)

   def build (self, rebuild) :

       sourceFileName = "ev3/examples/example.pas"

       grammarFileName = "ev3/ev3pas.g"
       parserFileName = self.win.outputFileName (grammarFileName, "_parser.py")
       productFileName = self.win.outputFileName (grammarFileName, "_product.py")

       sourceEdit = self.win.inputFile (sourceFileName)
       self.win.initProject (sourceEdit)

       if ( rebuild or
            self.win.rebuildFile (grammarFileName, parserFileName) or
            self.win.rebuildFile (grammarFileName, productFileName) ) :

          # parser

          print ("generating parser")
          self.win.showStatus ("generating parser")

          grammarEdit = self.win.inputFile (grammarFileName)

          grammar = Grammar ()
          grammar.openFile (grammarFileName)

          product = ToParser ()
          product.open (parserFileName)
          product.parserFromGrammar (grammar)
          product.close ()

          self.win.joinProject (grammarEdit)
          self.win.displayGrammarData (grammarEdit, grammar)

          parserEdit = self.win.reloadFile (parserFileName)
          self.win.joinProject (parserEdit)
          self.win.displayPythonCode (parserEdit)

          print ("parser O.K.")

          # product

          parserModuleName, ext = os.path.splitext (os.path.basename (parserFileName))

          product = ToProduct ()
          product.open (productFileName)
          product.productFromGrammar (grammar, parserModuleName)
          product.close ()

          productEdit = self.win.reloadFile (productFileName)
          self.win.joinProject (productEdit)
          self.win.displayPythonCode (productEdit)

          print ("product O.K.")
          self.win.showStatus ("")

       # run parser

       parser_module = self.win.loadModule (parserFileName)
       compiler_module = self.win.loadModule ("ev3pas_comp")

       compiler = compiler_module.Compiler ()
       compiler.pascal = True

       sourceEdit.highlighter.enabled = False # !?

       compiler.openFile (sourceFileName, with_support = True)
       result = compiler.parse_module_decl ()
       compiler.close ()

       self.win.displayCompilerData (sourceEdit, result)
       self.win.showClasses (compiler.global_scope)
       self.win.addNavigatorData (sourceEdit, compiler.global_scope)

       print ("run parser O.K.")

       # run product

       outputFileName = self.win.outputFileName (sourceFileName, "_output.pas")

       product_module = self.win.loadModule (productFileName)
       product = product_module.Product ()

       product.open (outputFileName, with_sections = True)
       product.send_module_decl (result)
       product.close ()

       print ("run product O.K.")

       # p2c

       outputFileName = self.win.outputFileName (sourceFileName, "_p2c.cpp")

       p2c_module = self.win.loadModule ("ev3p2c.py")
       p2c_object = p2c_module.P2C ()

       p2c_object.open (outputFileName, with_sections = True)
       p2c_object.send_module_decl (result)
       p2c_object.close ()

       print ("Pascal to C++ O.K.")

       # instructions

       outputFileName = self.win.outputFileName (sourceFileName, "_instr.txt")
       # edit.highlighter.enabled = False # !?

       instr = compiler_module.Instructions ()
       instr.open (outputFileName, with_sections = True)
       instr.code_module_decl (result)
       instr.close ()

       print ("Pascal Instructions O.K.")

       outputEdit = self.win.loadFile (outputFileName)
       if self.win.firstTabWidget.currentWidget ()  == outputEdit :
          self.win.moveEditor (self.win.firstTabWidget, self.win.rightTabs)
       self.win.alternate_tab_widget = self.win.rightTabs

       # show source

       self.win.loadFile (sourceFileName)

# --------------------------------------------------------------------------

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
