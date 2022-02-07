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

from input     import fileNameToIndex
from lexer     import Lexer
from grammar   import Grammar, Rule, Expression, Alternative, Ebnf, Nonterminal, Terminal
# from output    import openOutput, closeOutput, put, putEol, putLn, incIndent, decIndent
from symbols   import initSymbols
from tohtml    import ToHtml
from tolout    import ToLout
from toparser  import ToParser
from toproduct import ToProduct

# --------------------------------------------------------------------------

class GrammarPlugin (QObject) :

   def __init__ (self, main_window) :
       super (GrammarPlugin, self).__init__ (main_window)
       self.win = main_window

       self.gramMenu = self.win.menuBar().addMenu ("&Grammar")
       self.gramMenu.aboutToShow.connect (self.onShowGramMenu)

       act = QAction ("to &HTML", self.win)
       act.triggered.connect (self.toHtml)
       act.need_grammar = True
       self.gramMenu.addAction (act)

       act = QAction ("to &Lout", self.win)
       act.triggered.connect (self.toLout)
       act.need_grammar = True
       self.gramMenu.addAction (act)

       act = QAction ("to &Parser", self.win)
       act.triggered.connect (self.toParser)
       act.need_grammar = True
       self.gramMenu.addAction (act)

   def onShowGramMenu (self) :
       is_gram = self.win.hasExtension (self.win.getEditor(), ".g")
       for act in self.gramMenu.actions () :
           if getattr (act, "need_grammar", False) :
              act.setEnabled (is_gram)

   def openGrammar (self, editor) :
       source = str (editor.toPlainText ())
       grammar = Grammar ()
       grammar.openString (source)
       grammar.setFileName (editor.getFileName ())
       return grammar

   # Html

   def toHtml (self) :
       e = self.win.getEditor ()
       if self.win.hasExtension (e, ".g") :
          outputFileName = self.win.outputFileName (e.getFileName (), ".html")

          grammar = self.openGrammar (e)
          grammar.parseRules ()

          product = ToHtml ()
          product.open (outputFileName)
          product.htmlFromRules (grammar)
          product.close ()

          self.win.reloadFile (outputFileName)
          self.win.showHtml (outputFileName)
          print ("O.K.")

   # Lout

   def toLout (self) :
       e = self.win.getEditor ()
       if self.win.hasExtension (e, ".g") :
          outputFileName = self.win.outputFileName (e.getFileName (), ".lout")

          grammar = self.openGrammar (e)
          grammar.parseRules ()

          product = ToLout ()
          product.open (outputFileName)
          product.loutFromRules (grammar)
          product.close ()

          self.win.reloadFile (outputFileName)

          # create PDF or PostScript file
          self.win.showLout (outputFileName)

          print ("O.K.")

   # Parser

   def toParser (self) :
       e = self.win.getEditor ()
       if self.win.hasExtension (e, ".g") :

          parserFileName = self.win.outputFileName (e.getFileName (), "_parser.py")

          grammar = self.openGrammar (e)

          product = ToParser ()
          product.open (parserFileName)
          product.parserFromGrammar (grammar)

          if os.path.basename (e.getFileName ()) == "pas.g" : # !?
             product.putLn ("if __name__ == '__main__' :")
             product.incIndent ()
             product.putLn ("parser = Parser ()")
             product.putLn ("parser.pascal = True")
             product.putLn ("parser.openFile ('example.pas')")
             product.putLn ("result = parser.parse_module_decl ()")
             product.decIndent ()

          product.close ()

          self.win.displayGrammarData (e, grammar)

          parserEdit = self.win.reloadFile (parserFileName)
          self.win.displayPythonCode (parserEdit)
          print ("parser O.K.")

          # product

          productFileName = self.win.outputFileName (e.getFileName (), "_product.py")

          parserModuleName, ext = os.path.splitext (os.path.basename (parserFileName))

          product = ToProduct ()
          product.open (productFileName)
          product.productFromGrammar (grammar, parserModuleName)
          product.close ()

          productEdit = self.win.reloadFile (productFileName)
          self.win.displayPythonCode (productEdit)
          print ("product O.K.")

# --------------------------------------------------------------------------

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
