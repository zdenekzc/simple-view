
# lexer.py

from __future__ import print_function

import os

import subprocess
from gcc_options import gcc_options, pkg_options

from input import indexToFileName, fileNameToIndex, quoteString, Input

# --------------------------------------------------------------------------

class Separators (object) :
   def __init__ (self) :
       self.value = -1  # -1 ... substring is not a valid symbol
                        # value >= 0 ... token kind
       self.items = { } # another symbols with same prefix
                        # dictionary of Separators ( keys ... first character )

class Define (object) :
   def __init__ (self) :
       self.name = ""
       self.params = None # None ... without paramaters, [ ] ... with empty parameter list
       self.dots = False
       self.code = ""
       self.fileInx = 0
       self.lineNum = 1

class CondSection (object) :
   def __init__ (self) :
      self.orig_use_input = False # outer use_input
      self.allow_reading = True # some sub-section can be used (for reading tokens)
      self.allow_else = True # "else" sub-section is possible

class LexerException (Exception) :
   pass

# --------------------------------------------------------------------------

class LexerInput (object) :
   def __init__ (self) :
       self.source = ""

       self.fileInx = 0 # file index
       self.lineNum = 1 # line number (from 1)
       self.colNum  = 1 # column number (from 1)
       self.byteOfs = 0 # byte offset (from 0)

       self.isInclude = False
       self.isMacro = False

       self.macros = { } # local macro definitions

       self.above = None # above LexerInput

       self.guard = 1 # detect ifndef ... endif
       # 1 ... before ifndef
       # 2 ... inside ifndef ... endif
       # 3 ... after endif
       self.guard_symbol = None # symbol after ifndef
       self.guard_level = 0 # number of nested ifdef(s)

   def readChar (self) :
       if self.byteOfs < self.sourceLen :
          self.ch = self.source [self.byteOfs]
          self.byteOfs = self.byteOfs + 1
          if self.ch == '\n' :
             self.lineNum = self.lineNum + 1
             self.colNum = 0
          elif self.ch != '\r' :
             self.colNum = self.colNum + 1
       else :
          self.ch = '\0'

   def setFileName (self, name) :
       self.fileInx = fileNameToIndex (name)

   def getFileName (self) :
       return indexToFileName (self.fileInx)

   def openFile (self, fileName) :
       fileName = os.path.abspath (fileName)
       self.setFileName (fileName)
       f = open (fileName, "r")
       self.source = f.read ()
       self.sourceLen = len (self.source)

   def openString (self, sourceText) :
       self.source = str (sourceText) # optionaly conversion from QString
       self.sourceLen = len (self.source)

   def getSource (self) :
       return self.source # !?

# --------------------------------------------------------------------------

class Lexer (Input) :
   eos = 0
   identifier = 1
   number = 2
   real_number = 3
   character_literal = 4
   string_literal = 5
   separator = 6
   end_of_line = 7

   def __init__ (self) :
       super (Lexer, self).__init__ ()

       self.pascal = False

       self.at_keywords = False # allow identifiers stated with @
       self.debug = False
       self.monitor = None # object for reporting

       self.ignore_all_includes = False # used in view.py by run_cpp
       self.enable_embedded_options = False # collect single line comments with compile: text
       self.embedded_options = [ ] # used in view.py by run_cpp

       self.reset ()

   def reset (self) :

       self.charFileInx = 0
       self.charLineNum = 1
       self.charColNum = 1
       self.charByteOfs = 0 # character (in self.ch)

       self.tokenFileInx = 0
       self.tokenLineNum = 1
       self.tokenColNum = 1
       self.tokenByteOfs = 0 # token (in self.token)

       self.prevFileInx = 0
       self.prevLineNum = 1
       self.prevColNum = 1
       self.prevByteOfs = 0 # previous token
       self.prevEndOfs = 0

       self.ch = '\0'
       self.token = self.eos
       self.tokenText = ""
       self.tokenValue = ""

       self.input = None
       self.input_stack = [ ]
       self.file_input = None # main file or include file

       self.remember_level = 0
       self.remember_stack = [ ]
       self.recall_queue = [ ]

       self.pascal_dots = False

       self.inside_directive = False
       self.initPreproc ()

   # -----------------------------------------------------------------------

   def openFile (self, fileName, with_support = False) :
       # self.reset ()
       self.input = LexerInput ()
       self.input.openFile (fileName)
       if with_support :
          self.openSupport (fileName)
       self.file_input = self.input
       if self.monitor : self.monitor.start (self)
       self.original_file_name = self.getFileName () # !?
       self.nextChar ()
       self.nextToken ()

   def openString (self, sourceText) :
       # self.reset ()
       self.input = LexerInput ()
       self.input.openString (sourceText)
       self.file_input = self.input
       if self.monitor : self.monitor.start (self)
       self.nextChar ()
       self.nextToken ()

   def close (self) :
       super (Lexer, self).close ()

   # -----------------------------------------------------------------------

   def getFileName (self) :
       return self.file_input.getFileName () # !?

   def setFileName (self, name) :
       self.file_input.setFileName (name) # !?

   def getSource (self) :
       return self.file_input.source # !?

   def getFileInput (self) :
       inp = self.input
       while inp != None and inp.isMacro :
          inp = inp.above
       return inp

   # -----------------------------------------------------------------------

   def getPosition (self) :
       inp = self.file_input
       if inp == None :
          txt = " : : "
       else :
          txt = inp.getFileName () + ":" + str (inp.lineNum) + ":" + str (inp.colNum)
       return txt

   def info (self, text) :
       print (self.getPosition () + ": info: " + text)

   def warning (self, text) :
       print (self.getPosition () + ": warning: " + text)

   def error (self, text) :
       # print (self.getPosition () + ": error: " + text)
       raise LexerException (self.getPosition () + ": error: " + text + ", tokenText=" + self.tokenText)

   # -----------------------------------------------------------------------

   def getLocation (self, obj) :
       txt = " : : "
       if obj != None and getattr (obj, "src_file", -1) != -1 and getattr (obj, "src_line", -1) != -1 :
          txt = indexToFileName (obj.src_file) + ":" + str (obj.src_line) + ":"
          if getattr (obj, "src_column", -1) != -1 :
            txt = txt + str (obj.src_column)
       return txt

   def info_with_location (self, obj, text) :
       print (self.getLocation (obj) + ": info: " + text)

   def warning_with_location (self, obj, text) :
       print (self.getLocation (obj) + ": warning: " + text)

   def error_with_location (self, obj, text) :
       # print (self.getLocation (obj) + ": error: " + text)
       raise LexerException (self.getLocation (obj) + ": error: " + text)

   # -----------------------------------------------------------------------

   def nextChar (self) :
       self.charFileInx = self.input.fileInx
       self.charLineNum = self.input.lineNum
       self.charColNum  = self.input.colNum
       self.charByteOfs = self.input.byteOfs

       self.input.readChar ()
       self.ch = self.input.ch

       # if 0 and self.monitor : self.monitor.oneCharacter ()
       # if 0 and self.debug: print ("CHAR", quoteString (self.ch))

   def repeatChar (self) :
       self.charFileInx = self.input.fileInx
       self.charLineNum = self.input.lineNum
       self.charColNum  = self.input.colNum
       self.charByteOfs = self.input.byteOfs

       self.ch = self.input.ch

   # -----------------------------------------------------------------------

   def isLetter (self, c) :
       return c >= 'A' and c <= 'Z' or c >= 'a' and c <= 'z' or c == '_'

   def isDigit (self, c) :
       return c >= '0' and c <= '9'

   def isOctDigit (self, c) :
       return c >= '0' and c <= '7'

   def isHexDigit (self, c) :
       return c >= 'A' and c <= 'F' or c >= 'a' and c <= 'f' or c >= '0' and c <= '9'

   def isLetterOrDigit (self, c) :
       return self.isLetter (c) or self.isDigit (c)

   # -----------------------------------------------------------------------

   def comment_eol (self) :
       if self.monitor : self.monitor.startComment (2)

       txt = ""

       while self.ch != '\0' and self.ch != '\r' and self.ch != '\n' :
          txt += self.ch
          self.nextChar ()

       self.comment_directive (txt)

       if self.monitor: self.monitor.comment ()

   def comment (self, mark1) :
       if self.monitor : self.monitor.startComment (1)

       while self.ch != '\0' and self.ch != mark1 :
          if 0 :
             self.tokenText = self.tokenText + self.ch
          self.nextChar ()
       if self.ch == mark1 :
          self.nextChar () # skip mark1
       else :
          self.error ("Unterminated comment")

       if self.monitor: self.monitor.comment ()

   def comment2 (self, mark1, mark2) :
       if self.monitor : self.monitor.startComment (2)

       prev = ' '
       while self.ch != '\0' and not (prev == mark1 and self.ch == mark2) :
          prev = self.ch
          self.nextChar ()
       if self.ch == mark2 :
          self.nextChar () # skip mark2
       else :
          self.error ("Unterminated comment")

       if self.monitor : self.monitor.comment ()

   def checkDigit (self) :
       if not self.isDigit (self.ch) :
          self.error ("Digit expected")

   def digits (self) :
       while self.isDigit (self.ch) :
          self.tokenText = self.tokenText + self.ch
          self.nextChar ()

   def stringChar (self) :
       if self.ch != '\\' :
          c = self.ch
          self.nextChar ()
          return c
       else :
          self.nextChar () # skip backslash

          if self.ch >= '0' and self.ch <= '7' :
             cnt = 1
             c = 0
             while self.ch >= '0' and self.ch <= '7' and cnt <= 3 :
                c = 8 * c  + ord (self.ch) - ord ('0')
                cnt = cnt + 1
                self.nextChar ()
             return chr (c)

          elif self.ch == 'x' or self.ch <= 'X' :
             self.nextChar ()
             c = 0
             cnt = 1
             while self.ch >= '0' and self.ch <= '9' or self.ch >= 'A' and self.ch <= 'Z' or self.ch >= 'a' and self.ch <= 'z' and cnt <= 2 :
                if self.ch >= '0' and self.ch <= '9' :
                   n = ord (self.ch) - ord ('0')
                elif self.ch >= 'A' and self.ch <= 'Z' :
                   n = ord (self.ch) - ord ('A') + 10
                else :
                   n = ord (self.ch) - ord ('a') + 10
                c = 16 * c  + n
                cnt = cnt + 1
                self.nextChar ()
             return chr (c % 255)

          elif self.ch == 'a' :
             c = '\a'
          elif self.ch == 'b' :
             c =  '\b'
          elif self.ch == 'f' :
             c =  '\f'
          elif self.ch == 'n' :
             c =  '\n'
          elif self.ch == 'r' :
             c =  '\r'
          elif self.ch == 't' :
             c =  '\t'
          elif self.ch == 'v' :
             c =  '\v'
          elif self.ch == "'" or self.ch == '"'  or self.ch == '?' :
             c = self.ch
          else :
             c = self.ch # same

          self.nextChar ()
          return c

   def quoteString (self, s, quote = '"') :
       return quoteString (s, quote)

   def lookupKeyword (self) :
       pass

   def processSeparator (self) :
       # print ("separator start", self.tokenText)
       # if not self.inside_directive :
       pass

   def backStep (self) :
       self.tokenColNum = self.tokenColNum - 1
       self.tokenByteOfs = self.tokenByteOfs - 1

   # -----------------------------------------------------------------------

   def numericToken (self) :
       self.token = self.number
       cont = True
       if self.ch == "0" :
          self.tokenText = self.tokenText + self.ch
          self.nextChar ()
          if self.ch == "x" :
             self.tokenText = self.tokenText + self.ch
             self.nextChar ()
             while self.isHexDigit (self.ch) :
                self.tokenText = self.tokenText + self.ch
                self.nextChar ()
             cont = False
          else :
             if self.isOctDigit (self.ch) :
                cont = False
             while self.isOctDigit (self.ch) :
                self.tokenText = self.tokenText + self.ch
                self.nextChar ()
       if cont :
          self.digits ()
          if self.ch == '.' :
             self.decimalToken ()
          self.exponentToken ()

   def decimalToken (self) :
       self.token = self.real_number
       self.tokenText = self.tokenText + self.ch # store '.'
       self.nextChar () # skip '.'
       # NO self.checkDigit ()
       self.digits ()

   def exponentToken (self) :
       if self.ch == 'e' or self.ch == 'E' :
          self.token = self.real_number
          self.tokenText = self.tokenText + self.ch # store 'e'
          self.nextChar () # skip 'e'
          if self.ch == '+' or self.ch == '-' :
             self.tokenText = self.tokenText + self.ch # store '+' or '-'
             self.nextChar () # skip '+' or '-'
          self.checkDigit ()
          self.digits ()
       if self.token == self.real_number :
          if self.ch == 'f' or self.ch == 'F' :
             self.nextChar ()
       else :
          if self.ch == 'l' or self.ch == 'L' :
             self.nextChar ()
          if self.ch == 'u' or self.ch == 'U' :
             self.nextChar ()
          if self.ch == 'l' or self.ch == 'L' :
             self.nextChar ()

   def normalToken (self) :
       self.token = self.eos
       self.tokenText = ""

       slash = False
       stop = False
       whiteSpace = True

       while whiteSpace and self.ch != '\0' and not stop :
          if self.inside_directive :
             while (self.ch != '\0' and self.ch <= ' ') or self.ch == '\\' :
                if self.ch == '\\' :
                   # if 0 and self.monitor: self.monitor.whiteSpace ()
                   self.nextChar ()
                   if self.ch == '\r' :
                      # if 0 and self.monitor: self.monitor.whiteSpace ()
                      self.nextChar ()
                   if self.ch == '\n' :
                      # if 0 and self.monitor: self.monitor.whiteSpace ()
                      self.nextChar ()
                else :
                   if self.ch == '\r' or self.ch == '\n' :
                      stop = True
                   # if 0 and self.monitor: self.monitor.whiteSpace ()
                   self.nextChar ()
          else :
             while self.ch != '\0' and self.ch <= ' ' :
                # if 0 and self.monitor: self.monitor.whiteSpace ()
                self.nextChar ()

          whiteSpace = False
          if self.ch == '/' :
             self.nextChar () # skip '/'
             if self.ch == '/' :
                self.nextChar () # skip '/'
                self.comment_eol ()
                whiteSpace = True # check again for white space
             elif self.ch == '*' :
                self.nextChar () # skip '*'
                self.comment2 ('*', '/')
                whiteSpace = True # check again for white space
             else :
                slash = True # produce '/' token

       self.tokenFileInx = self.charFileInx
       self.tokenLineNum = self.charLineNum
       self.tokenColNum = self.charColNum
       self.tokenByteOfs = self.charByteOfs

       if slash :
          self.token = self.separator
          self.tokenText = '/'
          self.backStep ()
          self.processSeparator ()

       elif stop :
          self.token = self.end_of_line

       elif self.ch == '\0' :
          self.token = self.eos

       elif self.isLetter (self.ch) :
          self.token = self.identifier
          while self.isLetterOrDigit (self.ch) :
             self.tokenText = self.tokenText + self.ch
             self.nextChar ()
          # NO self.lookupKeyword ()

       elif self.ch == '@' and self.at_keywords :
          self.token = self.identifier
          while self.isLetterOrDigit (self.ch) or self.ch == '@' :
             self.tokenText = self.tokenText + self.ch
             self.nextChar ()
          # NO self.lookupKeyword ()

       elif self.isDigit (self.ch) :
          self.numericToken ()

       elif self.ch == '\'' :
          self.token = self.character_literal
          self.nextChar ()
          while self.ch != '\0' and self.ch != '\r' and self.ch != '\n' and self.ch != '\'' :
             self.tokenText = self.tokenText + self.stringChar ()
          if self.ch != '\'' :
             self.error ("Unterminated string")
          self.nextChar ()
          # NO self.tokenText = quoteString (self.tokenText, '\'' )

       elif self.ch == '\"' :
          self.token = self.string_literal
          self.nextChar ()
          while self.ch != '\0' and self.ch != '\r' and self.ch != '\n' and self.ch != '\"' :
             self.tokenText = self.tokenText + self.stringChar ()
          if self.ch != '\"' :
             self.error ("Unterminated string")
          self.nextChar ()
          # NO self.tokenText = quoteString (self.tokenText)

       else :
          self.token = self.separator
          self.tokenText = self.ch
          first_ch = self.ch
          self.nextChar ()
          if first_ch == '.' and self.isDigit (self.ch) :
             self.decimalToken ()
             self.exponentToken ()
          elif first_ch != '#' :
             self.processSeparator ()

   # -----------------------------------------------------------------------

   def pascalSkipSpaces (self) :
       while self.ch != '\0' and self.ch <= ' ' :
          self.nextChar ()

   def pascalReadName (self) :
       self.pascalSkipSpaces ()
       name = ""
       while self.isLetterOrDigit (self.ch) :
          name = name + self.ch.lower ()
          self.nextChar ()
       if name == "" :
          self.error ("Identifier expected")
       return name

   def pascalReadFileName (self, term) :
       self.pascalSkipSpaces ()
       name = ""
       while self.ch != '\0' and self.ch > ' ' and self.ch != term :
          name = name + self.ch
          self.nextChar ()
       if name == "" :
          self.error ("Include file name expected")
       return name

   def pascalDirective (self, term) :
       self.pascalSkipSpaces ()
       if self.ch == '$' :
          self.nextChar ()
          name = self.pascalReadName ()
          if name == "include" :
             fileName = self.pascalReadFileName (term)
             # !? self.simpleInclude (fileName)
          elif name == "define" :
             id = self.pascalReadName ()
             self.addMacro (id, "")
          elif name == "undef" :
             id = self.pascalReadName ()
             self.undefMacro (id)
          elif name == "ifdef" :
             id = self.pascalReadName ()
             self.simpleIf (id in self.macros)
          elif name == "ifndef" :
             id = self.pascalReadName ()
             self.simpleIf (id not in self.macros)
          elif name == "else" :
             self.simpleElse ()
          elif name == "endif" :
             self.simpleEndif ()
          else :
             self.warning ("Unknown directive")
             while self.ch != term :
                self.nextChar ()
          self.pascalSkipSpaces ()
          if self.ch != term :
             self.error ("End of directive expected")

   def pascalToken (self) :
       self.token = self.eos
       self.tokenText = ""

       whiteSpace = True
       slash = False
       parenthesis = False

       while whiteSpace and self.ch != '\0' :
          whiteSpace = False
          while self.ch != '\0' and self.ch <= ' ' :
             self.nextChar ()
          if self.ch == '/' :
             self.nextChar () # skip '/'
             if self.ch == '/' :
                self.nextChar () # skip '/'
                self.comment_eol ()
                whiteSpace = True # check again for white space
             else :
                slash = True # produce '/' token
          if self.ch == '{' :
             self.nextChar () # skip '{'
             self.pascalDirective ('}')
             self.comment ('}')
             whiteSpace = True # check again for white space
          if self.ch == '(' :
             self.nextChar () # skip '('
             if self.ch == '*' :
                self.nextChar () # skip '*'
                self.pascalDirective ('*')
                self.comment2 ('*', ')')
                whiteSpace = True # check again for white space
             else :
                parenthesis = True # produce '(' token

       self.tokenFileInx = self.charFileInx
       self.tokenLineNum = self.charLineNum
       self.tokenColNum = self.charColNum
       self.tokenByteOfs = self.charByteOfs

       if self.pascal_dots :
          self.pascal_dots = False
          self.tokenText = "."
          self.ch = '.'
          self.processSeparator ()

       elif slash :
          self.token = self.separator
          self.tokenText = '/'
          self.backStep ()
          self.processSeparator ()

       elif parenthesis :
          self.token = self.separator
          self.tokenText = '('
          self.backStep ()
          self.processSeparator ()

       elif self.ch == '\0' :
          self.token = self.eos

       elif self.isLetter (self.ch) :
          self.token = self.identifier
          while self.isLetterOrDigit (self.ch) :
             self.tokenText = self.tokenText + self.ch
             self.nextChar ()
          self.tokenText = self.tokenText.lower ()
          # NO self.lookupKeyword ()

       elif self.isDigit (self.ch) :
          self.token = self.number
          self.digits ()
          if self.ch == '.' :
             self.nextChar () # skip '.'
             if self.ch == '.' : # two dots
                self.backStep ()
                self.pascal_dots = True
             else :
                self.token = self.real_number
                self.tokenText = self.tokenText + '.' # store '.'
                self.checkDigit ()
                self.digits ()
          if self.ch == 'e' or self.ch == 'E' :
             self.token = self.real_number
             self.tokenText = self.tokenText + self.ch # store 'e'
             self.nextChar () # skip 'e'
             if self.ch == '+' or self.ch == '-' :
                self.tokenText = self.tokenText + self.ch # store '+' or '-'
                self.nextChar () # skip '+' or '-'
             self.checkDigit ()
             self.digits ()

       elif self.ch == '$' :
          self.token = self.number
          self.tokenText = '$'
          self.nextChar ()
          if not self.isHexDigit (self.ch) :
             self.error ("Hexadecimal digit expected")
          while self.isHexDigit (self.ch) :
             self.tokenText = self.tokenText + self.ch
             self.nextChar ()

       elif self.ch == '#' :
          self.token = self.character_literal # !?
          self.tokenText = '#'
          self.nextChar ()
          if not self.isDigit (self.ch) :
             self.error ("Digit expected")
          while self.isDigit (self.ch) :
             self.tokenText = self.tokenText + self.ch
             self.nextChar ()

       elif self.ch == '\'' :
          self.token = self.string_literal
          self.nextChar ()
          again = True
          while again :
             again = False
             while self.ch != '\0' and self.ch != '\r' and self.ch != '\n' and self.ch != '\'' :
                self.tokenText = self.tokenText + self.ch
                self.nextChar ()
             if self.ch == '\'' :
                self.nextChar () # skip quote
                if self.ch == '\'' : # two quotes
                   self.tokenText = self.tokenText + self.ch # store one quote
                   self.nextChar ()
                   again = True
             else :
                self.error ("Unterminated string")

       else :
          self.token = self.separator
          self.tokenText = self.ch
          self.nextChar ()
          self.processSeparator ()

   # -----------------------------------------------------------------------

   def initPreproc (self) :
       self.incl_path = [ "." ]

       self.macros = { }
       self.active_macros = { }

       self.use_input = True
       self.cond_stack = [ ]

       self.guard_map = { }

       self.tolerate_missing_include = False
       self.include_files = [ ]

       self.ignore_include_dir = { }
       self.ignore_include = { }
       self.ignore_macro = { }

       self.expand_limit = 100

       self.preprocDir = "_input"
       self.inputPrefix = "input_"
       self.preprocPrefix = "preproc_"

   def addInclDir (self, path) :
       self.incl_path.append (path)
       if self.monitor: self.monitor.addIncludeDir (path)
       # print ("INCL DIR", path)

   def newMacro (self, name, value) :
       defn = Define ()
       defn.name = name
       defn.code = value
       defn.fileInx = self.tokenFileInx
       defn.lineNum = self.tokenLineNum
       return defn

   def addMacro (self, name, value) :
       defn = self.newMacro (name, value)
       self.macros [defn.name] = defn
       if self.monitor: self.monitor.addMacro (defn)
       return defn

   def addMacroWithParams (self, name, params, value) :
       defn = self.addMacro (name, value)
       defn.params = [ ]
       for param in params :
          defn.params.append (param)
       if self.monitor: self.monitor.addMacro (defn)
       return defn

   def undefMacro (self, name) :
       if name in self.macros :
          del self.macros [name]
       if self.monitor: self.monitor.undefMacro (name)

   def searchFile (self, filename, incl_sys) :
       result = None
       if not incl_sys :
          path = os.path.dirname (self.getFileName ())
          test = os.path.join (path, filename)
          if os.path.exists (test) and not os.path.isdir (test) :
             result = test
       for path in self.incl_path :
          test = os.path.join (path, filename)
          if os.path.exists (test) and not os.path.isdir (test) :
             result = test
             break
       return result

   def searchNextFile (self, filename) :
       inp = self.input
       while inp != None and inp.isMacro :
          inp = inp.above

       dirName = ""
       if inp != None :
          dirName = os.path.dirname (inp.getFileName ())

       result = None
       accept = False
       for path in self.incl_path :
          if accept :
             test = os.path.join (path, filename)
             if os.path.exists (test) :
                result = test
                # result = os.path.abspath (result)
                break
          else :
             if path == dirName :
                accept = True
       return result

   def simpleToken (self) :
       "token without expansion"
       if self.pascal :
          self.pascalToken ()
       else :
          self.normalToken ()

       # if self.debug : print ("SIMPLE TOKEN", self.tokenToText (), "line", str (self.tokenLineNum), "col", str (self.tokenColNum))

   def isToken (self, value) :
       return self.tokenText == value

   def verifyToken (self, value) :
       if not self.isToken (value) :
          self.error (value + " expected")

   # -----------------------------------------------------------------------

   def searchMacro (self, name) :
       defn = None
       inp = self.input
       while defn == None and inp != None :
          if name in inp.macros :
             defn = inp.macros [name]
          inp = inp.above
       if defn == None and name in self.macros :
          defn = self.macros [name]
       if defn != None and name in self.ignore_macro :
          defn.code = ""
       # if defn != None :
       #   print ("FOUND", name)
       return defn

   def expandName (self, name) :
       defn = self.searchMacro (name)
       if defn != None and defn.params == None and not defn.dots :
          return defn.code
       else :
          return name

   def expandParam (self, name) :
       defn = None
       inp = self.input
       if name in inp.macros :
          defn = inp.macros [name]
       if defn != None and defn.params == None and not defn.dots :
          return defn.code
       else :
          return name

   def skipSpaces (self) :
       while self.ch != '\0' and self.ch != '\r' and self.ch != '\n' and self.ch <= ' ' :
          self.nextChar ()

   def expandToken (self) :
       again = True
       while again :
          "read simple token"
          self.simpleToken ()
          again = False
          quote = False
          if self.use_input and self.input.isMacro and self.tokenText == '#' :
             quote = True
             self.simpleToken ()
          if self.use_input and self.token == self.identifier :
             "compound name"
             name = self.tokenText
             if self.input.isMacro :
                self.skipSpaces ()
                if self.ch == '#' :
                   name = self.expandParam (name)
                   while self.ch == '#' : # !?
                      self.nextChar () # skip hash mark
                      if self.ch != '#' :
                         self.error ("## expected")
                         # self.warning ("## expected")
                      self.nextChar () # skip second hash mark
                      self.simpleToken () # skip identifier (as token)
                      if self.token != self.identifier :
                         self.warning ("Identifier expected")
                      else :
                         name1 = name
                         name2 = self.expandParam (self.tokenText)
                         name = name + name2
                         self.tokenText = name # store new token value
                         self.skipSpaces ()
                      # keep token equal to last identifier
                   # if self.debug : print ("COMPOUND NAME", name1, name2, "-->", name)

             if quote :
                value = self.expandName (name)
                self.token = self.string_literal
                self.tokenText = value
                # if self.debug : print ("STRING", name, quoteString (value))
             else :
                if not self.active_macros.get (name) :
                   defn = self.searchMacro (name)
                   if defn != None :
                      "expand macro"
                      if len (self.input_stack) > self.expand_limit :
                         self.error ("Too many nested macros")
                      if self.monitor : self.monitor.expandMacro (defn)
                      # if self.debug : print ("EXPAND MACRO", defn.name)
                      next_input = LexerInput ()
                      missing_parameters = False

                      if defn.params != None or defn.dots :
                         self.simpleToken () # skip macro name
                         if not self.isToken ('(') :
                            missing_parameters = True
                         else :
                            if self.monitor: self.monitor.openParameters ()
                            if self.monitor : self.monitor.paramToken ()
                            self.simpleToken () # skip '('
                            cnt = len (defn.params)
                            inx = 0
                            args = None
                            while inx < cnt or defn.dots and not self.isToken (')') :
                                if inx < cnt :
                                   param_name = defn.params [inx]
                                else :
                                   param_name = ""
                                if self.monitor: self.monitor.openParam (param_name)
                                # if self.debug : print ("OPEN PARAM", param_name)
                                value = ""
                                level = 0
                                while not (level == 0 and (self.isToken (',') or self.isToken (')'))) :
                                   if self.isToken ('(') :
                                      level = level + 1
                                   if self.isToken (')') :
                                      level = level - 1
                                   if value != "" :
                                      value = value + " "
                                   value = value + self.tokenText
                                   if self.monitor : self.monitor.paramToken ()
                                   self.simpleToken ()
                                if self.monitor: self.monitor.closeParam ()
                                # if self.debug : print ("CLOSE PARAM", param_name, "=", quoteString (value))
                                if inx < cnt :
                                   param = self.newMacro (param_name, value)
                                   next_input.macros [param.name] = param
                                else :
                                   if args == None :
                                      args = self.newMacro ("__VA_ARGS__", value)
                                      next_input.macros [args.name] = args
                                   else :
                                      args.code = args.code + "," + value
                                if inx+1 < cnt or not self.isToken (')') :
                                   self.verifyToken (',')
                                   if self.monitor : self.monitor.paramToken ()
                                   self.simpleToken ()
                                inx = inx + 1
                            self.verifyToken (')')
                            if self.monitor : self.monitor.paramToken ()
                            # NO self.simpleToken ()
                            if self.monitor: self.monitor.closeParameters ()

                      if not missing_parameters :
                         next_input.isMacro = True
                         next_input.macro_name = defn.name
                         next_input.above = self.input
                         self.input_stack.append (self.input)
                         self.active_macros [next_input.macro_name] = True
                         self.input = next_input
                         self.input.openString (defn.code + " ")
                         self.nextChar ()
                         again = True

          if not again :
             if self.isEndOfSource () and len (self.input_stack) != 0 :
                if self.input.isMacro : # only for macros, not for include files
                   if self.monitor: self.monitor.closeExpand ()
                   # if self.debug : print ("END EXPAND")
                   self.active_macros [self.input.macro_name] = False
                   self.input = self.input_stack.pop ()
                   self.file_input = self.getFileInput ()
                   self.repeatChar ()
                   again = True

          # if not again :
             # if self.debug : print ("EXPANDED TOKEN", self.tokenToText ())

   # -----------------------------------------------------------------------

   def defineDirective (self) :
       self.simpleToken () # skip define

       if not self.isIdentifier () :
          self.error ("Macro name expected")
       name = self.tokenText
       defn = self.newMacro (name, "")
       with_params = (self.ch == '(') # no space before '(' allowed
       self.simpleToken () # skip name

       if with_params :
          defn.params = [ ]
          self.simpleToken () # skip '('
          while not self.isToken (')') :
             if self.isToken ("...") :
                defn.dots = True
                self.simpleToken () # skip "..."
                self.verifyToken (')')
             elif self.isToken (".") :
                # when ... is not know token
                defn.dots = True
                self.simpleToken () # skip "."
                self.verifyToken ('.')
                self.simpleToken ()
                self.verifyToken ('.')
                self.simpleToken ()
                self.verifyToken (')')
             else :
                if not self.isIdentifier () :
                   self.error ("Parameter name expected")
                defn.params.append (self.tokenText)
                self.simpleToken ()
                if not self.isToken (')') :
                   self.verifyToken (',')
                   self.simpleToken ()
          self.simpleToken () # skip ')'

       while self.token != self.eos and self.token != self.end_of_line :
           defn.code = defn.code + self.tokenToText ()
           if self.ch != '\0' and self.ch != '\r' and self.ch != '\n' and self.ch <= ' ' :
              defn.code = defn.code + " "
           self.simpleToken ()

       self.macros [defn.name] = defn
       if self.monitor: self.monitor.defineDirective (defn)
       # if self.debug : print ("DEFINE", defn.name, defn.params, defn.code)
       # self.info ("DEFINE " + defn.name)

   def undefDirective (self) :
       self.simpleToken () # skip undef
       if not self.isIdentifier () :
          self.error ("Macro name expected")

       name = self.tokenText
       if name in self.macros :
          del self.macros [name]
       if self.monitor: self.monitor.undefDirective (name)

       self.simpleToken () # skip name

   def includeFileName (self) :
       incl_sys = False
       if self.token == self.string_literal :
          result = self.tokenText
       elif self.isToken ('<') :
          incl_sys = True
          result = ""
          while self.ch != '\0' and self.ch != '\r' and self.ch != '\n' and self.ch != '>' :
             result = result + self.ch
             self.nextChar ()
          if self.ch != '>' :
             self.error ("Missing >")
          self.nextChar ()
       else :
          self.error ("Include file name expected")
       self.simpleToken ()
       if not self.use_input :
          result = None
       return (result, incl_sys)

   # -----------------------------------------------------------------------

   def readMessage (self) :
       text = self.ch
       while self.ch != '\0' and self.ch != '\r' and self.ch != '\n' : # characters, not tokens
          if self.ch == '\\' :
             self.nextChar ()
             ok = False
             if self.ch == '\r' :
                self.nextChar ()
                ok = True
             if self.ch == '\n' :
                self.nextChar ()
                ok = True
             if not ok :
                text = text + '\\'
          else :
             text = text + self.ch
             self.nextChar ()
       self.token = self.end_of_line # !?
       return text

   def isDefined (self) :
       if not self.isIdentifier () :
          self.error ("Identifier expected")
       name = self.tokenText
       self.simpleToken ()
       return name in self.macros

   def readValue (self) :
       again = True
       while again :
          again = False
          # print ("READ_VALUE", self.tokenText)
          if self.isIdentifier () :
             if self.tokenText == "defined" :
                self.simpleToken ()
                if self.isToken ('(') :
                   self.simpleToken ()
                   value = self.isDefined ()
                   self.verifyToken (')')
                   self.simpleToken ()
                else :
                   value = self.isDefined ()
             else :
                name = self.tokenText
                if name in self.macros :
                   again = True
                else :
                   # self.error ("Unknown identifier " + name)
                   value = 0 # !?
                self.expandToken ()
          elif self.isNumber () :
             text = self.tokenText
             if text.endswith ('l') or text.endswith ('L') :
                text = text [:-1]
             if text.startswith ("0x") :
                value = int (text, 16)
             elif text.startswith ("0") :
                value = int (text, 8)
             else :
                value = int (text)
             self.expandToken ()
          elif self.isToken ('-') :
             self.expandToken ()
             value = - self.readValue ()
          elif self.isToken ('!') :
             self.expandToken ()
             value = not self.readValue ()
          elif self.isToken ('(') :
             self.expandToken ()
             value = self.expression ()
             self.verifyToken (')')
             self.expandToken ()
          else :
             self.error ("Value expected " + self.tokenText)
       return value

   def readArit (self) :
       func = ""
       prio = 0
       if self.isToken ('+') or self.isToken ('-') :
          func = self.tokenText
          prio = 11
       elif self.isToken ('*') or self.isToken ('/') or self.isToken ('%') :
          func = self.tokenText
          prio = 12
       elif self.isToken ('&') :
          if self.ch == '&' :
             self.nextChar ()
             func = "&&"
             prio = 4
          else :
             func = self.tokenText
             prio = 7
       elif self.isToken ('|') :
          if self.ch == '|' :
             self.nextChar ()
             func = "||"
             prio = 3
          else :
             func = self.tokenText
             prio = 5
       elif self.isToken ('<') :
          if self.ch == '<' :
             self.nextChar ()
             func = "<<"
             prio = 10
          elif self.ch == '=' :
             self.nextChar ()
             func = "<="
             prio = 9
          else :
             func = self.tokenText
             prio = 9
       elif self.isToken ('>') :
          if self.ch == '>' :
             self.nextChar ()
             func = ">>"
             prio = 10
          elif self.ch == '=' :
             self.nextChar ()
             func = ">="
             prio = 9
          else :
             func = self.tokenText
             prio = 9
       elif self.isToken ('=') :
          if self.ch == '=' :
             self.nextChar ()
             func = "=="
             prio = 8
          else :
             self.error ("Unknown operator")
       elif self.isToken ('!') :
          if self.ch == '=' :
             self.nextChar ()
             func = "!="
             prio = 8
          else :
             self.error ("Unknown operator")

       elif self.isToken ("&&") :
          func = self.tokenText
          prio = 4
       elif self.isToken ("||") :
          func = self.tokenText
          prio = 3
       elif self.isToken ("<<") or self.isToken (">>") :
          func = self.tokenText
          prio = 10
       elif self.isToken ("<=") or self.isToken (">=") :
          func = self.tokenText
          prio = 9
       elif self.isToken ("==") or self.isToken ("!=") :
          func = self.tokenText
          prio = 8

       else :
          self.error ("Unknown operator " + self.tokenText)
       self.expandToken ()
       return (func, prio)

   def calculate (self, a, func, b) :
       if func == "*" : return a * b
       elif func == "/" : return a / b
       elif func == "%" : return a % b
       elif func == "+" : return a + b
       elif func == "-" : return a - b
       elif func == "<<" : return a << b
       elif func == ">>" : return a >> b
       elif func == "<" : return a < b
       elif func == "<=" : return a <= b
       elif func == ">" : return a > b
       elif func == ">=" : return a >= b
       elif func == "==" : return a == b
       elif func == "!=" : return a != b
       elif func == "^" : return a ^ b
       elif func == "&" : return a & b
       elif func == "|" : return a | b
       elif func == "&&" : return bool (a) and bool (b)
       elif func == "||" : return bool (a) or bool (b)
       elif func == "," : return b
       else: self.error ("unknown operator " + func)

   def simpleExpression (self) :
       values = [ ]
       functions = [ ]
       priorities = [ ]

       value = self.readValue ()
       # if self.debug : print ("VALUE", value)
       values.append (value)

       while self.token != self.eos and self.token != self.end_of_line and not self.isToken (')') and not self.isToken ('?') and not self.isToken (':')  :

          next_func, next_prio = self.readArit ()
          # if self.debug : print ("NEXT FUNC", next_func)

          while len (priorities) > 0 and priorities [-1] >= next_prio :
             right = values.pop ()
             left = values.pop ()
             func = functions.pop ()
             priorities.pop ()
             value = self.calculate (left, func, right)
             # if self.debug : print ("CALC", left, func, right, "->", value)
             values.append (value)

          functions.append (next_func)
          priorities.append (next_prio)

          value = self.readValue ()
          # if self.debug : print ("VALUE", value)
          values.append (value)

       value = values.pop ()
       while len (priorities) > 0 :
          left = values.pop ()
          func = functions.pop ()
          priorities.pop ()
          value = self.calculate (left, func, value)

       return value

   def expression (self) :
       # if self.debug : print ("begin expr")
       value = self.simpleExpression ()
       if self.isToken ('?') :
          self.expandToken ()
          first = self.simpleExpression ()
          self.verifyToken (':')
          self.expandToken ()
          second = self.simpleExpression ()
          if value :
             value = first
          else :
             value = second
       # if self.debug : print ("end expr", value)
       return value

   # -----------------------------------------------------------------------

   def simpleIf (self, cond) :
       section = CondSection ()
       section.orig_use_input = self.use_input
       section.allow_reading = self.use_input
       section.allow_else = True
       self.cond_stack.append (section)
       if self.use_input :
          self.use_input = cond
          if cond :
             section.allow_reading = False # skip following sub-sections

   def simpleElif (self, cond) :
       if len (self.cond_stack) == 0 :
          self.error ("Unexpected elif")
       section = self.cond_stack [-1]
       if not section.allow_else :
          self.error ("Unexpected elif after else")

       self.use_input = section.allow_reading # important
       if self.use_input :
          self.use_input = cond
          if cond :
             section.allow_reading = False # skip following sub-sections

   def simpleElse (self) :
       if len (self.cond_stack) == 0 :
          self.error ("Unexpected else")
       section = self.cond_stack [-1]
       if not section.allow_else :
          self.error ("Duplicated else")

       self.use_input = section.allow_reading # important
       if self.use_input :
          section.allow_reading = False # skip following sub-sections

       section.allow_else = False

   def simpleEndif (self) :
       if len (self.cond_stack) == 0 :
          self.error ("Unexpected endif")
       section = self.cond_stack.pop ()
       self.use_input = section.orig_use_input

   # -----------------------------------------------------------------------

   def ifDirective (self) :
       self.expandToken ()
       if self.use_input :
          cond = bool (self.expression ())
       else :
          cond = False
          self.readMessage ()
       self.simpleIf (cond)
       # self.info ("if " + str (cond) + " -- " + str (len (self.cond_stack)))

   def ifdefDirective (self, negation = False) :
       self.simpleToken ()
       cond_name = self.tokenText
       if self.use_input :
          cond = self.isDefined ()
          if negation :
             cond = not cond
       else :
          cond = False
          self.readMessage ()
       self.simpleIf (cond)
       # self.info ("ifdef " + str (cond) + " -- " + str (len (self.cond_stack)))
       return cond_name

   def elifDirective (self) :
       if len (self.cond_stack) == 0 :
          self.error ("Unexpected else")
       section = self.cond_stack [-1]

       self.use_input = section.allow_reading # important, before expandToken
       self.expandToken ()

       if self.use_input : # important
          cond = bool (self.expression ())
       else :
          cond = False
          self.readMessage ()
       # self.info ("ELIF " + str (cond))
       self.simpleElif (cond)
       # self.info ("elif " + str (cond) + " -- " + str (len (self.cond_stack)))

   def elseDirective (self) :
       self.simpleToken ()
       self.simpleElse ()
       # self.info ("else " + " -- " + str (len (self.cond_stack)))

   def endifDirective (self) :
       # self.info ("endif " + " -- " + str (len (self.cond_stack)))
       self.simpleToken ()
       self.simpleEndif ()

   # -----------------------------------------------------------------------

   def readOptions (self, options) :
       for line in options :
           self.readOption (line)

   def readOption (self, line, warn = False) :
       words = line.split (" ", 1)
       if words [0] == "-I" :
          path = words [1]
          # print ("include", path)
          self.addInclDir (path)
       elif words [0] == "-D" :
          params = words[1].split ('=')
          name = params [0]
          value = params [1]
          # print ("define", name, value)
          self.addMacro (name, value)
       elif line.startswith ("-I") :
          path = line [2:]
          # print ("include", path)
          self.addInclDir (path)
       elif line.startswith ("-D") :
          line = line [2:]
          if line.find ("=") >= 0 :
             params = line.split ('=')
             name = params [0]
             value = params [1]
          else :
             name = line
             value = ""
          # print ("define", name, value)
          self.addMacro (name, value)
       elif warn :
          self.warning ("Unknown option: " + line)

   # -----------------------------------------------------------------------

   def comment_directive (self, line) :
       if self.enable_embedded_options :
          line = line.lstrip ()
          if line.startswith ("compile:") :
             line = line [8:].strip ()

             words = line.split ()
             if line == "-G" :
                self.storeOptions (gcc_options ())
             elif words[0] == "-P" and len (words) == 2 :
                name = words [1]
                self.storeOptions (pkg_options (name, libs = True))
             else :
                self.storeOption (line)

   def storeOptions (self, options) :
       for line in options :
            self.storeOption (line)

   def storeOption (self, line) :
       self.embedded_options.append (line)

   # -----------------------------------------------------------------------

   def make_dir (self, path) :
       if not os.path.isdir (path) :
          self.makedir (os.path.dirName (path))
          os.mkdir (path)

   # -----------------------------------------------------------------------

   def simpleIndentifier (self, msg) :
       if self.token != self.identifier :
          self.error (msg)
       value = self.tokenText
       self.simpleToken ()
       return value

   def simpleString (self, msg) :
       if self.token != self.string_literal :
          self.error (msg)
       value = self.tokenText
       self.simpleToken ()
       return value

   def simpleCheck (self, value) :
       if self.tokenText != value :
          self.error (quoteString (value) + " expected")

   def simpleParameter (self, msg) :
       if not self.token in [self.identifier, self.number, self.string_literal ] :
          self.error (msg)
       value = self.tokenToText ()
       if value == "true" :
          value = "True"
       if value == "false" :
          value = "False"
       self.simpleToken ()
       return value

   # -----------------------------------------------------------------------

   def directive (self) :
       incl_file_name = None
       incl_sys = False
       incl_next = False

       entry_use_input = self.use_input
       cond_directive = False
       cond_name = ""
       self.inside_directive = True

       if self.monitor: self.monitor.startDirective ()
       self.simpleToken () # skip hash mark
       directive_name = self.tokenText

       if self.isToken ("if") :
          self.ifDirective ()
          cond_directive = True
          if self.monitor : self.monitor.ifDirective ()

       elif self.isToken ("ifdef") :
          self.ifdefDirective ()
          cond_directive = True
          if self.monitor : self.monitor.ifdefDirective ()

       elif self.isToken ("ifndef") :
          cond_name = self.ifdefDirective (negation = True)
          cond_directive = True
          if self.monitor : self.monitor.ifndefDirective ()

       elif self.isToken ("elif") :
          self.elifDirective ()
          cond_directive = True
          if self.monitor : self.monitor.elifDirective ()

       elif self.isToken ("else") :
          self.elseDirective ()
          cond_directive = True
          if self.monitor : self.monitor.elseDirective ()

       elif self.isToken ("endif") :
          self.endifDirective ()
          cond_directive = True
          if self.monitor : self.monitor.endifDirective ()

       elif not self.use_input :
          self.readMessage () # read rest of line
          if self.monitor : self.monitor.unusedDirective ()

       else :
          if self.isToken ("define") :
             self.defineDirective ()

          elif self.isToken ("undef") :
             self.undefDirective ()

          elif self.isToken ("include") :
             # self.info ("include")
             self.expandToken () # skip include
             incl_file_name, incl_sys = self.includeFileName ()

          elif self.isToken ("include_next") :
             self.expandToken ()
             incl_file_name, incl_sys = self.includeFileName ()
             incl_next = True

          elif self.isToken ("warning") :
             text = self.readMessage ()
             if self.monitor : self.monitor.warningDirective (text)
             self.warning (text)

          elif self.isToken ("error") :
             text = self.readMessage ()
             if self.monitor : self.monitor.errorDirective (text)
             self.error (text)

          elif self.isToken ("pragma") :
             self.simpleToken () # skip pragma
             pragma_name = self.tokenText

             if self.isToken ("include_dir") :
                self.expandToken ()
                path = self.simpleString ("String with directory name expected")
                self.addInclDir (path)

             elif self.isToken ("gcc_options") :
                self.readOptions (gcc_options ())
                self.simpleToken ()

             elif self.isToken ("pkg") :
                self.expandToken ()
                name = self.simpleString ("String with package name expected")
                self.readOptions (pkg_options (name))

             elif self.isToken ("tolerate_missing_include") :
                self.tolerate_missing_include = True
                self.simpleToken ()

             elif self.isToken ("ignore_include_dir") :
                self.expandToken ()
                name = self.simpleString ("String with direcory name expected")
                self.ignore_include_dir [name] = True

             elif self.isToken ("ignore_include") :
                self.expandToken ()
                name = path = self.simpleString ("String with file name expected")
                self.ignore_include [name] = True

             elif self.isToken ("ignore_macro") :
                self.expandToken ()
                name = self.simpleIndentifier ("Identifier expected")
                self.ignore_macro [name] = True

             elif self.isToken ("enable_debug") :
                self.simpleToken ()
                self.debug = True
                if self.monitor: self.monitor.enableDebug ()

             elif self.isToken ("disable_debug") :
                self.simpleToken ()
                self.debug = False
                if self.monitor: self.monitor.disableDebug ()

             else :
                self.warning ("Unknown pragma directive " + self.tokenText)
                text = self.readMessage ()
                # self.info ("pragma message " + quoteString (text))
                # self.info ("token " +  quoteString (self.tokenText))

             if self.monitor : self.monitor.pragmaDirective (pragma_name)

          elif self.isIdentifier () :
             # self.error ("Unknown directive " + self.tokenText)
             self.warning ("Unknown directive " + self.tokenText)
             text = self.readMessage ()
          else :
             # self.error ("Directive name expected")
             self.warning ("Directive name expected")
             text = self.readMessage ()

       if self.token != self.end_of_line :
          self.warning ("End of line (after directive) expected")
          self.readMessage ()

       self.inside_directive = False
       if self.monitor: self.monitor.endDirective ()

       # ifndef .. endif guard

       if self.input.isInclude :
          if entry_use_input and self.input.guard == 1 and directive_name == "ifndef" :
             self.input.guard = 2
             self.input.guard_symbol = cond_name
             self.input.guard_level = len (self.cond_stack) - 1
             # self.info ("GUARD 2")
          elif self.use_input and self.input.guard == 2 and directive_name == "endif" :
             # self.use_input, not entry_use_input - important
             # self.info ("GUARD ENDIF " + str (self.input.guard_level) + " ... " + str (len (self.cond_stack)))
             if self.input.guard_level == len (self.cond_stack) :
                self.input.guard = 3
                # self.info ("GUARD 3")
          elif entry_use_input and self.input.guard == 3 :
              # self.info ("GUARD 0 " + str (self.token) + self.tokenText + "..." +  directive_name)
              self.input.guard = 0

       # open include file

       if incl_file_name != None and not self.ignore_all_includes :
          if incl_next :
             full_name = self.searchNextFile (incl_file_name)
          else :
             full_name = self.searchFile (incl_file_name, incl_sys)

          if full_name == None :
             if self.tolerate_missing_include :
                if self.monitor: self.monitor.skipMissingInclude (incl_file_name)
                # self.info ("MISSING INCL " + incl_file_name)
                self.warning ("Include file not found " + incl_file_name)
                self.expandToken ()
             else :
                self.error ("Include file not found " + incl_file_name)

          if full_name != None :
             key = os.path.abspath (full_name)
             if key in self.guard_map :
                cond = self.guard_map [key]
                if cond in self.macros :
                   if self.monitor: self.monitor.skipKnownInclude (incl_file_name)
                   # self.info ("KNOWN INCL " + incl_file_name)
                   full_name = None
                   self.expandToken ()

          if full_name != None :
             ignore = False
             base_name = os.path.basename (full_name)
             if base_name in self.ignore_include :
                ignore = True
             for prefix in self.ignore_include_dir :
                 if full_name.startswith (prefix) :
                    ignore = True
             if ignore :
                if self.monitor: self.monitor.skipIgnoredInclude (incl_file_name)
                # self.info ("IGNORE INCL " + incl_file_name)
                full_name = None
                self.expandToken ()

          if full_name != None :
             # self.info ("BEFORE INCL " + full_name)
             next_input = LexerInput ()
             next_input.above = self.input
             next_input.isInclude = True
             self.input_stack.append (self.input)
             self.input = next_input
             self.input.openFile (full_name)
             self.file_input = self.input
             if full_name in self.include_files :
                if self.monitor: self.monitor.alreadyIncluded (full_name)
                # self.info ("ALREADY INCLUDED " + full_name)
             self.include_files.append (full_name)
             if self.monitor: self.monitor.openInclude ()
             self.info ("OPEN INCL " + full_name)
             self.nextChar ()
             self.expandToken ()

       else : # not include directive
          self.expandToken ()

   # -----------------------------------------------------------------------

   def mark (self) :
       # print ("mark tokenText=" + self.tokenToText ())
       self.remember_level = self.remember_level + 1
       self.remember_stack.append ([ ])
       self.store () # store current token
       if self.monitor : self.monitor.mark ()
       return None

   def rewind (self, params) :
       # print ("before rewind tokenText=" + self.tokenToText ())
       items = self.remember_stack.pop ()
       self.remember_level = self.remember_level - 1
       if self.monitor : self.monitor.rewind ()
       if len (items) > 0 :
          self.recall_queue.extend (items)
          self.recall () # recall first token
       # print ("after rewind tokenText=" + self.tokenToText ())

   def store_data (self) :
       item = (
          self.charFileInx,
          self.charLineNum,
          self.charColNum,
          self.charByteOfs,

          self.tokenFileInx,
          self.tokenLineNum,
          self.tokenColNum,
          self.tokenByteOfs,

          self.prevFileInx,
          self.prevLineNum,
          self.prevColNum,
          self.prevByteOfs,
          self.prevEndOfs,

          self.ch,
          self.token,
          self.tokenText
       )
       return item

   def store (self) :
       item = self.store_data ()
       self.remember_stack [-1].append (item)

   def recall_data (self, item) :
       (
          self.charFileInx,
          self.charLineNum,
          self.charColNum,
          self.charByteOfs,

          self.tokenFileInx,
          self.tokenLineNum,
          self.tokenColNum,
          self.tokenByteOfs,

          self.prevFileInx,
          self.prevLineNum,
          self.prevColNum,
          self.prevByteOfs,
          self.prevEndOfs,

          self.ch,
          self.token,
          self.tokenText
       ) = item

   def recall (self) :
       item = self.recall_queue.pop (0)
       self.recall_data (item)
       if self.monitor : self.monitor.oneToken ()
       # if self.debug : print ("RECALL TOKEN", self.tokenToText ())

   def rememberToken (self) :
       item = self.store_data ()
       self.recall_queue.append (item)

   def nextToken (self) :
       if len (self.recall_queue) > 0 :
          self.recall ()
       else :
          self.plainToken ()
       if self.remember_level > 0 :
          self.store ()

       if self.token == self.character_literal :
          self.tokenValue = quoteString (self.tokenText, "'")
       elif self.token == self.string_literal :
          self.tokenValue = quoteString (self.tokenText)
       else :
          self.tokenValue = self.tokenText

   # -----------------------------------------------------------------------

   def plainToken (self) :
       self.prevFileInx = self.tokenFileInx
       self.prevLineNum = self.tokenLineNum
       self.prevColNum = self.tokenColNum
       self.prevByteOfs = self.tokenByteOfs
       self.prevEndOfs = self.charByteOfs

       if self.pascal :
          self.simpleToken ()
          while not self.use_input :
             if self.monitor : self.monitor.unusedToken ()
             self.simpleToken ()
       else :
          self.expandToken ()
          again = True
          while again :
             again = True
             if self.isToken ('#') :
                self.directive ()
             elif self.isEndOfSource () and len (self.input_stack) != 0 :
                if self.input.isInclude :
                   "check for empty ifndef ... endif include file"
                   key = os.path.abspath (self.getFileName ())
                   if self.file_input.guard == 3 :
                      value = self.file_input.guard_symbol
                      if self.monitor: self.monitor.storeGuard (key, value)
                      # self.info ("GUARD " +  key + " -> " + value)
                      self.guard_map [key] = value
                   else :
                      if self.monitor: self.monitor.missingGuard ()
                      # self.info ("MISSING GUARD " +  key + " -> " + value)
                   "close include file"
                   self.info ("CLOSE INCL")
                   if self.monitor: self.monitor.closeInclude ()
                if self.input.isMacro :
                   "close macro"
                   if self.monitor: self.monitor.closeExpand ()
                   self.active_macros [self.input.macro_name] = False
                self.input = self.input_stack.pop ()
                self.file_input = self.getFileInput ()
                self.repeatChar ()
                self.expandToken ()
             else :
                if not self.use_input :
                   if self.monitor : self.monitor.unusedToken ()
                   # print ("unused token:", self.tokenText)
                   self.simpleToken ()
                else :
                   "valid token"
                   again = False
       if self.file_input.guard == 1 or self.file_input.guard == 3 :
          "check for empty ifndef ... endif include file"
          self.file_input.guard = 0
       if self.token == self.identifier :
          "convert identifier to keyword"
          self.lookupKeyword ()
       if self.monitor : self.monitor.oneToken ()
       # if self.debug : print ("TOKEN", self.tokenToText ())

   # -----------------------------------------------------------------------

   def isEndOfSource (self) :
       return self.token == self.eos

   def isIdentifier (self) :
       return self.token == self.identifier

   def isNumber (self) :
       return self.token == self.number

   def isReal (self) :
       return self.token == self.real_number

   def isString (self) :
       return self.token == self.string_literal

   def isCharacter (self) :
       return self.token == self.character_literal

   def isSeparator (self, value) :
       # return self.token == self.separator and self.tokenText == value
       return self.token != self.string_literal and self.token != self.character_literal and self.tokenText == value

   def isKeyword (self, value) :
       return self.token == self.identifier and self.tokenText == value

   # -----------------------------------------------------------------------

   def readIdentifier (self, msg = "Identifier expected") :
       if not self.isIdentifier () :
          self.error (msg)
       value = self.tokenText
       self.nextToken ()
       return value

   def readNumber (self) :
       if not self.isNumber () :
          self.error ("Number expected")
       value = self.tokenText
       self.nextToken ()
       return value

   def readReal (self) :
       if not self.isReal () :
          self.error ("Real number expected")
       value = self.tokenText
       self.nextToken ()
       return value

   def readString (self) :
       if not self.isString () :
          self.error ("String literal expected")
       value = self.tokenText
       self.nextToken ()
       return value

   def readCharacter (self) :
       if not self.isCharacter () :
          self.error ("Character literal expected")
       value = self.tokenText
       self.nextToken ()
       return value

   # -----------------------------------------------------------------------

   def tokenToText (self) :
       if self.isCharacter () :
          return quoteString (self.tokenText, "'")
       elif self.isString () :
          return quoteString (self.tokenText)
       else :
          return self.tokenText

   # -----------------------------------------------------------------------

   def checkSeparator (self, value) :
       if not self.isSeparator (value) :
          self.error (value + " expected")
       self.nextToken ()

   def checkKeyword (self, value) :
       if not self.isKeyword (value) :
          self.error (value + " expected")
       self.nextToken ()

   # -----------------------------------------------------------------------

   def check (self, value) :
       if self.tokenText != value :
          self.error (value + " expected")
       self.nextToken ()

   def checkToken (self, value) :
       if self.token != value :
          self.error (self.tokenToSTring (value) + " expected")
       self.nextToken ()

   def tokenToString (self, value) :
       return "token " + str (value)

# --------------------------------------------------------------------------

class MonitorClass :
   def start (self, lexer) :
       pass

   def oneCharacter (self) :
       pass
   def whiteSpace (self) :
       pass
   def startComment (self, delta) :
       pass
   def comment (self) :
       pass

   def unusedToken (self) :
       pass
   def oneToken (self) :
       pass

   def mark (self) :
       pass
   def rewind (self) :
       pass

   def startDirective (self) :
       pass
   def endDirective (self) :
       pass
   def unusedDirective (self) :
       pass

   def ifDirective (self) :
       pass
   def ifdefDirective (self) :
       pass
   def ifndefDirective (self) :
       pass
   def elifDirective (self) :
       pass
   def elseDirective (self) :
       pass
   def endifDirective (self) :
       pass
   def warningDirective (self, text) :
       pass
   def errorDirective (self, text) :
       pass
   def pragmaDirective (self, name) :
       pass

   def openInclude (self) :
       pass
   def closeInclude (self) :
       pass

   def addIncludeDir (self, path) :
       pass
   def skipMissingInclude (self, name) :
       pass
   def skipKnownInclude (self, name) :
       pass
   def skipIgnoredInclude (self, name) :
       pass
   def alreadyIncluded (self, name) :
       pass

   def storeGuard (self, key, value) :
       pass
   def missingGuard (self) :
       pass

   def defineDirective (self, defn) :
       pass
   def undefDirective (self, name) :
       pass

   def addMacro (self, defn) :
       pass
   def undefMacro (self, name) :
       pass

   def expandMacro (self, defn) :
       pass
   def closeExpand (self) :
       pass
   def openParameters (self) :
       pass
   def closeParameters (self) :
       pass
   def openParam (self, param) :
       pass
   def paramToken (self) :
       pass
   def closeParam (self) :
       pass

   def enableDebug (self) :
       pass
   def disableDebug (self) :
       pass
   # def debugIncl (self, name) :
   #     pass

   def openObject (self, data) :
       pass
   def reopenObject (self, data) :
       pass
   def closeObject (self) :
       pass

   def declaration (self, decl) :
       pass

# --------------------------------------------------------------------------

def readEmbeddedOptions (fileName) : # used in view.py by run.cpp
    lexer = Lexer ()
    lexer.ignore_all_includes = True
    lexer.enable_embedded_options = True
    lexer.openFile (fileName)

    while not lexer.isEndOfSource () :
       lexer.nextToken ()

    result = lexer.embedded_options
    lexer.close ()

    result = " ".join (result)
    return result

# --------------------------------------------------------------------------

if __name__ == "__main__" :
    lexer = Lexer ()
    lexer.openFile ("pas.g")

    if 0 :
       for i in range (4) :
          print (lexer.tokenText)
          lexer.nextToken ()

       print ("---")

       point = lexer.mark ()
       for i in range (4) :
          print (lexer.tokenText)
          lexer.nextToken ()

       print ("---")
       lexer.rewind (point)
       for i in range (4) :
          print (lexer.tokenText)
          lexer.nextToken ()

    while not lexer.isEndOfSource () :
       print (lexer.tokenText, end = " ")
       lexer.nextToken ()

    point = lexer.mark ()
    lexer.rewind (point)

# --------------------------------------------------------------------------

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
