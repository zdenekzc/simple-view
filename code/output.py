
# output.py

from __future__ import print_function

import sys, time

from input import quoteString

from io import StringIO

sectionGenerator = None

# --------------------------------------------------------------------------

class Output (object) :

   def __init__ (self) :
       self.initialize ()

   def initialize (self) :
       self.indentation = 0
       self.addSpace = False
       self.extraSpace = False
       self.startLine = True
       self.addEmptyLine = False
       self.outputFile = sys.stdout
       self.sections = None

   def open (self, fileName, with_sections = False) :
       self.initialize ()

       if with_sections and sectionGenerator != None :
          self.sections = sectionGenerator.createSections (fileName)
          self.sections.open ()
       else :
          if fileName == "" :
             self.outputFile = sys.stdout
          else :
             self.outputFile = open (fileName, "w")

   def close (self) :
       if self.sections != None :
          self.sections.close ()
       else :
          self.outputFile.close ()
       self.outputFile = sys.stdout

   def write (self, txt) :
       if self.sections != None :
          self.sections.write (txt)
       else :
          self.outputFile.write (txt)

   # -----------------------------------------------------------------------

   def openString (self) :
       self.initialize ()
       self.outputFile = StringIO ()

   def closeString (self) :
       result = self.outputFile.getvalue ()
       self.outputFile.close ()
       self.outputFile = sys.stdout
       return result

   # -----------------------------------------------------------------------

   # put

   def incIndent (self) :
       self.indentation = self.indentation + 3

   def decIndent (self) :
       self.indentation = self.indentation - 3

   def indent (self) :
       self.incIndent ()

   def unindent (self) :
       self.decIndent ()

   def put (self, txt) :
       if txt != "" :
          if self.startLine :
             if self.addEmptyLine :
                self.write ("\n")
             self.write (" " * self.indentation)
             self.startLine = False
             self.addEmptyLine = False
          self.write (txt)

   def putEol (self) :
       self.startLine = True
       self.addSpace = False
       self.extraSpace = False
       self.write ("\n")

   def putCondEol (self) :
       if not self.startLine :
          self.putEol ()

   def putLn (self, txt = "") :
       if txt != "":
          self.put (txt)
       self.putEol ()

   # -----------------------------------------------------------------------

   # send

   def isLetterOrDigit (self, c) :
       return c >= 'A' and c <= 'Z' or c >= 'a' and c <= 'z' or c >= '0' and c <= '9' or c == '_'

   def send (self, txt) :
       if txt != "" :
          if self.startLine :
             self.write (" " * self.indentation)
             self.addSpace = False
             self.extraSpace = False
          self.startLine = False

          c = txt [0]
          if c == ',' or c == ';' or c == ')' :
             self.extraSpace = False
          if not self.isLetterOrDigit (c) :
             self.addSpace = False

          if self.addSpace or self.extraSpace :
             txt = " " + txt

          self.write (txt)

          c = txt [-1]
          self.addSpace = self.isLetterOrDigit (c)
          self.extraSpace = c != '('

   def sendChr (self, txt) :
       self.send (quoteString (txt, "'"))

   def sendStr (self, txt) :
       self.send (quoteString (txt))

   def style_no_space (self) :
       self.extraSpace = False

   def style_indent (self) :
       self.putCondEol ()
       self.incIndent ()

   def style_unindent (self) :
       self.decIndent ()
       self.putCondEol ()

   def style_new_line (self) :
       self.putCondEol ()

   def style_empty_line (self) :
       self.putCondEol ()
       self.addEmptyLine = True

   # -----------------------------------------------------------------------

   # sections

   def setSections (self, sections_param) :
       self.sections = sections_param

   def openSection (self, obj) :
       if self.sections != None :
          self.sections.openSection (obj)

   def closeSection (self) :
       if self.sections != None :
          self.sections.closeSection ()

   def simpleSection (self, obj) :
       if self.sections != None :
          self.sections.simpleSection (obj)

   def setInk (self, ink) :
       if self.sections != None :
          self.sections.setInk (ink)

   def setPaper (self, paper) :
       if self.sections != None :
          self.sections.setPaper (paper)

   def addToolTip (self, text, tooltip) :
       if self.sections != None :
          self.sections.addToolTip (text, tooltip)

   def addDefinition (self, text, defn) :
       if self.sections != None :
          self.sections.addDefinition (text, defn)

   def addUsage (self, text, usage) :
       if self.sections != None :
          self.sections.addUsage (text, usage)

# --------------------------------------------------------------------------

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
