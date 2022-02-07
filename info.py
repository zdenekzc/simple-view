#!/usr/bin/env python

from __future__ import print_function

import sys, os, re, traceback

from util import use_pyside2, use_qt5, use_python3, simple_bytearray_to_str
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

from util import Text, findColor

# --------------------------------------------------------------------------

class Redirect (object) :
   def __init__ (self, target) :
       self.target = target
       self.buffer = ""

       self.save_out = sys.stdout
       self.save_err = sys.stderr

       sys.stdout = self
       sys.stderr = self

   def write (self, text) :
       if self.save_out != None :
          self.save_out.write (text)

       try:
          text = self.buffer + text
          inx = text.find ("\n")
          while inx > 0 :
             line = text [ : inx ]
             self.target.commandOneLine (line)
             text = text [ inx + 1 : ]
             inx = text.find ("\n")

          self.buffer = text
       except :
           sys.stdout = self.save_out
           sys.stderr = self.save_err

           sys.stderr.write ("\n")
           sys.stderr.write ("EXCEPTION during stderr redirect")
           sys.stderr.write ("\n")
           sys.stderr.write ("\n")
           traceback.print_exc ()
           sys.stderr.write ("\n")

           sys.stdout = self
           sys.stderr = self

   def send_buffer (self) :
       if self.buffer != "" :
          self.target.commandOneLine (self.buffer)
          self.buffer = ""

   def flush (self) :
       self.send_buffer ()
       if self.save_out != None :
          self.save_out.flush ()

   def duplicate (self, text) :
       self.save_out.write (text)

   def close (self) :
       self.send_buffer ()
       sys.stdout = self.save_out
       sys.stderr = self.save_err

# --------------------------------------------------------------------------

class Info (QPlainTextEdit) :

   def __init__ (self, win) :
       super (Info, self).__init__ (win)
       self.win = win
       self.setLineWrapMode (QPlainTextEdit.NoWrap)

       self.process = None

       self.stopAction = None
       self.directory = ""
       self.buffer = ""
       self.redirect = None
       self.redirect_count = 0

       self.red = findColor ("red")
       self.green = findColor ("green")
       self.blue = findColor ("blue")
       self.gray = findColor ("gray")
       self.norm = findColor ("ink")
       self.brown = findColor ("brown")
       self.orange = findColor ("orange")
       self.yellow = findColor ("yellow")
       self.cornflowerblue = findColor ("cornflowerblue")

   # -- redirect output --

   def redirectOutput (self) :
       self.redirect_count = self.redirect_count + 1
       if self.redirect_count == 1 :
          self.redirect = Redirect (self)

   def restoreOutput (self) :
       self.redirect_count = self.redirect_count - 1
       if self.redirect_count == 0 :
          self.redirect.close ()

   # -- color output --

   def colorText (self) :
       cursor = self.textCursor ()

       format = cursor.charFormat ()
       format.setForeground (self.blue)
       cursor.setCharFormat (format)

       cursor.insertText ("blue line\n")

       format = cursor.charFormat ()
       format.setForeground (self.red)
       cursor.setCharFormat (format)

       cursor.insertText ("red line")

   def setColor (self, cursor, color) :
       format = cursor.charFormat ()
       format.setForeground (color)
       cursor.setCharFormat (format)

   def setNote (self, cursor, note) :
       format = cursor.charFormat ()
       format.setProperty (Text.locationProperty, note)
       cursor.setCharFormat (format)

   def clearNote (self, cursor) :
       format = cursor.charFormat ()
       format.clearProperty (Text.locationProperty)
       cursor.setCharFormat (format)

   # -- grep with ANSI colors --

   def colorDataReady (self) :
       cursor = self.textCursor ()
       cursor.movePosition (cursor.End)

       txt = ""
       esc = False
       code = ""
       normal = True

       data = simple_bytearray_to_str (self.process.readAll ())
       self.redirect.duplicate (data)

       for c in data :
          if c == chr (27) :
             esc = True
             code = ""
          elif esc :
             code = code + c
             if not (c == '[' or c >= '0' and c <= '9' or c == ';') :
                if txt != "" :
                   cursor.insertText (txt)
                   txt = ""
                esc = False
                if code == "[35m" :
                   self.setColor (cursor, self.blue) # magenta
                   normal = False
                elif code == "[36m" :
                   self.setColor (cursor, self.gray)
                   normal = False
                elif code == "[32m" :
                   self.setColor (cursor, self.green)
                   normal = False
                elif code == "[01;31m" :
                   self.setColor (cursor, self.red)
                   normal = False
                elif code == "[m" :
                   if not normal :
                      self.setColor (cursor, self.norm)
                      normal = True
          else :
              txt = txt + c

       if txt != "" :
          cursor.insertText (txt)

       self.ensureCursorVisible ()

   # -- grep in output window --

   def grepPutLine (self, cursor, text) :
       self.setNote (cursor, text[1] + ":" + text[3])
       cursor.insertText (text [0])
       self.setColor (cursor, self.blue)
       cursor.insertText (text [1])
       self.setColor (cursor, self.gray)
       cursor.insertText (text [2])
       self.setColor (cursor, self.green)
       cursor.insertText (text [3])
       self.setColor (cursor, self.gray)
       cursor.insertText (text [4])
       self.setColor (cursor, self.norm)
       cursor.insertText (text [5])
       self.setColor (cursor, self.red)
       cursor.insertText (text [6])
       self.setColor (cursor, self.norm)
       cursor.insertText (text [7])

   def grepDataReady (self) :
       cursor = self.textCursor ()
       cursor.movePosition (QTextCursor.End)

       esc = False
       code = ""
       txt = ""
       section = 0
       text = ["", "", "", "", "", "", "", ""]

       data = simple_bytearray_to_str (self.process.readAll ())
       self.redirect.duplicate (data)

       for c in data :
          if c == chr (10) :
             text [section] = text [section] + txt
             self.grepPutLine (cursor, text)
             cursor.insertText (c)
             # re-initialize
             esc = False
             code = ""
             txt = ""
             section = 0
             text = ["", "", "", "", "", "", "", ""]
          elif c == chr (27) :
             esc = True
             code = ""
          elif esc :
             code = code + c
             if not (c == '[' or c >= '0' and c <= '9' or c == ';') :
                if txt != "" :
                   text [section] = text [section] + txt
                   txt = ""
                esc = False
                if code == "[35m" :
                   # magenta (blue)
                   section = 1
                elif code == "[36m" :
                   # gray
                   if section == 1 or section == 3 :
                      section = section + 1
                elif code == "[32m" :
                   # green
                   section = 3
                elif code == "[01;31m" :
                   # red
                   section = 6
                elif code == "[m" :
                   # black
                   if section == 4 or section == 6 :
                      section = section + 1
          else :
             txt = txt + c

       self.grepPutLine (cursor, text)
       self.ensureCursorVisible ()

   def grep (self, params) :
       self.process = QProcess (self)
       self.process.setProcessChannelMode (QProcess.MergedChannels)
       self.process.readyRead.connect (self.grepDataReady)
       if self.stopAction != None :
          self.process.started.connect (lambda: self.stopAction.setEnabled (True))
          self.process.finished.connect (lambda: self.stopAction.setEnabled (False))
       self.process.start ("/bin/sh", [ "-c", "grep " + params + " -n -r . --color=always" ] )
       # self.process.waitForFinished ()

   # -- gcc options --

   def gccLine (self, cursor, line) :
       cont = False
       for word in line.split () :
           style = False

           if not cont :
              if word.endswith (".c") or  word.endswith (".cc") or word.endswith (".cpp") :
                 self.setColor (cursor, self.brown)
                 style = True

           if not cont :
              if word.startswith ("-I") :
                 self.setColor (cursor, self.green)
                 style = True
              elif word.startswith ("-D") or word.startswith ("-U") :
                 self.setColor (cursor, self.orange)
                 style = True
              elif word.startswith ("-L") :
                 self.setColor (cursor, self.cornflowerblue)
                 style = True
              elif word.startswith ("-l") :
                 self.setColor (cursor, self.blue)
                 style = True
              elif word.startswith ("-o") :
                 self.setColor (cursor, self.red)
                 style = True

           next_cont = style and len (word) == 2

           cursor.insertText (word)

           if style and not next_cont or cont :
              self.setColor (cursor, self.norm)

           cont = next_cont

           cursor.insertText (" ")

   # -- make output --

   def modifyLine (self, cursor, line, keyword) :
       pattern = "(.*\s)?(\S*):(\d\d*):(\d\d*):(\s*" + keyword + ":)(.*)"
       m = re.search (pattern, line)
       if m :
          mark = os.path.join (self.directory, m.group (2)) + ":" + m.group (3) + ":" + m.group (4)

          self.setNote (cursor, mark)

          if m.group (1) != None :
             cursor.insertText (m.group (1))

          self.setColor (cursor, self.blue)
          cursor.insertText (m.group (2))
          self.setColor (cursor, self.norm)
          cursor.insertText (":")

          self.setColor (cursor, self.green)
          cursor.insertText (m.group (3))
          self.setColor (cursor, self.norm)
          cursor.insertText (":")

          self.setColor (cursor, self.gray)
          cursor.insertText (m.group (4))

          self.setColor (cursor, self.red)
          cursor.insertText (m.group (5))

          self.setColor (cursor, self.orange)
          cursor.insertText (m.group (6))
          self.setColor (cursor, self.norm)

          self.clearNote (cursor)  # before end of line, otherwise format is not changed
       else :
          self.setColor (cursor, self.brown)
          cursor.insertText (line)
          self.setColor (cursor, self.norm)

   def directoryLine (self, cursor, line) :
       pattern = "Entering directory '([^']*)'"
       m = re.search (pattern, line)
       if m :
          self.directory = m.group (1)
          self.setColor (cursor, self.orange)
       else :
          self.setColor (cursor, self.brown)
       cursor.insertText (line)
       self.setColor (cursor, self.norm)

   # -- Python trace --

   def pythonLine (self, cursor, line) :
       pattern = "  File (.*), line ([0-9]*)(, in (.*))?"
       m = re.match (pattern, line)
       if m :
          fileName = m.group (1)
          line =  m.group (2)
          if fileName.startswith ('"') and fileName.endswith ('"') :
             fileName = fileName [ 1 : -1 ]
          mark = fileName + ":" + line
          self.setNote (cursor, mark)

          cursor.insertText ("File ")
          self.setColor (cursor, self.blue)
          cursor.insertText (m.group (1))
          self.setColor (cursor, self.norm)

          cursor.insertText (", line ")
          self.setColor (cursor, self.green)
          cursor.insertText (m.group (2))
          self.setColor (cursor, self.norm)

          if m.group (4) != None :
             cursor.insertText (", in ")
             self.setColor (cursor, self.orange)
             cursor.insertText (m.group (4))
             self.setColor (cursor, self.norm)

          self.clearNote (cursor) # before end of line, otherwise format is not changed
       else :
          self.setColor (cursor, self.brown)
          cursor.insertText (line)
          self.setColor (cursor, self.norm)

   def commandOneLine (self, line) :
       cursor = self.textCursor ()
       cursor.movePosition (QTextCursor.End)
       # line = line.rstrip ("\n")
       # line = line.rstrip ("\r")
       # line = line.replace ("\n", "[N]")
       # line = line.replace ("\r", "[R]")

       """
       text = line
       line = ""
       for ch in text :
           if ch <= "\x7f" :
              line = line + ch
       """
       if not use_python3 :
          line = line.decode ("ascii", "ignore")

       if line.find ("error:") >= 0 :
          self.modifyLine (cursor, line, "error")
       elif line.find ("warning:") >= 0 :
          self.modifyLine (cursor, line, "warning")
       elif line.find ("debug:") >= 0 :
          self.modifyLine (cursor, line, "debug")
       elif line.find ("info:") >= 0 :
          self.modifyLine (cursor, line, "info")
       elif line.find ("Entering directory ") >= 0 :
          self.directoryLine (cursor, line)
       elif line.find ("Leaving directory ") >= 0 :
          self.directory = ""
          cursor.insertText (line)
       elif line.startswith ("  File ") :
          self.pythonLine (cursor, line)
       elif line.find ("gcc") >= 0 or line.find ("g++") >= 0 :
          self.gccLine (cursor, line)
       else :
          cursor.insertText (line)
       cursor.insertText ("\n")

   def commandDataReady (self) :
       data = simple_bytearray_to_str (self.process.readAll ())
       self.redirect.duplicate (data)
       for c in data :
           if c == '\n' :
              self.commandOneLine (self.buffer)
              self.buffer = ""
           else :
              self.buffer = self.buffer + c

   def commandDataFinished (self) :
       if self.buffer != "" :
          self.commandOneLine (self.buffer)
          self.buffer = ""
          self.ensureCursorVisible ()

   # -- mouse click --

   def mousePressEvent (self, e) :
       cursor = self.cursorForPosition (e.pos ())
       cursor.select (QTextCursor.WordUnderCursor)
       format = cursor.charFormat ()
       mark = str (format.stringProperty (Text.locationProperty))
       if mark != "" :
          (fileName, line, column) = self.getLocation (mark)
          if fileName != None :
             if e.modifiers () & Qt.ControlModifier :
                self.goToLocation (fileName, line, column)
                self.goToCtrlLocation (fileName, line, column)
             else :
                self.goToLocation (fileName, line, column)
       super (Info, self).mousePressEvent (e)

   def getLocation (self, mark) :
       pattern = "([^:]*)(:([0-9]*)(:([0-9]*))?)?"
       m = re.match (pattern, mark)
       if m :
          fileName = m.group (1)
          line = m.group (3)
          column = m.group (5)
          if line == None or line == "" :
             line = 0
          else :
             line = int (line)
          if column == None or column == "" :
             column = 0
          else :
             column = int (column)
          # print ("file:", fileName)
          # print ("line:",  line)
          # print ("column:", column)
       else :
          fileName = None
          line = 0
          column = 0
       return (fileName, line, column)

   def goToLocation (self, fileName, line, column) :
       if self.win != "" :
          self.win.loadFile (fileName, line, column)

   def goToCtrlLocation (self, fileName, line, column) :
       pass

   # -- jump to next mark --

   def jumpToPrevMark (self) :
       cursor = self.textCursor ()
       cursor.movePosition (QTextCursor.StartOfLine)
       stop = False
       found = False
       while not stop and not found:
          if not cursor.movePosition (QTextCursor.Up) :
             stop = True
          if cursor.charFormat ().hasProperty (Text.locationProperty) :
             found = True
          if cursor.atStart () :
             stop = True

       if found :
          cursor.movePosition (QTextCursor.EndOfLine, QTextCursor.KeepAnchor)

       self.setTextCursor (cursor)
       self.ensureCursorVisible ()

       if found :
          mark = str (cursor.charFormat ().stringProperty (Text.locationProperty))
          (fileName, line, column) = self.getLocation (mark)
          self.goToLocation (fileName, line, column)
          self.win.showStatus ("")
       else :
          self.win.showStatus ("Begin of file")

   def jumpToNextMark (self) :
       cursor = self.textCursor ()
       cursor.movePosition (QTextCursor.StartOfLine)
       stop = False
       found = False
       while not stop and not found:
          if not cursor.movePosition (QTextCursor.NextBlock) :
             stop = True
          if cursor.charFormat ().hasProperty (Text.locationProperty) :
             found = True
          if cursor.atEnd () :
             stop = True

       if found :
          cursor.movePosition (QTextCursor.EndOfLine, QTextCursor.KeepAnchor)

       self.setTextCursor (cursor)
       self.ensureCursorVisible ()

       if found :
          mark = str (cursor.charFormat ().stringProperty (Text.locationProperty))
          (fileName, line, column) = self.getLocation (mark)
          self.goToLocation (fileName, line, column)
          self.win.showStatus ("")
       else :
          self.win.showStatus ("End of file")

   def jumpToLastMark (self) :
       cursor = self.textCursor ()
       cursor.movePosition (QTextCursor.End)
       self.jumpToPrevMark ()

# http://stackoverflow.com/questions/26500429/qtextedit-and-colored-bash-like-output-emulation
# http://stackoverflow.com/questions/22069321/realtime-output-from-a-subprogram-to-stdout-of-a-pyqt-widget

# --------------------------------------------------------------------------

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
