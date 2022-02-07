
# cmm_plugin.py

from __future__ import print_function

import os, sys, subprocess, importlib, inspect

from util import use_pyside2, use_qt5, use_python3

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
from lexer import Lexer
from monitor import Monitor
from grammar import Grammar
from toparser  import ToParser
from toproduct import ToProduct
from gcc_options import gcc_options, pkg_options

from util import findColor, findIcon, get_win
from tree import TreeItem

# --------------------------------------------------------------------------

cmm_instance = None

def get_builder () :
    return cmm_instance

# --------------------------------------------------------------------------

class Plugin (QObject) :

   def __init__ (self, main_window, plugin_menu = None) :
       super (Plugin, self).__init__ (main_window)
       self.win = main_window

       global cmm_instance
       cmm_instance = self # used by tools.py

       if plugin_menu != None :
          self.pluginMenu = plugin_menu
       else :
          self.pluginMenu = self.win.menuBar().addMenu ("&C--")

       act = QAction ("C-- Make", self.win)
       act.setShortcut ("F11")
       act.triggered.connect (self.cmmCompile)
       self.pluginMenu.addAction (act)

       act = QAction ("C-- Build", self.win)
       act.setShortcut ("F12")
       act.triggered.connect (self.cmmBuild)
       self.pluginMenu.addAction (act)

   # -----------------------------------------------------------------------

   def setup (self) :
       "setup grammar, parser and compiler file name"

       self.grammarFileName = "cmm/cmm.g"

       self.lexerFileName = "code/lexer.py"

       self.parserFileName = self.win.outputFileName ("cmm_parser.py")
       self.productFileName = self.win.outputFileName ("cmm_product.py")

       self.basicCompilerFileName = "cmm/cmm_comp.py"

       self.compilerFileName = "cmm/cmm_comp.py"
       # self.compilerClassName = "CmmCompiler"
       # self.compilerClassName = "CmmQtCompiler"
       self.compilerClassName = "CmmCustomCompiler" # parameter from tools.ini
       self.compilerFuncName = "compile_program" # parameter from tools.ini
       self.enableMonitor = False # parameter from tools.ini

       self.cppWriterFileName = "cmm/c2cpp.py"
       # self.cppClassName = "ToCpp"
       # self.cppClassName = "ToQtCpp"
       self.cppClassName = "ToCustomCpp" # parameter from tools.ini

       self.pythonWriterFileName = "cmm/c2py.py"
       # self.pythonClassName = "ToPy"
       # self.pythonClassName = "ToExtPy"
       # self.pythonClassName = "ToQtPy"
       self.pythonClassName = "ToCustomPy" # parameter from tools.ini

       self.foreign_modules = [ ]
       if use_pyside2 :
          prefix = "PySide2."
       elif use_qt5 :
          prefix = "PyQt5."
       else :
          prefix = "PyQt4."
       for m in sys.modules :
           if m.startswith (prefix) :
              self.foreign_modules.append (sys.modules [m])
              # print ("foreign module", m)

       self.attribute_modules = [ ]
       module_names = [ ]
       # module_names = [ "cmm/cmm_view.py" ]
       for name in module_names :
           module = self.win.loadModule (name)
           self.attribute_modules.append (module)

   # -----------------------------------------------------------------------

   def start (self, fileName) :
       "open new project"

       self.sourceFileName = fileName

       self.sourceEdit = self.win.inputFile (self.sourceFileName)
       self.win.initProject (self.sourceEdit)
       self.win.info.clearOutput ()

   # -----------------------------------------------------------------------

   def build (self, rebuild = False) :
       "generate parser module and product module"

       if ( rebuild or
            self.win.rebuildFile (self.grammarFileName, self.parserFileName) or
            self.win.rebuildFile (self.grammarFileName, self.productFileName) ) :

            # parser

            print ("generating parser")
            self.win.showStatus ("generating parser")

            grammar = Grammar ()
            grammar.openFile (self.grammarFileName)
            grammar.show_tree = True # report new objects to monitor class

            parser_generator = ToParser ()
            parser_generator.open (self.parserFileName)
            parser_generator.parserFromGrammar (grammar)
            parser_generator.close ()

            grammarEdit = self.win.inputFile (self.grammarFileName)
            self.win.joinProject (grammarEdit)
            gt = self.win.displayGrammarData (grammarEdit, grammar)

            parserEdit = self.win.reloadFile (self.parserFileName)
            self.win.joinProject (parserEdit)
            self.win.displayPythonCode (parserEdit)

            print ("parser O.K.")

            # product

            parserModuleName, ext = os.path.splitext (os.path.basename (self.parserFileName))

            product_generator = ToProduct ()
            product_generator.open (self.productFileName)
            product_generator.productFromGrammar (grammar, parserModuleName)
            product_generator.close ()

            productEdit = self.win.reloadFile (self.productFileName)
            self.win.joinProject (productEdit)
            self.win.displayPythonCode (productEdit)
            gt.updateGroups ()

            print ("product O.K.")
            self.win.showStatus ("")

   # -----------------------------------------------------------------------

   def compile (self) :
       "run compiler module"

       if use_python3 :
          importlib.invalidate_caches ()

          self.parser_module = self.win.loadModule (self.parserFileName)
          self.product_module = self.win.loadModule (self.productFileName) # required by compiler_module
          if self.compilerFileName != self.basicCompilerFileName :
             self.win.loadModule (self.basicCompilerFileName)

       compiler_module = self.win.loadModule (self.compilerFileName)

       compiler = getattr (compiler_module, self.compilerClassName)
       compiler = compiler () # create instace

       compiler.win = self.win

       if self.enableMonitor :
          compiler.monitor = Monitor (self.win)

       compiler.foreign_modules = self.foreign_modules
       compiler.attribute_modules = self.attribute_modules

       compiler.openFile (self.sourceFileName, with_support = True)
       try :
          # compiler.compile_program ()
          func = getattr (compiler, self.compilerFuncName)
          func ()
       finally :
          compiler.close ()

       self.win.showClasses (compiler.global_scope)
       self.win.addNavigatorData (self.sourceEdit, compiler.global_scope)
       self.win.displayCompilerData (self.sourceEdit, compiler.top_decl_list)
       self.win.displayObject ("builder", self)

       self.compiler_module = compiler_module
       self.compiler = compiler
       self.compiler_data = compiler.top_decl_list
       self.compiler_scope = compiler.global_scope # only for information

       print ("compilation O.K.")
       return self.compiler_data

   # -----------------------------------------------------------------------

   def to_cpp (self) :

       input_data = self.compiler_data

       outputSuffix = "_output.cpp"
       outputFileName = self.win.outputFileName (self.sourceFileName, outputSuffix)

       # product_module = self.win.loadModule (self.productFileName) # required by cmm_comp

       tool_module = self.win.loadModule (self.cppWriterFileName)
       tool_object = getattr (tool_module, self.cppClassName)
       tool_object = tool_object () # create instance

       tool_object.open (outputFileName, with_sections = True)
       # tool_object.foreign_modules = self.foreign_modules

       tool_object.send_program (input_data)
       tool_object.close ()

       self.win.loadFile (self.sourceFileName) # show tab with source

       print ("run product O.K.")

   def to_python (self) :

       input_data = self.compiler_data

       outputSuffix = "_output.py"
       outputFileName = self.win.outputFileName (self.sourceFileName, outputSuffix)

       tool_module = self.win.loadModule (self.pythonWriterFileName)
       # tool_object = tool_module.C2PyQt ()
       tool_object = getattr (tool_module, self.pythonClassName)
       tool_object = tool_object () # create instance

       tool_object.open (outputFileName, with_sections = True)
       # tool_object.foreign_modules = self.foreign_modules

       tool_object.send_program (input_data)
       tool_object.close ()

       self.win.loadFile (self.sourceFileName) # show tab with source

       print ("C++ to Python O.K.")

       self.win.runPython (outputFileName)

   # -----------------------------------------------------------------------

   # run tool

   def toolObject (self, moduleName = "", className = "") :
       if moduleName == "" :
          tool_module = sys.modules [__name__] # cmm_plugin module
       else :
          tool_module = self.win.loadModule (moduleName)

       if moduleName == "" and className == "" :
          tool_object = self # cmm_instance class
       elif className == "" :
          tool_object = tool_module
       else :
          tool_object = getattr (tool_module, className)
          # if inspect.isclass (tool_object) or inspect.isfunction (tool_object) :
          if inspect.isclass (tool_object) :
             tool_object = tool_object ()

       return tool_object


   def tool (self, input_data = None, moduleName = "", className = "", funcName = "", outputSuffix = "", msg = "", addBuilder = False) :
       "load tool module, create tool object, run tool method"

       if input_data == None :
          input_data = self.compiler_data

       if funcName == "" :
          funcName = "send_program"

       if outputSuffix == "" :
          outputSuffix = "_tool_output.py"

       if msg == "" :
          msg = "O.K."


       outputFileName = self.win.outputFileName (self.sourceFileName, outputSuffix)
       # self.toolOutputFileName = outputFileName

       tool_object = self.toolObject (moduleName, className)

       if funcName == "" :
          tool_func = tool_object
       else :
          tool_func = getattr (tool_object, funcName)

       if addBuilder :
          tool_func (self)
       else :
          if hasattr (tool_object, "open") :
             tool_object.open (outputFileName, with_sections = True)
          # tool_object.foreign_modules = self.compiler.foreign_modules

          tool_func (input_data)

          if hasattr (tool_object, "close") :
             tool_object.close ()

       # file is already displayed and joined to project by open ( ..., with_sections = True )
       # do not reload, otherwise color highlighting is lost

       # outputEdit = self.win.reloadFile (outputFileName)
       # self.win.joinProject (outputEdit)
       # self.win.displayFile (outputFileName)

       # self.win.loadFile (self.sourceFileName) # show tab with source

       # self.outputFileName = outputFileName # !?
       print (msg)
       return outputFileName

   # -----------------------------------------------------------------------

   def comp (self, fileName, rebuild = False) :

       self.setup ()
       self.start (fileName)
       self.build (rebuild)
       self.compile ()

   def run (self) :
       self.to_cpp ()
       self.to_python ()

   def runCmmGroup (self, ini, group) :
       "runCmmGroup - used from tools module"
       ini.beginGroup (group)

       "module, cls, func, param, outputSuffix"
       module = self.win.commands.string ("module")
       cls = self.win.commands.string ("cls")
       func = self.win.commands.string ("func")
       param = self.win.commands.string ("param")
       outputSuffix = self.win.commands.string ("outputSuffix")

       "example"
       example = self.win.commands.string ("example")
       if example != "" :
          param = "examples/" + example

       ini.endGroup ()

       rebuild = False

       self.start (param)
       self.setup ()

       ini.beginGroup (group)

       "compiler_mod"
       tmp = ini.string ("compiler_mod")
       if tmp != "" :
          self.compilerFileName = tmp

       "compiler_cls"
       tmp = self.win.commands.string ("compiler_cls")
       if tmp != "" :
          self.compilerClassName = tmp

       "compiler_func"
       tmp = self.win.commands.string ("compiler_func")
       if tmp != "" :
          self.compilerFuncName = tmp

       "monitor"
       tmp = self.win.commands.boolean ("monitor")
       if tmp :
          self.enableMonitor = True

       "cpp_cls"
       tmp = self.win.commands.string ("cpp_cls")
       if tmp != "" :
          self.cppClassName = tmp

       "python_cls"
       tmp = self.win.commands.string ("python_cls")
       if tmp != "" :
          self.pythonClassName = tmp

       "module cls func outputSuffix"
       module = self.win.commands.string ("module")
       cls = self.win.commands.string ("cls")
       func = self.win.commands.string ("func")
       outputSuffix = self.win.commands.string ("outputSuffix")
       addBuilder = self.win.commands.boolean ("addBuilder")

       ini.endGroup ()

       self.build (rebuild)
       self.compile ()

       self.to_python ()
       self.to_cpp ()

       if module != "" or cls != "" or func != "" :
          self.tool (moduleName = module, className = cls, funcName = func,
                     outputSuffix = outputSuffix, addBuilder = addBuilder)

   # -----------------------------------------------------------------------

   def cmmCompile (self) :
       self.comp ("examples/simple.cc")
       self.run ()

   def cmmBuild (self) :
       self.comp ("examples/simple.cc", rebuild = True)
       self.run ()

# --------------------------------------------------------------------------

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
