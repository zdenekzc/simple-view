#!/usr/bin/env python

from __future__ import print_function

import sys, os

from util import use_pyside2, use_qt5, use_new_api
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

from util import findColor, setEditFont, Text, columnNumber
from util import qstring_starts_with, qstring_to_str, list_count
from input import indexToFileName, fileNameToIndex

# --------------------------------------------------------------------------

def isLetter (c) :
    return c >= 'A' and c <= 'Z' or c >= 'a' and c <= 'z' or c == '_'

def isDigit (c) :
    return c >= '0' and c <= '9'

def isLetterOrDigit (c) :
    return c >= 'A' and c <= 'Z' or c >= 'a' and c <= 'z' or c == '_' or c >= '0' and c <= '9'

class Highlighter (QSyntaxHighlighter) :

   def __init__ (self, parent = None) :
       super (Highlighter, self).__init__ (parent)
       self.enabled = True
       self.enable_info_property = True

       self.keywordFormat = QTextCharFormat ()
       self.keywordFormat.setForeground (findColor ("darkRed"))

       self.identifierFormat = QTextCharFormat ()
       self.identifierFormat.setForeground (findColor ("darkRed"))

       self.qidentifierFormat = QTextCharFormat ()
       self.qidentifierFormat.setForeground (findColor ("green"))

       self.numberFormat = QTextCharFormat ()
       self.numberFormat.setForeground (findColor ("blue"))

       self.realFormat = QTextCharFormat ()
       self.realFormat.setForeground (findColor ("magenta"))

       self.characterFormat = QTextCharFormat ()
       self.characterFormat.setForeground (findColor ("cornflowerblue"))

       self.stringFormat = QTextCharFormat ()
       self.stringFormat.setForeground (findColor ("blue"))

       self.separatorFormat = QTextCharFormat ()
       self.separatorFormat.setForeground (findColor ("orange"))

       self.commentFormat = QTextCharFormat ()
       self.commentFormat.setForeground (findColor ("gray"))

   def highlightBlock (self, text) :
       if not self.enabled :
          return

       # print ("highlightBlock", self.currentBlock().blockNumber())

       use_cursor = self.enable_info_property
       if use_cursor :
          cursor = QTextCursor (self.currentBlock())
          cursor_inx = 0

       cnt = len (text)
       inx = 0

       inside_comment = self.previousBlockState () == 1
       start_comment = 0

       while inx < cnt :
          if inside_comment :
             if inx == 0 :
                inx = 1
             while inx < cnt and (text [inx-1] != '*' or text [inx] != '/')  :
                inx = inx + 1
             if inx < cnt:
                inx = inx + 1
                self.setFormat (start_comment, inx-start_comment, self.commentFormat)
                inside_comment = False
          else :

             while inx < cnt and text [inx] <= ' ' :
                inx = inx + 1

             start = inx

             if inx < cnt :
                c = text [inx]

                if use_cursor :
                   cursor.movePosition (QTextCursor.NextCharacter, QTextCursor.MoveAnchor, inx+1-cursor_inx)
                   cursor_inx = inx+1
                   fmt = cursor.charFormat ()

                if isLetter (c) :
                   while inx < cnt and isLetterOrDigit (text [inx]) :
                      inx = inx + 1

                   if use_cursor and fmt.hasProperty (Text.infoProperty) :
                      pass # no higligting for identifier with infoProperty
                   else :
                      if c == 'Q' :
                          self.setFormat (start, inx-start, self.qidentifierFormat)
                      else :
                          self.setFormat (start, inx-start, self.identifierFormat)

                elif isDigit (c) :
                   while inx < cnt and isDigit (text [inx]) :
                      inx = inx + 1
                   if use_cursor and fmt.hasProperty (Text.infoProperty) :
                      pass # no higligting for identifier with infoProperty
                   else :
                      self.setFormat (start, inx-start, self.numberFormat)

                elif c == '"' :
                   inx = inx + 1
                   while inx < cnt and text [inx] != '"' :
                      inx = inx + 1
                   inx = inx + 1
                   if use_cursor and fmt.hasProperty (Text.infoProperty) :
                      pass # no higligting for identifier with infoProperty
                   else :
                      self.setFormat (start, inx-start, self.stringFormat)

                elif c == '\'' :
                   inx = inx + 1
                   while inx < cnt and text [inx] != '\'' :
                      inx = inx + 1
                   inx = inx + 1
                   if use_cursor and fmt.hasProperty (Text.infoProperty) :
                      pass # no higligting for identifier with infoProperty
                   else :
                      self.setFormat (start, inx-start, self.characterFormat)

                elif c == '/' :
                   inx = inx + 1
                   if inx < cnt and text [inx] == '/' :
                      inx = cnt # end of line
                      self.setFormat (start, inx-start, self.commentFormat)
                   elif inx < cnt and text [inx] == '*' :
                      inx = inx + 1 # skip asterisk
                      inside_comment = True
                      start_comment = inx - 2 # back to slash
                   else :
                      if use_cursor and fmt.hasProperty (Text.infoProperty) :
                         pass # no higligting for identifier with infoProperty
                      else :
                         self.setFormat (start, inx-start, self.separatorFormat)

                else :
                   inx = inx + 1
                   if use_cursor and fmt.hasProperty (Text.infoProperty) :
                      pass # no higligting for identifier with infoProperty
                   else :
                      self.setFormat (start, inx-start, self.separatorFormat)

       if inside_comment :
          self.setFormat (start_comment, inx-start_comment, self.commentFormat)
          self.setCurrentBlockState (1)
       else :
          self.setCurrentBlockState (0)

# --------------------------------------------------------------------------

class CompletionTextEdit (QPlainTextEdit) :

   def __init__ (self, parent = None) :
       super (CompletionTextEdit, self).__init__ (parent)

       self.win = None
       self.completer = None

       self.minLength = 1
       self.automatic_completion = False
       # self.automatic_completion == False ... popup is displayed only when Ctrl+Space is pressed

       localList = [ ]
       localCompleter = QCompleter (localList, self)
       self.setCompleter (localCompleter, filtered = True)

   def setCompleter (self, completer, filtered = False) :
       if self.completer :
           # self.disconnect (self.completer, SIGNAL ("activated(const QString&)"),  self.insertCompletion)
           self.completer.activated.disconnect (self.insertCompletion)
       if completer == None :
           return

       completer.setWidget (self)

       if filtered :
          completer.setCompletionMode (QCompleter.PopupCompletion)
       else :
          completer.setCompletionMode (QCompleter.UnfilteredPopupCompletion)

       completer.setCaseSensitivity (Qt.CaseInsensitive)

       self.completer = completer
       # self.connect (self.completer, SIGNAL ("activated(const QString&)"), self.insertCompletion)
       self.completer.activated.connect (self.insertCompletion)

   def insertCompletion (self, completion) :
       if self.completer.widget() == self :
          tc = self.textCursor ()
          if use_new_api :
             extra = len (completion) -  len (self.completer.completionPrefix())
          else :
             extra = completion.length() -  self.completer.completionPrefix().length()
          if extra != 0 :
             tc.movePosition (QTextCursor.Left)
             tc.movePosition (QTextCursor.EndOfWord)
          if use_new_api :
             tc.insertText (completion [-extra : ])
          else :
             tc.insertText (completion.right (extra))
          self.setTextCursor (tc)

   def textUnderCursor (self) :
       tc = self.textCursor ()
       tc.select (QTextCursor.WordUnderCursor)
       return tc.selectedText ()

   def focusInEvent (self, event) :
       if self.completer :
           self.completer.setWidget (self);
       QPlainTextEdit.focusInEvent (self, event)

   def focusOutEvent (self, event) :
       QPlainTextEdit.focusOutEvent (self, event)

   def keyPressEvent (self, event) :
       if self.completer != None and self.completer.popup().isVisible() :
           if event.key () in (
              Qt.Key_Enter,
              Qt.Key_Return,
              Qt.Key_Escape,
              Qt.Key_Tab,
              Qt.Key_Backtab) :
                 event.ignore ()
                 return

       mask = Qt.ShiftModifier | Qt.ControlModifier | Qt.AltModifier | Qt.MetaModifier
       mod = int (event.modifiers () & mask)

       isShortcut = mod == Qt.ControlModifier and event.key () == Qt.Key_Space # Ctrl + Space

       if (self.completer == None or not isShortcut) :
           QPlainTextEdit.keyPressEvent (self, event) # do not process the shortcut when we have a completer
           if not self.automatic_completion :
              return

       ctrlOrShift = mod in (Qt.ControlModifier, Qt.ShiftModifier)
       if self.completer == None or (ctrlOrShift and event.text () == "") : # unicode has not isEmpty method
           # ctrl or shift key on it's own
           return

       eow = "~!@#$%^&*()_+{}|:\"<>?,./;'[]\\-=" # end of word
       if not use_new_api :
          eow = QString (eow)

       hasModifier = ((event.modifiers () != Qt.NoModifier) and not ctrlOrShift)

       # completionList = [ ]
       completionList = self.getCompletionList ()
       if self.win.generateCompletionList != None :
          completionList =  completionList + self.win.generateCompletionList ()
       if len (completionList) == 0 :
          completionList = [ "alpha", "beta", "gamma", "delta" ]
       model = QStringListModel (completionList, self.completer)
       self.completer.setModel (model)

       completionPrefix = self.textUnderCursor ()
       print ("completion", completionPrefix, "," , completionList)

       if use_new_api :
          if (not isShortcut
              and (hasModifier or
                   event.text () == "" or
                   len (completionPrefix) < self.minLength or
                   event.text()[-1] in eow )) :
              self.completer.popup ().hide ()
              print ("hide completer")
              return
       else :
          if (not isShortcut
              and (hasModifier or
                   event.text ().isEmpty () or
                   completionPrefix.length () < self.minLength or
                   eow.contains (event.text().right(1)) )) :
              self.completer.popup ().hide ()
              print ("hide completer")
              return

       if (completionPrefix != self.completer.completionPrefix ()) :
           self.completer.setCompletionPrefix (completionPrefix)
           popup = self.completer.popup ()
           popup.setCurrentIndex (self.completer.completionModel ().index (0,0))

       cr = self.cursorRect ()
       cr.setWidth (self.completer.popup ().sizeHintForColumn (0) +
                    self.completer.popup ().verticalScrollBar ().sizeHint ().width ())
       self.completer.complete (cr) # popup it

   def getCompletionList (self) :
       return [ "alpha", "beta", "gamma" ]

# http://doc.qt.io/qt-5/qtwidgets-tools-customcompleter-example.html
# http://rowinggolfer.blogspot.cz/2010/08/qtextedit-with-autocompletion-using.html

# --------------------------------------------------------------------------

class IndentationTextEdit (CompletionTextEdit) :

   def __init__ (self, parent = None) :
       super (IndentationTextEdit, self).__init__ (parent)

   def getFileName (self) :
       return ""

   def getCommentMark (self) :
       name, ext = os.path.splitext (self.getFileName ())
       mark = ""
       if ext in [".py", ".sh"] :
          mark = "#"
       else :
          mark = "//"
       return mark

   def linesInSelection (self) :
       cursor = self.textCursor ()
       cursor.beginEditBlock ()
       if cursor.hasSelection () :
           start = cursor.selectionStart ()
           stop = cursor.selectionEnd ()

           cursor.setPosition (stop)
           stop_line = cursor.blockNumber ()

           cursor.setPosition (start)
           start_line = cursor.blockNumber ()

           for n in range (stop_line - start_line + 1) :
               cursor.movePosition (QTextCursor.StartOfLine)
               yield cursor
               cursor.movePosition (QTextCursor.NextBlock)
       else :
           cursor.movePosition (QTextCursor.StartOfLine)
           yield cursor
       cursor.endEditBlock ()

   def comment (self) :
       mark = self.getCommentMark () + " "
       for cursor in self.linesInSelection () :
           cursor.insertText (mark)

   def uncomment (self) :
       mark = self.getCommentMark ()
       for cursor in self.linesInSelection () :
           line = cursor.block().text ()
           inx = 0
           cnt = len (line)
           while inx < cnt and line [inx] <= ' ' :
               cursor.movePosition (QTextCursor.NextCharacter)
               inx = inx + 1
           m = len (mark)
           if inx + m <= cnt and line [ inx : inx + m ] == mark :
              for i in range (m) :
                 cursor.deleteChar ()
              inx = inx + m
              if inx < cnt and line [ inx ] == ' ' :
                 cursor.deleteChar ()

   def indent (self) :
       delta = 1
       for cursor in self.linesInSelection () :
           cursor.insertText (" " * delta)

   def unindent (self) :
       delta = 1
       for cursor in self.linesInSelection () :
           # Grab the current line
           line = cursor.block().text ()

           # If the line starts with a tab character, delete it
           if qstring_starts_with (line, "\t") :
               # Delete next character
               cursor.deleteChar ()
               cursor.insertText (" " * (delta-1))

           # Otherwise, delete all spaces until a non-space character is met
           else :
               for char in line [:delta] :
                   if char != " " :
                       break
                   cursor.deleteChar ()

# https://www.binpress.com/tutorial/building-a-text-editor-with-pyqt-part-2/145

# --------------------------------------------------------------------------

class Bookmark (object) :
   def __init__ (self) :
       # self.fileName = ""
       self.line = 0
       self.column = 0
       self.mark = 0

class BookmarkTextEdit (IndentationTextEdit) :

   bookmark_colors = [ QColor (Qt.yellow).lighter (160),
                       QColor (Qt.green).lighter (160),
                       QColor (Qt.blue).lighter (160),
                       QColor (Qt.red).lighter (160),
                       QColor (Qt.gray).lighter (140) ]

   def __init__ (self, parent=None) :
       super (BookmarkTextEdit, self).__init__ (parent)

   def keyPressEvent (self, e) :
       modifiers = int (e.modifiers ())
       if modifiers & Qt.KeypadModifier == 0:
          mask = int (Qt.ShiftModifier | Qt.ControlModifier | Qt.AltModifier | Qt.MetaModifier)
          mod = modifiers & mask # necessary for Ctrl Shift
          key = e.key ()
          if mod == Qt.ControlModifier :
             if key >= Qt.Key_1 and key <= Qt.Key_5 :
                # Ctrl 1 ... Ctrl 5
                self.gotoBookmark (key - Qt.Key_0)
                return
          elif mod == Qt.MetaModifier :
             if key >= Qt.Key_1 and key <= Qt.Key_5 :
                # Win 1 ... Win 5
                self.setBookmark (key - Qt.Key_0)
                return
          elif mod == Qt.ControlModifier + Qt.ShiftModifier :
             # Ctrl Shift 1 ... Ctrl Shift 5
             if key == Qt.Key_Exclam : # ord ('!')
                self.setBookmark (1)
                return
             if key == Qt.Key_At :
                self.setBookmark (2)
                return
             if key == Qt.Key_NumberSign :
                self.setBookmark (3)
                return
             if key == Qt.Key_Dollar :
                self.setBookmark (4)
                return
             if key == Qt.Key_Percent :
                self.setBookmark (5)
                return
       super (BookmarkTextEdit, self).keyPressEvent (e)

   def setBookmark (self, markType = 1) :
       line = self.textCursor ().blockNumber ()
       selections = self.extraSelections ()

       found = False
       inx = 0
       cnt = list_count (selections)
       while inx < cnt and not found :
          item = selections [inx]
          if item.format.hasProperty (Text.bookmarkProperty) :
             if item.format.intProperty (Text.bookmarkProperty) == markType :
                if item.cursor.blockNumber () == line :
                   del selections [inx]
                   self.setExtraSelections (selections)
                   found = True
          inx = inx + 1

       if not found :
          lineColor = self.bookmark_colors [markType-1]
          item = QTextEdit.ExtraSelection ()
          item.format.setBackground (lineColor)
          item.format.setProperty (Text.bookmarkProperty, markType)
          item.format.setProperty (QTextFormat.FullWidthSelection, QVariant (True))
          item.cursor = self.textCursor ()
          selections.append (item)
          self.setExtraSelections (selections)

       if self.win != None :
          self.win.bookmarks.activate ()

   def gotoBookmark (self, markType = 1) :
       line = self.textCursor ().blockNumber ()
       selections = self.extraSelections ()
       found = False
       for item in selections :
           if not found :
              if item.format.hasProperty (Text.bookmarkProperty) :
                 if item.format.intProperty (Text.bookmarkProperty) == markType :
                    if item.cursor.blockNumber () > line :
                       self.setTextCursor (item.cursor)
                       found = True
       for item in selections :
          if not found :
              if item.format.hasProperty (Text.bookmarkProperty) :
                 if item.format.intProperty (Text.bookmarkProperty) == markType :
                    self.setTextCursor (item.cursor)
                    found = True

   def gotoPrevBookmark (self, markType = 1) :
       line = self.textCursor ().blockNumber ()
       extraSelections = self.extraSelections ()
       found = False
       for selection in extraSelections :
           if selection.format.hasProperty (Text.bookmarkProperty) :
                 if selection.cursor.blockNumber () < line :
                    self.setTextCursor (selection.cursor)

   def gotoNextBookmark (self, markType = 1) :
       line = self.textCursor ().blockNumber ()
       extraSelections = self.extraSelections ()
       found = False
       for selection in extraSelections :
           if not found :
              if selection.format.hasProperty (Text.bookmarkProperty) :
                 if selection.cursor.blockNumber () > line :
                    self.setTextCursor (selection.cursor)
                    found = True

   def clearBookmarks (self) :
       "clear all bookmarks in one document"
       selections = self.extraSelections ()
       inx = 0
       cnt = selections.count()
       while inx < cnt :
           if item.format.hasProperty (Text.bookmarkProperty) :
              del selections [inx]
              cnt = cnt - 1
           else :
              inx = inx + 1
       self.setExtraSelections (selections)
       if self.win != None :
          self.win.bookmarks.activate ()

   def getBookmarks (self) :
       result = [ ]
       selections = self.extraSelections ()
       for item in selections :
           if item.format.hasProperty (Text.bookmarkProperty) :
              cursor = item.cursor
              answer = Bookmark ()
              answer.line = cursor.blockNumber () + 1
              answer.column = columnNumber (cursor) + 1
              answer.mark = item.format.intProperty (Text.bookmarkProperty)
              result.append (answer)
       return result

   def setBookmarks (self, bookmarks) :
       selections = self.extraSelections ()
       max = len (self.bookmark_colors)
       for item in bookmarks :
           item = QTextEdit.ExtraSelection ()
           item.cursor = self.textCursor () # important
           item.cursor.movePosition (QTextCursor.Start)
           if item.line > 0 :
              item.cursor.movePosition (QTextCursor.NextBlock, QTextCursor.MoveAnchor, item.line - 1)

           index = item.mark
           if (index < 1) :
              index = 1
           if index > max :
              index = max
           item.format.setBackground (self.bookmark_colors [index-1])
           item.format.setProperty (Text.bookmarkProperty, index)

           item.format.setProperty (QTextFormat.FullWidthSelection, QVariant (True))

           selections.append (item)
       self.setExtraSelections (selections)

# --------------------------------------------------------------------------

class SimpleTextEdit (BookmarkTextEdit) :

   def __init__ (self, parent=None) :
       super (SimpleTextEdit, self).__init__ (parent)

       self.setLineWrapMode (QPlainTextEdit.NoWrap)

       self.setMouseTracking (True) # report mouse move

       self.highlighter = Highlighter (self.document ()) # important: keep reference to highlighter

       self.lastCursor = None
       self.lastUnderline = None
       self.lastUnderlineColor = None

       # self.cursorPositionChanged.connect (self.onCursorPositionChanged)

   def showStatus (self, text) :
       if self.win != None :
          self.win.showStatus (text)

   def onCursorPositionChanged (self) :
       cursor = self.textCursor ()
       line = cursor.blockNumber () + 1
       column = columnNumber (cursor) + 1
       self.showStatus ("Line: " + str (line) + " Col: " + str (column))

   def selectLine (self, line) :
       cursor = self.textCursor ()
       cursor.movePosition (QTextCursor.Start)
       cursor.movePosition (QTextCursor.NextBlock, QTextCursor.MoveAnchor, line-1)
       cursor.movePosition (QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
       self.setTextCursor (cursor)
       self.ensureCursorVisible ()

   def selectLineByPosition (self, pos) :
       cursor = self.textCursor ()
       cursor.setPosition (pos)
       cursor.movePosition (QTextCursor.StartOfLine)
       cursor.movePosition (QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
       self.setTextCursor (cursor)
       self.ensureCursorVisible ()

   def select (self, start_line, start_col, stop_line, stop_col) :
       cursor = self.textCursor ()
       cursor.movePosition (QTextCursor.Start)
       cursor.movePosition (QTextCursor.NextBlock, QTextCursor.MoveAnchor, start_line-1)
       cursor.movePosition (QTextCursor.NextCharacter, QTextCursor.MoveAnchor, start_col-1)

       if start_line == stop_line :
          cursor.movePosition (QTextCursor.NextCharacter, QTextCursor.KeepAnchor, stop_col-start_col+1)
       else :
          cursor.movePosition (QTextCursor.NextBlock, QTextCursor.KeepAnchor, stop_line-start_line)
          cursor.movePosition (QTextCursor.StartOfLine, QTextCursor.KeepAnchor)
          cursor.movePosition (QTextCursor.NextCharacter, QTextCursor.KeepAnchor, stop_col)

       self.setTextCursor (cursor)

   def event (self, e) :
       type = e.type()
       "show tooltip for current word"
       if type == QEvent.ToolTip :
          tooltip = ""
          cursor = self.cursorForPosition (e.pos ())
          cursor.select (QTextCursor.WordUnderCursor)
          if cursor.selectedText() != "" :
             fmt = cursor.charFormat ()
             if fmt.hasProperty (QTextFormat.TextToolTip) :
                tooltip = fmt.toolTip()
             if tooltip == "" :
               if fmt.hasProperty (Text.defnProperty) :
                  tooltip = fmt.stringProperty (Text.defnProperty)
             if tooltip == "" :
               if fmt.hasProperty (Text.infoProperty) :
                  tooltip = fmt.stringProperty (Text.infoProperty)
          if tooltip != "" :
             QToolTip.showText (e.globalPos(), tooltip)
          else :
             QToolTip.hideText ()
          return True
       else :
          return super (SimpleTextEdit, self).event (e)

   def mouseMoveEvent (self, e) :

       "hide previous cursor underline"
       if self.lastCursor != None :
          fmt = self.lastCursor.charFormat ()
          fmt.setFontUnderline (self.lastUnderline)
          fmt.setUnderlineColor (self.lastUnderlineColor)
          self.lastCursor.setCharFormat (fmt)
          self.lastCursor = None

       mask = Qt.ShiftModifier | Qt.ControlModifier | Qt.AltModifier | Qt.MetaModifier
       mod = int (e.modifiers () & mask)

       "Ctrl Mouse Move : underline word under cursor"
       if mod == Qt.ControlModifier :
          cursor = self.cursorForPosition (e.pos ())
          if cursor.selectedText() == "" :
             cursor.select (QTextCursor.WordUnderCursor)
          fmt = cursor.charFormat ()
          if fmt.hasProperty (Text.defnProperty) :
             self.lastCursor = cursor
             self.lastUnderline = fmt.fontUnderline ()
             self.lastUnderlineColor = fmt.underlineColor ()
             fmt.setFontUnderline (True)
             fmt.setUnderlineColor (Qt.red)
             cursor.setCharFormat (fmt)
          elif fmt.hasProperty (Text.infoProperty) :
             self.lastCursor = cursor
             self.lastUnderline = fmt.fontUnderline ()
             self.lastUnderlineColor = fmt.underlineColor ()
             fmt.setFontUnderline (True)
             fmt.setUnderlineColor (Qt.blue)
             cursor.setCharFormat (fmt)
       super (SimpleTextEdit, self).mouseMoveEvent (e)

   def mousePressEvent (self, e) :
       mask = Qt.ShiftModifier | Qt.ControlModifier | Qt.AltModifier | Qt.MetaModifier
       mod = int (e.modifiers () & mask)

       "Ctrl Mouse : show properties"
       if mod == Qt.ControlModifier :
          cursor = self.cursorForPosition (e.pos ())
          cursor.select (QTextCursor.WordUnderCursor)
          fmt = cursor.charFormat ()
          if fmt.hasProperty (Text.infoProperty) :
             name = str (fmt.stringProperty (Text.infoProperty))
             obj = self.findIdentifier (name)
             if obj != None :
                self.win.showProperties (obj)
                # self.jumpToObject (obj)

       "Ctrl Shift Mouse : find compiler data"
       if mod == Qt.ControlModifier + Qt.ShiftModifier :
          cursor = self.cursorForPosition (e.pos ())
          line = cursor.blockNumber () + 1
          column = columnNumber (cursor) + 1
          self.win.findCompilerData (self, line, column)

       super (SimpleTextEdit, self).mousePressEvent (e)

   def jumpToObject (self, obj) :
       if obj != None and self.win != None :
          if hasattr (obj, "src_file") :
             fileName = indexToFileName (obj.src_file)
             line = None
             column = None
             pos = None

             if hasattr (obj, "src_line") :
                line = obj.src_line

             if hasattr (obj, "src_column") :
                column = obj.src_column

             if hasattr (obj, "src_pos") :
                pos = obj.src_pos

             if fileName == self.getFileName () :
                edit = self
             else :
                edit = self.win.loadFile (fileName,)

             if edit != None:
                if line != None:
                   edit.selectLine (line)
                elif pos != None :
                   edit.selectLineByPosition (pos)

          self.win.showProperties (obj)

   def findGlobalData (self) :
       data = getattr (self, "navigator_data", None)
       return data

   def findIdentifier (self, qual_name) :
       qual_name = str (qual_name)
       data = self.findGlobalData ()
       if data != None :
          name_list = qual_name.split (".")
          for name in name_list :
              answer = None
              if hasattr (data, "item_dict") :
                 answer = data.item_dict.get (name)
              if answer == None and hasattr (data, "registered_scopes") : # !?
                 answer = data.registered_scopes.get (name)
              # if answer == None and hasattr (data, "parameters") : # !?
              #    answer = data.parameters.item_dict.get (name)
              # if answer == None and hasattr (data, "variables") : # !?
              #    answer = data.variables.item_dict.get (name)
              if answer == None and isinstance (data, dict) : # !?
                 answer = data.get (name)
              if answer == None :
                 return None
              data = answer
       return data

   def findContext (self, cursor) :
       # print ("----")
       result = ""
       level = 0 # number of closePropert(ies)
       first = True # compare position in first block
       position = cursor.position ()
       found = False
       block = cursor.block ()
       while not found and block.isValid () :
          # print ("line", block.blockNumber())
          begin = block.begin ()

          iterator = block.end ()
          stop = False
          if iterator != begin :
             iterator -= 1 # important
          else :
             stop = True # do not decrement begin iterator
          while not stop and not found :
             fragment = iterator.fragment ();
             ok = True
             if first :
                ok = fragment.position () < position
             if ok :
                fmt = fragment.charFormat ()
                if fmt.hasProperty (Text.closeProperty) :
                   level += 1
                   # print ("close", fmt.stringProperty (Text.closeProperty), level)
                if fmt.hasProperty (Text.openProperty) :
                   # print ("open", fmt.stringProperty (Text.openProperty), level)
                   if level == 0 :
                      result = str (fmt.stringProperty (Text.openProperty))
                      found = True
                      # print ("found", result)
                   level -= 1
                # if fmt.hasProperty (Text.contextProperty) :
                #    result = str (fmt.stringProperty (Text.contextProperty))
                #    # print ("context", result)
                #    found = True
             if iterator != begin : # inside second <while> statement,
                iterator -= 1
             else :
                stop = True
          block = block.previous ()
          first = False
       return result

   def displayProperty (self, menu, format, title, property) :
       if format.hasProperty (property) :
          menu.addAction (title + ": " + str (format.stringProperty (property)))

   def contextMenuEvent (self, e) :
       menu = self.createStandardContextMenu ()

       cursor = self.cursorForPosition (e.pos ())
       cursor.select (QTextCursor.WordUnderCursor)

       if self.win != None :
          menu.addSeparator ()

          fmt = cursor.charFormat ()
          if fmt.hasProperty (Text.infoProperty) :
             name = str (fmt.stringProperty (Text.infoProperty))
             act = menu.addAction ("Show Memo")
             # act.setShortcut ("Ctrl+M")
             act.triggered.connect (lambda param, self = self, name = name: self.showMemo (name))

             act = menu.addAction ("Show References")
             # act.setShortcut ("Ctrl+Y")
             act.triggered.connect (lambda param, self = self, name = name: self.showReferences (name))

             obj = self.findIdentifier (name)
             if obj != None :
                act = menu.addAction ("Show Properties")
                act.triggered.connect (lambda param, self = self, obj = obj: self.win.showProperties (obj))

                act = menu.addAction ("Jump to object")
                act.triggered.connect (lambda param, self = self, obj = obj: self.jumpToObject (obj))

          if getattr (self, "compiler_data", None) != None:
             act = menu.addAction ("Find Compiler Data")
             edit = self
             line = cursor.blockNumber () + 1
             column = columnNumber (cursor) + 1
             act.triggered.connect (lambda param, self = self, line = line, column = column:
                                     self.win.findCompilerData (self, line, column))

       menu.addSeparator ()

       cursor = self.textCursor ()
       text = "line: " + str (cursor.blockNumber () + 1)
       text = text + ", column: " + str (columnNumber (cursor) + 1)
       menu.addAction (text)

       menu.addAction ("selected text: " + cursor.selectedText ())
       menu.addAction ("context: " + self.findContext (cursor))

       fmt = cursor.charFormat ()
       self.displayProperty (menu, fmt, "tooltip", QTextFormat.TextToolTip)
       self.displayProperty (menu, fmt, "info", Text.infoProperty)
       self.displayProperty (menu, fmt, "defn", Text.defnProperty)
       self.displayProperty (menu, fmt, "open", Text.openProperty)
       self.displayProperty (menu, fmt, "close", Text.closeProperty)
       self.displayProperty (menu, fmt, "outline", Text.outlineProperty)

       # cursor.select (QTextCursor.BlockUnderCursor)
       # fmt = cursor.blockFormat ()
       # self.displayProperty (menu, fmt, "block tooltip", QTextFormat.TextToolTip)

       menu.exec_ (e.globalPos())

   def getCompletionList (self) :
       result = [ ]
       cursor = self.textCursor ()
       # print ("getCompletionList findContext")
       context = self.findContext (cursor)
       # print ("getCompletionList after findContext")
       obj = None
       if context == "" :
          obj = self.findGlobalData ()
       else :
          obj = self.findIdentifier (context)
       # print ("getCompletionList context=", context)
       while obj != None :
          if hasattr (obj, "item_list") :
             for item in obj.item_list :
                 result.append (item.item_name)
                 # print ("getCompletionList item", item.item_name)
          obj = getattr (obj, "item_context", None)
       # print ("getCompletionList result=", result)
       return result

   def getCursorInfo (self) :
       name = ""
       cursor = self.textCursor ()
       cursor.select (QTextCursor.WordUnderCursor)
       fmt = cursor.charFormat ()
       if fmt.hasProperty (Text.infoProperty) :
          name = str (fmt.stringProperty (Text.infoProperty))
       return name

   def showMemo (self, name = "") :
       if name == "" :
          name = self.getCursorInfo ()
       if self.win != None :
          self.win.showMemo (self, name)

   def showReferences (self, name = "") :
       if name == "" :
          name = self.getCursorInfo ()
       if self.win != None :
          self.win.showReferences (self, name)

   def gotoNextFunction (self) :
       found = False
       cursor = self.textCursor ()
       block = cursor.block ().next ()
       while not found and block.isValid () :
          iterator = block.begin ()
          while not found and not iterator.atEnd () :
             fragment = iterator.fragment ();
             if fragment.isValid () :
                fmt = fragment.charFormat ()
                if fmt.hasProperty (Text.outlineProperty) :
                   # print ("outline:", fmt.stringProperty (Text.outlineProperty))
                   cursor.setPosition (block.position ())
                   self.setTextCursor (cursor)
                   found = True
             iterator += 1
          block = block.next ()

   def gotoPrevFunction (self) :
       found = False
       cursor = self.textCursor ()
       block = cursor.block ().previous ()
       while not found and block.isValid () :
          iterator = block.end ()
          begin = block.begin ()
          while not found and iterator != begin :
             fragment = iterator.fragment ();
             if fragment.isValid () :
                fmt = fragment.charFormat ()
                if fmt.hasProperty (Text.outlineProperty) :
                   # print ("outline:", fmt.stringProperty (Text.outlineProperty))
                   cursor.setPosition (block.position ())
                   self.setTextCursor (cursor)
                   found = True
             iterator -= 1
          block = block.previous ()

   def gotoBegin (self) :
       self.verticalScrollBar ().triggerAction (QAbstractSlider.SliderToMinimum)

   def gotoEnd (self) :
       self.verticalScrollBar ().triggerAction (QAbstractSlider.SliderToMaximum)

   def gotoPageUp (self) :
       self.verticalScrollBar ().triggerAction (QAbstractSlider.SliderPageStepSub)

   def gotoPageDown (self) :
       self.verticalScrollBar ().triggerAction (QAbstractSlider.SliderPageStepAdd)

   def scrollUp (self) :
       self.verticalScrollBar ().triggerAction (QAbstractSlider.SliderSingleStepSub)

   def scrollDown (self) :
       self.verticalScrollBar ().triggerAction (QAbstractSlider.SliderSingleStepAdd)

   def scrollLeft (self) :
       self.horizontalScrollBar ().triggerAction (QAbstractSlider.SliderSingleStepSub)

   def scrollRight (self) :
       self.horizontalScrollBar ().triggerAction (QAbstractSlider.SliderSingleStepAdd)

   def enlargeFont (self) :
       font = self.document().defaultFont()
       if font.pixelSize () > 0 :
          font.setPixelSize (font.pixelSize () + 1)
       else :
          font.setPointSize (font.pointSize () + 1)
       self.document().setDefaultFont (font)

   def shrinkFont (self) :
       font = self.document().defaultFont()
       if font.pixelSize () > 0 :
          if font.pixelSize () > 8 :
             font.setPixelSize (font.pixelSize () - 1)
       else :
          if font.pointSize () > 8 :
             font.setPointSize (font.pointSize () - 1)
       self.document().setDefaultFont (font)

   def moveLines (self, up) :
       cursor = self.textCursor ()
       cursor.beginEditBlock ()

       if not cursor.hasSelection () :
          cursor.movePosition (QTextCursor.StartOfBlock)
          cursor.movePosition (QTextCursor.NextBlock, QTextCursor.KeepAnchor)
          # NO cursor.select (QTextCursor.LineUnderCursor)
       self.setTextCursor (cursor) # important

       # data = self.createMimeDataFromSelection ()
       # print (data.text ())
       self.cut ()
       self.setTextCursor (cursor)


       cursor = self.textCursor ()

       if up :
          cursor.movePosition (QTextCursor.PreviousBlock)
       else :
          cursor.movePosition (QTextCursor.NextBlock)

       self.setTextCursor (cursor)

       self.paste ()
       # self.insertFromMimeData (data)

       cursor.movePosition (QTextCursor.PreviousBlock)
       self.setTextCursor (cursor)
       cursor.endEditBlock ()

   def moveLinesUp (self) :
       self.moveLines (True)

   def moveLinesDown (self) :
       self.moveLines (False)

# --------------------------------------------------------------------------

class Editor (SimpleTextEdit) :

   def __init__ (self, parent=None) :
       super (Editor, self).__init__ (parent)

       self.findBox = None
       self.lineBox = None
       self.origFileName = ""
       self.origTimeStamp = 0
       self.origText = ""
       self.closeWithoutQuestion = False
       setEditFont (self)

   def findText (self) :
       if self.lineBox :
          self.lineBox.hide ()
       if self.findBox :
          self.findBox.edit = self
          self.copyNonEmptySelectedText ()
          self.findBox.open ()

   def findNext (self) :
       if self.findBox :
          self.findBox.edit = self
          self.findBox.findNext ()

   def findPrev (self) :
       if self.findBox :
          self.findBox.edit = self
          self.findBox.findPrev ()

   def replaceText (self) :
       if self.lineBox :
          self.lineBox.hide ()
       if self.findBox :
          self.findBox.edit = self
          self.copyNonEmptySelectedText ()
          self.findBox.open ()

   def findSelected (self) :
       self.findText ()
       if self.findBox :
          self.copySelectedText ()

   def findIncremental (self) :
       self.findText ()
       if self.findBox :
          self.copySelectedText ()
          self.findBox.incremental = True

   def goToLine (self) :
       if self.findBox :
          self.findBox.hide ()
       if self.lineBox :
          self.lineBox.edit = self
          self.lineBox.open ()

   def copySelectedText (self) :
       if self.findBox :
          text = self.textCursor ().selectedText ()
          self.findBox.line.lineEdit().setText (text)

   def copyNonEmptySelectedText (self) :
       if self.findBox :
          text = self.textCursor ().selectedText ()
          if text != "" :
             self.findBox.line.lineEdit().setText (text)

   def getFileName (self) :
       return self.origFileName

   def simpleReadFile (self, fileName) :
       f = open (fileName)
       text = f.read ()
       self.setPlainText (text)

   def readFileData (self, fileName) :
       text = ""
       f = QFile (fileName)
       if not f.open (QIODevice.ReadOnly) :
          raise IOError (qstring_to_str (f.errorString()))
       else :
          try :
             stream = QTextStream (f)
             stream.setCodec ("UTF-8")
             text = stream.readAll ()
          except Exception as e :
             QMessageBox.warning (self, "Read File Error", "Cannot read file %s: %s" % (fileName, e))
          finally :
             f.close ()
       return text

   def writeFileData (self, fileName) :
       text = self.toPlainText ()
       f = QFile (fileName)
       if not f.open (QIODevice.WriteOnly) :
              raise IOError (qstring_to_str (f.errorString ()))
       else :
          try :
             stream = QTextStream (f)
             stream.setCodec ("UTF-8")
             stream << text
             self.document ().setModified (False)
             self.origText = text
          except Exception as e :
             QMessageBox.warning (self, "Write File Error", "Failed to save %s: %s" % (fileName, e))
          finally :
             f.close ()
             # QMessageBox.information (self, "File Save", "File written %s" % (fileName))

   def readFile (self, fileName) :
       fileName = os.path.abspath (fileName)
       self.origFileName = fileName
       self.origTimeStamp = os.path.getmtime (fileName)

       text = self.readFileData (fileName)

       if len (text) > 640*1024 : # !?
          self.highlighter.enabled = False

       self.origText = text
       self.setPlainText (text)
       self.document ().setModified (False)

       fi = QFileInfo (fileName)
       self.setWindowTitle (fi.fileName ())

   def writeFile (self, fileName) :
       fileName = os.path.abspath (fileName)
       self.origFileName = fileName
       # print ("writeFile", fileName)
       self.writeFileData (fileName)
       self.origTimeStamp = os.path.getmtime (fileName)

   def isModified (self) :
       # return self.document ().isModified ()
       text = self.toPlainText ()
       return text != self.origText

   def isModifiedOnDisk (self) :
       result = False
       if os.path.getmtime (self.origFileName) > self.origTimeStamp :
          result = True
       return result

   def isDifferentOnDisk (self) :
       result = False
       text = self.readFileData (self.origFileName)
       if text != self.toPlainText () :
          "text changed"
          result = True
       return result

   def openFile (self) :
       fileName = str (QFileDialog.getOpenFileName (self, "Open File"))
       if fileName != "" :
          self.readFile (fileName)

   def saveFile (self) :
       self.writeFile (self.origFileName)

   def saveFileAs (self) :
       fileName = str (QFileDialog.getSaveFileName (self, "Save File As", self.origFileName))
       if fileName != "" :
          self.writeFile (fileName)

# --------------------------------------------------------------------------

class FindBox (QWidget) :

   def __init__ (self, parent = None) :
       super (FindBox, self).__init__ (parent)

       self.edit = None
       self.small = False
       self.incremental = False

       self.red = QColor (Qt.red).lighter (160)
       self.green = QColor (Qt.green).lighter (160)

       self.horiz_layout = QHBoxLayout ()
       self.setLayout (self.horiz_layout)

       self.closeButton = QToolButton ()
       self.closeButton.setIcon (QIcon.fromTheme ("dialog-close")) # !?
       self.closeButton.setShortcut ("Esc")
       self.closeButton.clicked.connect (self.hide)
       self.horiz_layout.addWidget (self.closeButton)

       self.label = QLabel ()
       self.label.setText ("Find:")
       self.horiz_layout.addWidget (self.label)

       self.line = QComboBox ()
       self.line.setEditable (True)
       # self.line.setFrame (False)
       # self.line.setDuplicatesEnabled (False)
       # self.line.setInsertPolicy (QComboBox.InsertAtBottom)
       self.horiz_layout.addWidget (self.line)

       self.orig_palette = self.line.palette ()

       self.clearButton = QToolButton ()
       self.clearButton.setIcon (QIcon.fromTheme ("edit-clear-list"))
       self.clearButton.clicked.connect (self.line.clearEditText)
       self.horiz_layout.addWidget (self.clearButton)

       self.wholeWords = QCheckBox ()
       self.wholeWords.setText ("Whole &words")
       self.horiz_layout.addWidget (self.wholeWords)

       self.matchCase = QCheckBox ()
       self.matchCase.setText ("Match &case")
       self.horiz_layout.addWidget (self.matchCase)

       self.nextButton = QPushButton ()
       self.nextButton.setText ("&Next")
       self.nextButton.clicked.connect (self.findNext)
       self.horiz_layout.addWidget (self.nextButton)

       self.prevButton = QPushButton ()
       self.prevButton.setText ("&Prev")
       self.prevButton.clicked.connect (self.findPrev)
       self.horiz_layout.addWidget (self.prevButton)

       self.horiz_layout.setStretch (2, 10)

       self.line.lineEdit().returnPressed.connect (self.returnPressed)
       self.line.editTextChanged.connect (self.textChanged)

   def resizeEvent (self, e) :
       w = e.size().width()
       if w < 640 :
          if not self.small :
             self.wholeWords.setText ("&Words")
             self.matchCase.setText ("&Case")
             self.small = True
       else :
          if self.small :
             self.wholeWords.setText ("Whole &words")
             self.matchCase.setText ("Match &case")
             self.small = False
       super (FindBox, self).resizeEvent (e)

   def returnPressed (self) :
       self.findNext ()

   def textChanged (self, text) :
       self.findNext ()
       if self.edit != None :
          self.setColor (text)

   def setColor (self, text) :
       if self.edit == None :
          self.line.lineEdit().setPalette (self.orig_palette)
       else :
          opt = QTextDocument.FindFlags (0)
          if self.wholeWords.isChecked () :
             opt = opt | QTextDocument.FindWholeWords
          if self.matchCase.isChecked () :
             opt = opt | QTextDocument.FindCaseSensitively

          if self.incremental :
             cursor = self.edit.textCursor ()
             cursor.setPosition (self.start)
             self.edit.setTextCursor (cursor)
          else :
             cursor = self.edit.textCursor ()
             pos = cursor.position ()

          ok = self.edit.find (text, opt)
          if not ok :
             ok = self.edit.find (text, opt | QTextDocument.FindBackward)

          if not self.incremental :
             cursor.setPosition (pos)
             self.edit.setTextCursor (cursor)

          if ok :
             color = self.green
          else :
             color = self.red
          widget = self.line.lineEdit()
          palette = widget.palette ()
          role = widget.backgroundRole ()
          palette.setColor (role, color)
          widget.setPalette (palette)

   def setEdit (self, edit) :
       self.edit = edit
       text = self.line.currentText ()
       self.setColor (text)

   def open (self) :
       self.show ()
       self.line.setFocus ()
       self.line.lineEdit ().selectAll () # enable editing
       self.start = 0
       if self.edit != None :
          self.start = self.edit.textCursor().position()

   def findNext (self) :
       self.findStep (False)

   def findPrev (self) :
       self.findStep (True)

   def findStep (self, back) :
       text = self.line.currentText ()
       if text != "" :
          if self.line.findText (text) == -1 :
             self.line.addItem (text)

          opt = QTextDocument.FindFlags (0)
          if self.wholeWords.isChecked () :
             opt = opt | QTextDocument.FindWholeWords
          if self.matchCase.isChecked () :
             opt = opt | QTextDocument.FindCaseSensitively
          if back :
             opt = opt | QTextDocument.FindBackward

          if self.edit != None :
             ok = self.edit.find (text, opt)
             if not ok :
                if back :
                   self.edit.moveCursor (QTextCursor.End)
                else :
                   self.edit.moveCursor (QTextCursor.Start)
                self.edit.find (text, opt)

# --------------------------------------------------------------------------

class GoToLineBox (QWidget) :

   def __init__ (self, parent=None) :
       super (GoToLineBox, self).__init__ (parent)

       self.edit = None

       self.horiz_layout = QHBoxLayout ()
       self.setLayout (self.horiz_layout)

       self.closeButton = QToolButton ()
       self.closeButton.setIcon (QIcon.fromTheme ("dialog-close")) # !?
       self.closeButton.setShortcut ("Esc")
       self.closeButton.clicked.connect (self.hide)
       self.horiz_layout.addWidget (self.closeButton)

       self.label = QLabel ()
       self.label.setText ("Go to line:")
       self.horiz_layout.addWidget (self.label)

       self.line = QSpinBox ()
       self.horiz_layout.addWidget (self.line)

       self.button = QPushButton ()
       self.button.setText ("Go")
       self.horiz_layout.addWidget (self.button)

       self.horiz_layout.addStretch ()

       self.line.editingFinished.connect (self.editingFinished)

   def open (self) :
       cursor = self.edit.textCursor ()
       document = self.edit.document ()
       self.line.setMinimum (1)
       self.line.setMaximum (document.blockCount ())
       self.line.setValue (cursor.blockNumber () + 1) # line number
       self.line.setFocus ()
       self.line.selectAll () # enable editing
       self.show ()

   def editingFinished (self) :
       self.edit.selectLine (self.line.value ())

# --------------------------------------------------------------------------

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
