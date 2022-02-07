#!/usr/bin/env python

from __future__ import print_function

import os, sys, importlib, traceback

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

from grammar   import Grammar # , Rule, Expression, Alternative, Ebnf, Nonterminal, Terminal
from toparser  import ToParser
from toproduct import ToProduct

from util import findColor

# --------------------------------------------------------------------------

class TutorialPlugin (QObject) :

   def __init__ (self, main_window) :
       super (TutorialPlugin, self).__init__ (main_window)
       self.win = main_window

       self.exampleMenu = self.win.menuBar().addMenu ("Tutorial")

       act = QAction ("cecko.g", self.win)
       act.triggered.connect (self.test_cecko)
       self.exampleMenu.addAction (act)

       self.exampleMenu.addSeparator ()

       act = QAction ("cecko2.g", self.win)
       act.triggered.connect (self.test_cecko2)
       self.exampleMenu.addAction (act)

       act = QAction ("cecko2.g lout", self.win)
       act.triggered.connect (self.test_cecko2_lout)
       self.exampleMenu.addAction (act)

       self.exampleMenu.addSeparator ()

       act = QAction ("cecko3.g", self.win)
       act.triggered.connect (self.test_cecko3)
       # act.setShortcut ("Shift+F10")
       self.exampleMenu.addAction (act)

       act = QAction ("cecko3.g Python Qt", self.win)
       act.triggered.connect (self.test_cecko3_python)
       # act.setShortcut ("Ctrl+F10")
       self.exampleMenu.addAction (act)

       act = QAction ("cecko3.g Qt", self.win)
       # act.setShortcut ("Alt+F10")
       act.triggered.connect (self.test_cecko3_qt)
       self.exampleMenu.addAction (act)

       self.exampleMenu.addSeparator ()

       act = QAction ("cecko4.g", self.win)
       # act.setShortcut ("F10")
       act.triggered.connect (self.test_cecko4)
       self.exampleMenu.addAction (act)

   def test_cecko (self) :
       self.grammarFileName = "tutorial/cecko.g"
       self.sourceFileName = "tutorial/c1.cc"
       self.test (run = False, rebuild = True)

   def test_cecko2 (self) :
       self.grammarFileName = "tutorial/cecko2.g"
       self.sourceFileName = "tutorial/c2.cc"
       self.test (show_product = True, rebuild = True)

   def test_cecko2_lout (self) :
       self.grammarFileName = "tutorial/cecko2.g"
       self.sourceFileName = "tutorial/c2.cc"
       result = self.test ()
       self.toLout ("tutorial/cecko2_to_lout.py", result)

   def test_cecko3 (self) :
       self.grammarFileName = "tutorial/cecko3.g"
       self.sourceFileName = "tutorial/c3.cc"
       self.test (show_product = True, compilerFileName = "tutorial/cecko3_compiler.py", rebuild = True)
       self.win.loadFile (self.sourceFileName) # show source

   def test_cecko3_python (self) :
       self.grammarFileName = "tutorial/cecko3.g"
       self.sourceFileName = "tutorial/c3win.cc"
       result = self.test (compilerFileName = "tutorial/cecko3_compiler.py")
       self.toPython ("tutorial/cecko3_to_python.py", result, with_qt = True)

   def test_cecko3_qt (self) :
       self.grammarFileName = "tutorial/cecko3.g"
       self.sourceFileName = "tutorial/c3qt.cc"
       result = self.test (compilerFileName = "tutorial/cecko3_compiler.py")
       self.toQt (result)

   def test_cecko4 (self) :
       self.grammarFileName = "tutorial/cecko4.g"
       self.sourceFileName = "tutorial/c4.cc"
       result = self.test (compilerFileName = "tutorial/cecko4_compiler.py")
       self.writeInstructions ("tutorial/cecko4_instr.py", result)
       self.win.loadFile (self.sourceFileName) # show source

   # -----------------------------------------------------------------------

   # parse and run

   def test (self, run = True, show_product = False, compilerFileName = "", rebuild = False) :

       shortName, ext = os.path.splitext (os.path.basename (self.grammarFileName))

       parserFileName = self.win.outputFileName (shortName + "_parser.py")
       productFileName = self.win.outputFileName (shortName + "_product.py")

       sourceEdit = self.win.inputFile (self.sourceFileName)
       self.win.initProject (sourceEdit)

       if ( rebuild or
            self.win.rebuildFile (self.grammarFileName, parserFileName) or
            self.win.rebuildFile (self.grammarFileName, productFileName) ) :

            # parser

            print ("generating parser")
            self.win.showStatus ("generating parser")

            self.win.inputFile (self.grammarFileName) # save if modified

            grammar = Grammar ()
            grammar.openFile (self.grammarFileName)

            parser_generator = ToParser ()
            parser_generator.open (parserFileName)
            parser_generator.parserFromGrammar (grammar)
            parser_generator.close ()

            grammarEdit = self.win.inputFile (self.grammarFileName)
            self.win.joinProject (grammarEdit)
            self.win.displayGrammarData (grammarEdit, grammar)

            parserEdit = self.win.reloadFile (parserFileName)
            self.win.joinProject (parserEdit)
            self.win.displayPythonCode (parserEdit)

            print ("parser O.K.")

            # product

            if run :
               parserModuleName, ext = os.path.splitext (os.path.basename (parserFileName))

               product_generator = ToProduct ()
               product_generator.open (productFileName)
               product_generator.productFromGrammar (grammar, parserModuleName)
               product_generator.close ()

               productEdit = self.win.reloadFile (productFileName)
               self.win.joinProject (productEdit)
               self.win.displayPythonCode (productEdit)

               print ("product O.K.")

            self.win.showStatus ("")

       result = None

       # run parser

       if run :
          parser_module = self.win.loadModule (parserFileName) # load parser module (required for compile_module)
          self.parser_module = parser_module # store for diagram drawing

          if compilerFileName == "" :
             parser_object = parser_module.Parser ()

             parser_object.openFile (self.sourceFileName)
             result = parser_object.parse_program ()
             parser_object.close ()

             self.win.displayCompilerData (sourceEdit, result)

          else :
             compiler_module = self.win.loadModule (compilerFileName)
             self.compiler_module = compiler_module # store for instruction generation

             compiler_object = compiler_module.Compiler ()

             compiler_object.openFile (self.sourceFileName, with_support = True)
             result = compiler_object.parse_program ()
             compiler_object.close ()

             self.win.displayCompilerData (sourceEdit, result)
             self.win.showClasses (result)
             self.win.addNavigatorData (sourceEdit, result)

          print ("run parser O.K.")

       # run product

       if run :
          outputFileName = self.win.outputFileName (self.sourceFileName, "_output.cpp")

          product_module = self.win.loadModule (productFileName)
          product_object = product_module.Product ()

          product_object.open (outputFileName)
          product_object.send_program (result)
          product_object.close ()

          productEdit = self.win.reloadFile (outputFileName)
          self.win.joinProject (productEdit)
          if show_product :
             self.win.displayFile (outputFileName)

          print ("run product O.K.")

       return result

   # -----------------------------------------------------------------------

   # run tool

   def tool (self, compiler_data, toolFileName, toolClassName, outputSuffix = "_output.py") :

       outputFileName = self.win.outputFileName (self.sourceFileName, outputSuffix)

       tool_module = self.win.loadModule (toolFileName)
       tool_class = getattr (tool_module, toolClassName)
       tool_object = tool_class ()

       tool_object.open (outputFileName, with_sections = True)
       tool_object.send_program (compiler_data)
       tool_object.close ()

       self.win.reloadFile (outputFileName)

       print ("O.K.")

   # -----------------------------------------------------------------------

   # generate instructions

   def writeInstructions (self, instrModuleFileName, result) :

       outputFileName = self.win.outputFileName (self.sourceFileName, "_instr.txt")

       module = self.win.loadModule (instrModuleFileName)
       instr = module.Instructions ()
       instr.open (outputFileName, with_sections = True)
       instr.code_program (result)
       instr.close ()

       print ("Instructions O.K.")

       outputEdit = self.win.loadFile (outputFileName)
       if 0 :
          if self.win.firstTabWidget.currentWidget ()  == outputEdit :
             self.win.moveEditor (self.win.firstTabWidget, self.win.rightTabs)
          self.win.alternate_tab_widget = self.win.rightTabs

   # -----------------------------------------------------------------------

   # Lout

   def toLout (self, loutModuleFileName, result) :
       outputFileName = self.win.outputFileName (self.sourceFileName, "_output.lout")

       lout_module = self.win.loadModule (loutModuleFileName)
       lout_object = lout_module.ExampleToLout ()

       lout_object.open (outputFileName)
       lout_object.send_program (result)
       lout_object.close ()

       outputEdit = self.win.reloadFile (outputFileName)
       self.win.joinProject (outputEdit)
       self.win.displayFile (outputFileName)

       # create PDF or PostScript file
       self.win.showLout (outputFileName)
       print ("O.K.")

   # -----------------------------------------------------------------------

   # Python

   def toPython (self, generatorFileName, compiler_data, with_qt = False) :

       outputFileName = self.win.outputFileName (self.sourceFileName, "_output.py")

       generator_module = self.win.loadModule (generatorFileName)
       generator_object = generator_module.C2Py ()


       generator_object.open (outputFileName, with_sections = True)
       if with_qt :
          generator_object.putLn ("#!/usr/bin/env python")
          generator_object.putLn ("")
          generator_object.putLn ("import sys")
          generator_object.putLn ("try :")
          generator_object.putLn ("   from PyQt5.QtCore import *")
          generator_object.putLn ("   from PyQt5.QtGui import *")
          generator_object.putLn ("   from PyQt5.QtWidgets import *")
          generator_object.putLn ("except :")
          generator_object.putLn ("   from PyQt4.QtCore import *")
          generator_object.putLn ("   from PyQt4.QtGui import *")
          generator_object.putLn ("")

       generator_object.send_program (compiler_data)

       if with_qt :
          generator_object.putLn ("if __name__ == '__main__' :")
          generator_object.incIndent ()
          # generator_object.putLn ("app = QApplication (sys.argv)")
          generator_object.putLn ("main ()")
          # generator_object.putLn ("app.exec_ ()")
          generator_object.decIndent ()
       generator_object.close ()

       self.win.reloadFile (outputFileName)

       print ("O.K.")

       if with_qt :
          os.system ("python" + " " + outputFileName + " &")

   # -----------------------------------------------------------------------

   # Qt

   def createInstance (self, type) :
       return eval (type + "()")

   def setProperty (self, obj, field, value) :
       # print ("PROPERTY", field, value);
       # setattr (obj, field, value)
       field = "set" + field.capitalize()
       getattr (obj, field) (value)

   def toQt (self, decl_list) :
       for decl in decl_list.items :
           if isinstance (decl, self.compiler_module.CmmSimpleDecl) :
              print (decl.type, decl.name);
              widget = self.createInstance (decl.type)
              widget.setText ("ABC")
              widget.show ()
              self.widget = widget # keep reference
              for stat in decl.init_stat.items :
                  if isinstance (stat, self.compiler_module.CmmSimpleStat) :
                     expr = stat.inner_expr
                     if expr.kind == expr.assignExp :
                        left = expr.left
                        right = expr.right
                        if left.kind == left.varExp and right.kind == right.stringValueExp :
                           print (left.name, "=" , right.value)
                           self.setProperty (widget, left.name, right.value)

# --------------------------------------------------------------------------

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
