#!/usr/bin/env python

from __future__ import print_function

import sys, os

from util import use_pyside2, use_qt5, use_new_api, use_simple
from util import columnNumber, qstring_to_str, dialog_to_str

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

from input import indexToFileName, fileNameToIndex
from util import findIcon, findColor, setApplStyle, resizeDetailWindow, setEditFont, setZoomFont

from edit import Editor, FindBox, GoToLineBox, Bookmark
from tree import Tree, TreeItem
from grep import GrepWin
from prop import Property
from info import Info

from small import TreeDir, Documents, Bookmarks, Navigator, Memo, References, Structure

from tools import InfoWithTools

# --------------------------------------------------------------------------

class Settings (QSettings):

   def __init__ (self, fileName, formatType) :
       super (Settings, self).__init__ (fileName, formatType)

   def string (self, name, init = "") :
       result = self.value (name, init)
       if use_new_api :
          return str (result)
       else :
          return str (result.toString ())

   def boolean (self, name, init = False) :
       s = self.value (name, "")
       result = False
       if s == "true" or s == "True" or s == "1" :
          result = True
       return result

# --------------------------------------------------------------------------

class ViewTabWidget (QTabWidget):

   def __init__ (self, parent = None, win = None) :
       super (ViewTabWidget, self).__init__ (parent)
       self.win = win
       self.currentChanged.connect (self.onCurrentChanged)

   def onCurrentChanged (self, index) :
       if self.win != None :

          findBox = self.win.findBox
          if findBox :
             edit = self.widget (index)
             if not isinstance (edit, Editor) :
                edit = None
             findBox.setEdit (edit)

          self.win.emitTabChanged (self, index)

# --------------------------------------------------------------------------

class ToolTabWidget (QTabWidget):
   def __init__ (self, parent = None) :
       super (ToolTabWidget, self).__init__ (parent)

# --------------------------------------------------------------------------

class MainWindow (QMainWindow):

   def __init__ (self, parent = None) :
       super (MainWindow, self).__init__ (parent)

# --------------------------------------------------------------------------

class DetailWindow (MainWindow):

   def __init__ (self, win) :
       super (DetailWindow, self).__init__ (win)
       self.win = win

       self.items = { }

       self.tabWidget = ViewTabWidget (self, self.win)
       self.tabWidget.setMovable (True)
       self.setCentralWidget (self.tabWidget)

       resizeDetailWindow (self)

   def addItem (self, fileName) :
       if fileName not in self.items :
          w = Editor ()
          w.win = self.win
          w.tabWidget = self.tabWidget
          self.items [fileName] = w
          name = os.path.basename (fileName)
          self.tabWidget.addTab (w, name)
       w = self.items [fileName]
       self.tabWidget.setCurrentWidget (w)
       return w

# --------------------------------------------------------------------------

class CentralWindow (MainWindow):

   if use_pyside2 :
      tabChanged = Signal (ViewTabWidget, int)
   else :
      tabChanged = pyqtSignal (ViewTabWidget, int)

   def emitTabChanged (self, tab, index) :
       self.tabChanged.emit (tab, index)

   def __init__ (self, parent = None) :
       super (CentralWindow, self).__init__ (parent)

       self.appl = None

       self.editors = { }

       self.commands = Settings ("tools.ini", QSettings.IniFormat)
       self.settings = Settings ("view.ini", QSettings.IniFormat)
       self.session = Settings ("edit.ini", QSettings.IniFormat)

       self.toolbar = self.addToolBar ("Main")
       self.status = self.statusBar ()

       self.generateCompletionList = None

       self.process_list = [ ]

       # center

       self.firstTabWidget = ViewTabWidget (self, self)
       self.firstTabWidget.setMovable (True)

       self.findBox = FindBox ()
       self.findBox.hide ()

       self.lineBox = GoToLineBox ()
       self.lineBox.hide ()

       self.secondTabWidget = ViewTabWidget (self, self)
       self.secondTabWidget.setMovable (True)
       self.secondTabWidget.hide ()

       # left

       self.leftTabs = ToolTabWidget ()
       self.leftTabs.setMovable (True)
       self.leftTabs.setTabPosition (QTabWidget.West)

       self.project = Tree (self)
       self.leftTabs.addTab (self.project, "Project")

       self.classes = Tree (self)
       self.leftTabs.addTab (self.classes, "Classes")

       self.tree = Tree (self)
       self.leftTabs.addTab (self.tree, "Tree")

       self.navigator = Navigator (self, self.leftTabs)
       self.leftTabs.addTab (self.navigator, "Navigator")

       self.files = TreeDir (self)
       self.leftTabs.addTab (self.files, "Files")

       self.grep = GrepWin (self)
       self.leftTabs.addTab (self.grep, "Grep")

       self.documents = Documents (self, self.leftTabs, self.firstTabWidget)
       self.leftTabs.addTab (self.documents, "Documents")

       self.bookmarks = Bookmarks (self, self.leftTabs, self.firstTabWidget)
       self.leftTabs.addTab (self.bookmarks, "Bookmarks")

       self.structure = Structure (self, self.leftTabs)
       inx = self.leftTabs.addTab (self.structure, "Structure")
       self.leftTabs.setTabToolTip (inx, "Text Structure")
       self.leftTabs.setTabWhatsThis (inx, "Text Structure")

       # right

       self.rightTabs = ToolTabWidget ()
       self.rightTabs.setMovable (True)
       self.rightTabs.setTabPosition (QTabWidget.East)

       self.prop = Property (self)
       self.rightTabs.addTab (self.prop, "Properties")

       self.memo = Memo (self, self.rightTabs)
       self.rightTabs.addTab (self.memo, "Memo")

       self.references = References (self, self.rightTabs)
       self.rightTabs.addTab (self.references, "References")

       # bottom

       # self.info = Info (self)
       self.info = InfoWithTools (self)

       # layout

       self.esplitter = QSplitter ()
       self.esplitter.setOrientation (Qt.Horizontal)
       self.esplitter.addWidget (self.firstTabWidget)
       self.esplitter.addWidget (self.secondTabWidget)
       self.esplitter.setStretchFactor (1, 1)

       self.esplitter.setSizePolicy (QSizePolicy.Preferred, QSizePolicy.Expanding)
       self.findBox.setSizePolicy   (QSizePolicy.Preferred, QSizePolicy.Fixed)
       self.lineBox.setSizePolicy   (QSizePolicy.Preferred, QSizePolicy.Fixed)

       self.vlayout = QVBoxLayout ()
       self.vlayout.addWidget (self.esplitter)
       self.vlayout.addWidget (self.findBox)
       self.vlayout.addWidget (self.lineBox)

       self.middle = QWidget ()
       self.middle.setLayout (self.vlayout)

       self.hsplitter = QSplitter ()
       self.hsplitter.addWidget (self.leftTabs)
       self.hsplitter.addWidget (self.middle)
       self.hsplitter.addWidget (self.rightTabs)
       self.hsplitter.setStretchFactor (0, 1)
       self.hsplitter.setStretchFactor (1, 4)
       self.hsplitter.setStretchFactor (2, 1)

       self.vsplitter = QSplitter ()
       self.vsplitter.setOrientation (Qt.Vertical)
       self.vsplitter.addWidget (self.hsplitter)
       self.vsplitter.addWidget (self.info)
       self.vsplitter.setStretchFactor (0, 3)
       self.vsplitter.setStretchFactor (1, 1)

       self.setCentralWidget (self.vsplitter)

       # other windows

       self.other_win = DetailWindow (self)
       self.zoom_win = DetailWindow (self)

       self.other_win.setWindowTitle ("Other")
       self.zoom_win.setWindowTitle ("Zoom")

       self.left_win = QMainWindow (self)
       self.right_win = QMainWindow (self)
       self.bottom_win = QMainWindow (self)

       self.left_win.setWindowTitle ("Tree")
       self.right_win.setWindowTitle ("Properties")
       self.bottom_win.setWindowTitle ("Output")

       self.window_list = [ self, self.other_win, self.zoom_win,
                            self.left_win, self.right_win, self.bottom_win ]

       self.active_tab_widget = self.firstTabWidget
       self.alternate_tab_widget = self.secondTabWidget

       self.alternate_win_id = None

       self.alt_map = None

       # file menu

       self.fileMenu = self.menuBar().addMenu ("&File")
       self.fileMenu.aboutToShow.connect (self.onShowFileMenu)
       menu = self.fileMenu

       act = QAction ("&Open...", self)
       act.setShortcut ("Ctrl+O")
       act.setIcon (findIcon ("document-open"))
       act.triggered.connect (self.openFile)
       menu.addAction (act)

       act = QAction ("&Save", self)
       act.setShortcut ("Ctrl+S")
       act.setIcon (findIcon ("document-save"))
       act.triggered.connect (self.saveFile)
       act.need_editor = True
       menu.addAction (act)

       act = QAction ("Save As...", self)
       act.setIcon (findIcon ("document-save-as"))
       act.triggered.connect (self.saveFileAs)
       act.need_editor = True
       menu.addAction (act)

       act = QAction ("&Close", self)
       act.setShortcut ("Ctrl+W")
       act.setIcon (findIcon ("window-close"))
       act.triggered.connect (self.closeFile)
       act.need_editor = True
       menu.addAction (act)

       menu.addSeparator ()

       act = QAction ("&Quit", self)
       act.setShortcut ("Ctrl+Q")
       act.setShortcutContext (Qt.ApplicationShortcut)
       act.setIcon (findIcon ("application-exit"))
       act.triggered.connect (self.quit)
       menu.addAction (act)

       # edit menu

       self.editMenu = self.menuBar().addMenu ("&Edit")
       self.editMenu.aboutToShow.connect (self.onShowEditMenu)
       menu = self.editMenu

       act = QAction ("&Indent", self)
       act.setShortcut ("Ctrl+I")
       act.setIcon (findIcon ("format-indent-more"))
       act.setStatusTip ("Indent the current line or selection")
       act.triggered.connect (self.indent)
       menu.addAction (act)

       act = QAction ("&Unindent", self)
       act.setShortcut ("Ctrl+U")
       act.setIcon (findIcon ("format-indent-less"))
       act.setStatusTip ("Unindent the current line or selection")
       act.triggered.connect (self.unindent)
       menu.addAction (act)

       menu.addSeparator ()

       act = QAction ("Comment", self)
       act.setShortcut ("Ctrl+D")
       act.triggered.connect (self.comment)
       menu.addAction (act)

       act = QAction ("Uncomment", self)
       act.setShortcut ("Ctrl+E")
       act.triggered.connect (self.uncomment)
       menu.addAction (act)

       menu.addSeparator ()

       act = QAction ("&Find", self)
       act.setShortcut ("Ctrl+F")
       act.setIcon (findIcon ("edit-find"))
       act.triggered.connect (self.findText)
       menu.addAction (act)

       act = QAction ("&Replace", self)
       act.setShortcut ("Ctrl+R")
       act.setIcon (findIcon ("edit-find-replace"))
       act.triggered.connect (self.replaceText)
       menu.addAction (act)

       act = QAction ("Find &Next", self)
       act.setShortcut ("F3")
       act.setIcon (findIcon ("go-next"))
       act.triggered.connect (self.findNext)
       menu.addAction (act)

       act = QAction ("Find &Previous", self)
       act.setShortcut ("Shift+F3")
       act.setIcon (findIcon ("go-previous"))
       act.triggered.connect (self.findPrev)
       menu.addAction (act)

       menu.addSeparator ()

       act = QAction ("&Go to Line", self)
       act.setShortcut ("Ctrl+G")
       act.setIcon (findIcon ("go-jump"))
       act.triggered.connect (self.goToLine)
       menu.addAction (act)

       act = QAction ("Find Selected", self)
       act.setShortcut ("Ctrl+H")
       act.triggered.connect (self.findSelected)
       menu.addAction (act)

       act = QAction ("Find Incremental", self)
       act.setShortcut ("Ctrl+J")
       act.triggered.connect (self.findIncremental)
       menu.addAction (act)

       menu.addSeparator ()

       act = QAction ("Set &Bookmark", self)
       act.setShortcut ("Ctrl+B")
       act.setIcon (findIcon ("bookmark-new"))
       act.triggered.connect (lambda: self.setBookmark (1))
       menu.addAction (act)

       act = QAction ("Clear Bookmarks", self)
       act.setIcon (findIcon ("bookmark-remove"))
       act.setStatusTip ("Remove all bookmarks of the current document")
       act.triggered.connect (self.clearBookmarks)
       menu.addAction (act)

       menu.addSeparator ()

       act = QAction ("Move Lines Up", self)
       act.setShortcut ("Ctrl+Shift+Up")
       act.setIcon (findIcon ("go-up"))
       act.triggered.connect (self.moveLinesUp)
       act.need_editor = True
       menu.addAction (act)

       act = QAction ("Move Lines Down", self)
       act.setShortcut ("Ctrl+Shift+Down")
       act.setIcon (findIcon ("go-down"))
       act.triggered.connect (self.moveLinesDown)
       act.need_editor = True
       menu.addAction (act)

       # view menu

       self.viewMenu = self.menuBar().addMenu ("&View")
       self.viewMenu.aboutToShow.connect (self.onShowViewMenu)
       menu = self.viewMenu

       act = QAction ("Enlarge Font", self)
       act.setShortcut ("Ctrl+=")
       act.setIcon (findIcon ("zoom-in"))
       act.triggered.connect (self.enlargeFont)
       act.need_editor = True
       menu.addAction (act)

       act = QAction ("Shrink Font", self)
       act.setShortcut ("Ctrl+-")
       act.setIcon (findIcon ("zoom-out"))
       act.triggered.connect (self.shrinkFont)
       act.need_editor = True
       menu.addAction (act)

       menu.addSeparator ()

       act = QAction ("Previous Function", self)
       act.setShortcut ("Alt+Up")
       act.setIcon (findIcon ("go-up-search"))
       act.triggered.connect (self.gotoPrevFunction)
       act.need_editor = True
       menu.addAction (act)

       act = QAction ("Next Function", self)
       act.setShortcut ("Alt+Down")
       act.setIcon (findIcon ("go-down-search"))
       act.triggered.connect (self.gotoNextFunction)
       act.need_editor = True
       menu.addAction (act)

       menu.addSeparator ()

       act = QAction ("Previous Bookmark", self)
       act.setShortcut ("Alt+PgUp")
       act.setIcon (findIcon ("arrow-up"))
       act.triggered.connect (self.gotoPrevBookmark)
       act.need_editor = True
       menu.addAction (act)

       act = QAction ("Next Bookmark", self)
       act.setShortcut ("Alt+PgDown")
       act.setIcon (findIcon ("arrow-down"))
       act.triggered.connect (self.gotoNextBookmark)
       act.need_editor = True
       menu.addAction (act)

       menu.addSeparator ()

       act = QAction ("Next output mark", self)
       act.setShortcut ("F4")
       act.setIcon (findIcon ("go-up"))
       act.setStatusTip ("Jump to next output mark")
       act.triggered.connect (self.info.jumpToNextMark)
       menu.addAction (act)

       act = QAction ("Previous output mark", self)
       act.setShortcut ("Shift+F4")
       act.setIcon (findIcon ("go-down"))
       act.setStatusTip ("Jump to previous output mark")
       act.triggered.connect (self.info.jumpToPrevMark)
       menu.addAction (act)

       act = QAction ("Last output mark", self)
       act.setShortcut ("Ctrl+F4")
       act.setIcon (findIcon ("go-last"))
       act.setStatusTip ("Jump to last output mark")
       act.triggered.connect (self.info.jumpToLastMark)
       menu.addAction (act)

   def additionalMenuItems (self) :

       # window menu

       self.windowMenu = self.menuBar().addMenu ("&Window")
       self.windowMenu.aboutToShow.connect (self.onShowWindowMenu)
       menu = self.windowMenu

       self.globalAction (menu, "Split view left/right", self.splitViewRight,  "Ctrl+;")
       self.globalAction (menu, "Split view top/bottom", self.splitViewBottom, "Ctrl+'")

       menu.addSeparator ()

       self.localAction (menu, "Move to left/top view",     self.moveEditorLeft,  "Ctrl+[")
       self.localAction (menu, "Move to right/bottom view", self.moveEditorRight, "Ctrl+]")

       menu.addSeparator ()

       self.leftAction   = self.showSideAction (menu, "Left",   self.leftTabs,  "Ctrl+,")
       self.rightAction  = self.showSideAction (menu, "Right",  self.rightTabs, "Ctrl+.")
       self.bottomAction = self.showSideAction (menu, "Bottom", self.info,      "Ctrl+/")

       menu.addSeparator ()

       self.floatingAction (menu, "Floating &left window", "Meta+,", self.floatingLeft)
       self.floatingAction (menu, "Floating &right window", "Meta+.", self.floatingRight)
       self.floatingAction (menu, "Floating &bottom window", "Meta+/", self.floatingBottom)

       menu.addSeparator ()

       self.globalAction (menu, "Left window",  self.selectLeftWindow,  "Meta+Left")
       self.globalAction (menu, "Right window", self.selectRightWindow, "Meta+Right")
       self.globalAction (menu, "Above window", self.selectAboveWindow, "Meta+Up")
       self.globalAction (menu, "Below window", self.selectBelowWindow, "Meta+Down")

       # tabs menu

       self.tabsMenu = self.menuBar().addMenu ("T&abs")
       menu = self.tabsMenu

       self.showSideTabAction (menu, "Project",    self.leftTabs, self.project,   "Meta+P", "project-development")
       self.showSideTabAction (menu, "Classes",    self.leftTabs, self.classes,   "Meta+C", "code-class")
       self.showSideTabAction (menu, "Tree",       self.leftTabs, self.tree,      "Meta+T", "view-list-tree")
       self.showSideTabAction (menu, "Navigator",  self.leftTabs, self.navigator, "Meta+N", "view-form-table")
       self.showSideTabAction (menu, "Files",      self.leftTabs, self.files,     "Meta+F", "system-file-manager")
       self.showSideTabAction (menu, "Grep",       self.leftTabs, self.grep,      "Meta+G", "system-search")
       self.showSideTabAction (menu, "Documents",  self.leftTabs, self.documents, "Meta+D", "document-multiple")
       self.showSideTabAction (menu, "Bookmarks",  self.leftTabs, self.bookmarks, "Meta+B", "bookmarks")
       self.showSideTabAction (menu, "Structure",  self.leftTabs, self.structure, "Meta+S", "edit-copy")

       menu.addSeparator ()

       self.globalAction (menu, "Edit",   self.showEditor, "Meta+E", "document-edit")
       self.globalAction (menu, "Output", self.showOutput, "Meta+O", "view-close")

       menu.addSeparator ()

       self.showSideTabAction (menu, "Properties", self.rightTabs, self.prop,       "Meta+L", "document-properties")
       self.showSideTabAction (menu, "Memo",       self.rightTabs, self.memo,       "Meta+M", "help-about")
       self.showSideTabAction (menu, "References", self.rightTabs, self.references, "Meta+R", "documentation")

       menu.addSeparator ()

       act = self.globalAction (menu, "&Other window", self.showOther, "Meta+X")
       act.setStatusTip ("Open text in another window")
       self.otherAction = act

       act = self.globalAction (menu, "&Zoom window", self.showZoom, "Meta+Z")
       act.setStatusTip ("Open text in zoom window")
       self.zoomAction = act

       # jump menu

       self.jumpMenu = self.menuBar().addMenu ("&Jump")
       menu = self.jumpMenu

       """
       self.jumpAction (menu, "&Project",     "P", "project-development")
       self.jumpAction (menu, "&Class",       "C", "code-class")
       self.jumpAction (menu, "&Tree",        "T", "view-list-tree")
       self.jumpAction (menu, "&Navigator",   "N", "view-form-table")
       self.jumpAction (menu, "&Files",       "F", "system-file-manager")
       self.jumpAction (menu, "&Grep",        "G", "system-search")
       self.jumpAction (menu, "&Documents",   "D", "document-multiple")
       self.jumpAction (menu, "&Bookmarks",   "B", "bookmarks")
       self.jumpAction (menu, "&Structure",   "S", "edit-copy")
       menu.addSeparator ()
       """
       self.jumpAction (menu, "Add to &Memo",        "Alt+M", "help-about",    self.addToMemo)
       self.jumpAction (menu, "Add to &References",  "Alt+R", "documentation", self.addToReferences)
       menu.addSeparator ()
       self.jumpAction (menu, "Show in other window", "Alt+X", None,  self.showInOther)
       self.jumpAction (menu, "Show in zoom window",  "Alt+Z", None, self.showInZoom)
       """
       menu.addSeparator ()
       self.jumpAction (menu, "Grammar",      "6", "view-list-text")
       self.jumpAction (menu, "Tree",         "7", "view-list-tree")
       self.jumpAction (menu, "Source",       "8", "text-x-generic")
       self.jumpAction (menu, "C++ code",     "9", "text-x-c++src")
       self.jumpAction (menu, "Python code",  "0", "text-x-python")
       """

       # keyboard shortcuts

       for inx in range (10) :
           self.setTabShortcut (inx)

       self.addShortcut (self.setFirstTab, "Alt+Home")
       self.addShortcut (self.setLastTab,  "Alt+End")
       self.addShortcut (self.setPrevTab,  "Alt+Left")
       self.addShortcut (self.setNextTab,  "Alt+Right")

       self.addShortcut (self.moveTabLeft,   [ "Alt+,", "Alt+Shift+Left" ])
       self.addShortcut (self.moveTabRight,  [ "Alt+.", "Alt+Shift+Right" ])
       self.addShortcut (self.placeTabFirst, [ "Alt+[", "Alt+Shift+Home" ])
       self.addShortcut (self.placeTabLast,  [ "Alt+]", "Alt+Shift+End" ])

       self.addShortcut (self.leftToolUp,    "Meta+Home")
       self.addShortcut (self.leftToolDown,  "Meta+End")
       self.addShortcut (self.rightToolUp,   "Meta+PgUp")
       self.addShortcut (self.rightToolDown, "Meta+PgDown")


   # Jump menu

   def jumpAction (self, menu, title, key = None, icon = None, func = None) :
       shortcut = key
       if key != None and len(key) == 1 :
          if key >= "0" and key <= "9" :
             shortcut = "Meta+" + key # Win
          elif key >= "A" and key <= "Z" :
             shortcut = "Meta+Ctrl+" + key

       act = QAction (title, self)
       if shortcut != None :
          self.addShortcuts (act, shortcut)
       if icon != None :
          act.setIcon (findIcon (icon))
       if func != None :
          act.triggered.connect (func)
       menu.addAction (act)
       return act

   # Window menu

   def onShowWindowMenu (self) :
       self.leftAction.setChecked  (self.leftTabs.isVisible ())
       self.rightAction.setChecked (self.rightTabs.isVisible ())
       self.bottomAction.setChecked  (self.info.isVisible ())

       is_edit = self.getEditor() != None
       self.otherAction.setEnabled (is_edit)
       self.zoomAction.setEnabled (is_edit)

   def addShortcuts (self, action, shortcut) :
       if shortcut != None and shortcut != "" :
          if isinstance (shortcut, list) :
             action.setShortcuts (shortcut)
          else :
             action.setShortcut (shortcut)

   def globalAction (self, menu, text, func, shortcut = "", icon = None) :
       act = QAction (text, self)
       self.addShortcuts (act, shortcut)
       act.setShortcutContext (Qt.ApplicationShortcut)
       if icon != None :
          act.setIcon (findIcon (icon))
       act.triggered.connect (func)
       menu.addAction (act)
       return act

   def localAction (self, menu, text, func, shortcut = "") :
       act = QAction (text, self)
       self.addShortcuts (act, shortcut)
       act.triggered.connect (func)
       menu.addAction (act)
       return act

   # toggle (show/hide) widget

   def toggleWidgetAction (self, menu, text, widget, shortcut) :
       act = QAction (text, self)
       self.addShortcuts (act, shortcut)
       act.setShortcutContext (Qt.ApplicationShortcut)
       act.triggered.connect (lambda: self.toggleWidget (widget))
       menu.addAction (act)
       return act

   def toggleWidget (self, widget) :
       widget.setVisible (not widget.isVisible ())

   # show output

   def showOutput (self) :
       "set focus and activate"
       widget = self.info
       widget.setFocus ()
       self.activateWindow ()

   # show editor

   def showEditor (self) :
       "set focus to current tab and activate"
       widget = self.firstTabWidget.currentWidget ()
       widget.setFocus ()
       self.activateWindow ()

   # change side tab (tool tab)

   def changeSideTab (self, widget, delta) :
       if delta == -2 :
          widget.setCurrentIndex (0)
       elif delta == 2:
          widget.setCurrentIndex (widget.count() - 1)
       elif delta == -1 :
          inx = widget.currentIndex ()
          if inx == 0 :
             inx = widget.count ()
          else :
             inx = inx - 1
          widget.setCurrentIndex (inx)
       elif delta == 1 :
          inx = widget.currentIndex ()
          inx = inx + 1
          if inx > widget.count () :
             inx = 0
          widget.setCurrentIndex (inx)

   def leftToolUp (self) :
       self.changeSideTab (self.leftTabs, -1)

   def leftToolDown (self) :
       self.changeSideTab (self.leftTabs, 1)

   def leftToolHome (self) :
       self.changeSideTab (self.leftTabs, -2)

   def leftToolEnd (self) :
       self.changeSideTab (self.leftTabs, 2)

   def rightToolUp (self) :
       self.changeSideTab (self.rightTabs, -1)

   def rightToolDown (self) :
       self.changeSideTab (self.rightTabs, 1)

   # show one tab (in side panel)

   def showSideTabAction (self, menu, text, sideTabs, widget, shortcut = None, icon = None) :
       act = QAction (text, self)
       if shortcut != None and shortcut != "":
          self.addShortcuts (act, shortcut)
          act.setShortcutContext (Qt.ApplicationShortcut)
       if icon != None :
          icon = findIcon (icon)
          act.setIcon (icon)
          if not use_simple :
             inx = sideTabs.indexOf (widget)
             if inx >= 0 :
                sideTabs.setTabIcon (inx, icon)
       act.triggered.connect (lambda: self.showSideTab (sideTabs, widget))
       menu.addAction (act)
       return act

   def showSideTab (self, sideTabs, widget) :
       sideTabs.setVisible (True)
       sideTabs.setCurrentWidget (widget)
       widget.setFocus ()

   def showTab (self, widget) :
       sideTabs = widget.parentWidget ()
       sideTabs.setVisible (True)
       sideTabs.setCurrentWidget (widget)
       widget.setFocus ()

   # show side panel

   def showSideAction (self, menu, text, widget, shortcut) :
       act = QAction (text, self)
       act.setCheckable (True)
       act.setChecked (True)
       self.addShortcuts (act, shortcut)
       act.setShortcutContext (Qt.ApplicationShortcut)
       act.triggered.connect (lambda: self.showSide (widget))
       menu.addAction (act)
       return act

   def showSide (self, widget) :
       w = widget.parent()
       if w != self and isinstance (w, QMainWindow):
          w.setVisible (not w.isVisible ())
          widget.setVisible (True)
       else :
          widget.setVisible (not widget.isVisible())

   # floating side panels

   def floatingAction (self, menu, text, shortcut, func) :
       act = QAction (text, self)
       act.setCheckable (True)
       self.addShortcuts (act, shortcut)
       act.setShortcutContext (Qt.ApplicationShortcut)
       act.toggled.connect (func)
       menu.addAction (act)

   def floatingLeft (self, checked) :
       if checked :
          self.left_win.setCentralWidget (self.leftTabs)
          self.left_win.setVisible (True)
       else :
          self.left_win.setVisible (False)
          self.hsplitter.insertWidget (0, self.leftTabs)
       self.leftTabs.setVisible (True)

   def floatingRight (self, checked) :
       if checked :
          self.right_win.setCentralWidget (self.rightTabs)
          self.right_win.setVisible (True)
       else :
          self.right_win.setVisible (False)
          self.hsplitter.addWidget (self.rightTabs)
       self.rightTabs.setVisible (True)

   def floatingBottom (self, checked) :
       if checked :
          self.bottom_win.setCentralWidget (self.info)
          self.bottom_win.setVisible (True)
       else :
          self.bottom_win.setVisible (False)
          self.vsplitter.addWidget (self.info)
       self.info.setVisible (True)

   # detail windows

   def showOther (self) :
       if self.other_win.tabWidget.count () == 0 :
          self.showInOther ()
       self.other_win.show ()
       # self.other_win.setFocus ()
       self.other_win.activateWindow ()

   def showZoom (self) :
       if self.zoom_win.tabWidget.count () == 0 :
          self.showInZoom ()
       self.zoom_win.show ()
       # self.zoom_win.setFocus ()
       self.zoom_win.activateWindow ()

   def showInOther (self) :
       editor = self.getEditor ()
       if editor != None :
          fileName = editor.getFileName ()
          e = self.other_win.addItem (fileName)
          e.setDocument (editor.document ())
       if not self.other_win.isVisible() :
          self.other_win.show ()

   def showInZoom (self) :
       editor = self.getEditor ()
       if editor != None :
          fileName = editor.getFileName ()
          e = self.zoom_win.addItem (fileName)
          e.setReadOnly (True)

          document = editor.document ().clone()

          # QPlainTextEdit - change document layout
          layout = QPlainTextDocumentLayout (document)
          document.setDocumentLayout (layout)

          e.setDocument (document)

          setZoomFont (e)
          e.setLineWrapMode (QPlainTextEdit.NoWrap)
       if not self.zoom_win.isVisible() :
          self.zoom_win.show ()

   # top level windows

   def selectWindow (self, compare)  :
       done = False
       if QApplication.activeWindow () == self :
          done = self.selectLocalWindow (compare)
       if not done :
          self.selectTopLevelWindow (compare)

   def selectLocalWindow (self, compare)  :
       win_list = [ self.firstTabWidget,
                    self.secondTabWidget,
                    # self.leftTabs,
                    # self.rightTabs,
                    # self.info
                    ]

       win_list = [ w for w in win_list if w.isVisible () and w.parentWidget() != None ]
       sort_list (win_list, compare)

       focused = QApplication.focusWidget ()
       while focused != None and focused not in win_list :
          focused = focused.parentWidget ()
       # print ("focused", focused)
       # print ("win_list", win_list)

       answer = False
       if focused in win_list :
          inx = win_list.index (focused)
          if inx > 0 :
             inx = inx - 1
             widget = win_list [inx]
             if isinstance (widget, ViewTabWidget) :
                widget = widget.currentWidget ()
             widget.setFocus ()
             print ("select", widget)
             answer = True
       return answer

   def selectTopLevelWindow (self, compare)  :
       win_list = [ w for w in self.window_list if w.isVisible () ]
       sort_list (win_list, compare)

       active = QApplication.activeWindow ()
       # print ("SELECT WINDOW")
       # for w in win_list :
       #     print ("WINDOW", w.windowTitle(), w.__class__, w.x (), w.y (), w == active)

       target = None
       cnt = len (win_list)
       inx = -1
       if active in win_list :
          inx = win_list.index (active)

       if cnt > 0 and inx >= 0 :
          if inx > 0 :
             target = win_list [inx-1]
          else :
             target = win_list [-1]

       if target != None and target != active :
          target.activateWindow ()

   def selectLeftWindow (self) :
       self.selectWindow (lambda a, b : cmp (a.x (), b.x ()))

   def selectRightWindow (self) :
       self.selectWindow (lambda a, b : cmp (b.x (), a.x ()))

   def selectAboveWindow (self) :
       self.selectWindow (lambda a, b : cmp (a.y (), b.y ()))

   def selectBelowWindow (self) :
       self.selectWindow (lambda a, b : cmp (b.y (), a.y ()))

   # split view, move editor between tab widgets

   def splitViewRight (self) :
       if self.esplitter.orientation () == Qt.Horizontal and self.secondTabWidget.isVisible() :
          self.secondTabWidget.hide ()
       else :
          self.esplitter.setOrientation (Qt.Horizontal)
          self.secondTabWidget.show ()

   def splitViewBottom (self) :
       if self.esplitter.orientation () == Qt.Vertical and self.secondTabWidget.isVisible() :
          self.secondTabWidget.hide ()
       else :
          self.esplitter.setOrientation (Qt.Vertical)
          self.secondTabWidget.show ()

   def moveEditor (self, source, target) :
       inx = source.currentIndex ()
       if inx >= 0 :
          text = source.tabText (inx)
          widget = source.widget (inx)
          source.removeTab (inx)
          inx = target.addTab (widget, text)
          target.setCurrentIndex (inx)
          if not target.isVisible() :
             target.show ()
          widget.setFocus ()

   def moveEditorLeft (self) :
       self.moveEditor (self.secondTabWidget, self.firstTabWidget)

   def moveEditorRight (self) :
       self.moveEditor (self.firstTabWidget, self.secondTabWidget)

   # show editor tabs

   def getTabWidget (self) :
       widget = None
       active = QApplication.activeWindow ()
       if active == self.zoom_win :
          widget = self.zoom_win.tabWidget
       elif active == self.other_win :
          widget = self.other_win.tabWidget
       else :
          widget = self.firstTabWidget
       return widget

   def setTabShortcut (self, inx) :
       act = QShortcut (self)
       act.setObjectName ("Tab " + str (inx))
       act.setKey ("Alt+" + str (inx))
       act.setContext (Qt.ApplicationShortcut)
       act.activated.connect (lambda: self.setTab (inx))

   def setTab (self, inx, tabWidget = None, passive = False) :
       # print ("TAB", inx)
       if tabWidget == None :
          tabWidget = self.getTabWidget ()
       cnt = tabWidget.count ()
       if inx == 0 :
          inx = cnt # 0 ... last tabs
       if inx >= 1 and inx <= cnt :
          tabWidget.setCurrentIndex (inx-1)
          if not passive :
             tabWidget.currentWidget ().setFocus ()

   def addShortcut (self, func, shortcut) :
       if isinstance (shortcut, list) :
          for s in shortcut :
              self.addShortcut (func, s)
       else :
          act = QShortcut (self)
          act.setObjectName (func.__name__)
          act.setKey (shortcut)
          act.setContext (Qt.ApplicationShortcut)
          act.activated.connect (func)

   def setFirstTab (self, tabWidget = None, passive = False) :
       if tabWidget == None :
          tabWidget = self.getTabWidget ()
       self.setTab (1, tabWidget, passive)

   def setLastTab (self, tabWidget = None, passive = False) :
       if tabWidget == None :
          tabWidget = self.getTabWidget ()
       cnt = tabWidget.count ()
       self.setTab (cnt, tabWidget, passive)

   def setPrevTab (self, tabWidget = None, passive = False) :
       if tabWidget == None :
          tabWidget = self.getTabWidget ()
       inx = tabWidget.currentIndex () + 1
       cnt = tabWidget.count ()
       if inx > 1 :
          inx = inx - 1
       else :
          inx = cnt
       self.setTab (inx, tabWidget, passive)

   def setNextTab (self, tabWidget = None, passive = False) :
       if tabWidget == None :
          tabWidget = self.getTabWidget ()
       inx = tabWidget.currentIndex () + 1
       cnt = tabWidget.count ()
       if inx < cnt :
          inx = inx + 1
       else :
          inx = 1
       self.setTab (inx, tabWidget, passive)

   # move editor tabs

   def placeTab (self, new_inx) :
       tabWidget = self.getTabWidget ()
       inx = tabWidget.currentIndex ()

       text = tabWidget.tabText (inx)
       tooltip = tabWidget.tabToolTip (inx)
       widget = tabWidget.widget (inx)

       tabWidget.removeTab (inx)

       tabWidget.insertTab (new_inx, widget, text)
       tabWidget.setTabToolTip (new_inx, tooltip)

       tabWidget.setCurrentIndex (new_inx)

   def moveTabLeft (self) :
       tabWidget = self.getTabWidget ()
       inx = tabWidget.currentIndex ()
       cnt = tabWidget.count ()
       if inx > 0 :
          self.placeTab (inx - 1)

   def moveTabRight (self) :
       tabWidget = self.getTabWidget ()
       inx = tabWidget.currentIndex ()
       cnt = tabWidget.count ()
       if inx < cnt - 1 :
          self.placeTab (inx + 1)

   def placeTabFirst (self) :
       tabWidget = self.getTabWidget ()
       inx = tabWidget.currentIndex ()
       cnt = tabWidget.count ()
       if inx > 0 :
          self.placeTab (0)

   def placeTabLast (self) :
       tabWidget = self.getTabWidget ()
       inx = tabWidget.currentIndex ()
       cnt = tabWidget.count ()
       if inx < cnt - 1 :
          self.placeTab (cnt - 1)

   # Files

   def newEditor (self, fileName) :
       editor = Editor ()
       editor.win = self
       editor.tabWidget = self.firstTabWidget
       editor.findBox = self.findBox
       editor.lineBox = self.lineBox

       self.editors [fileName] = editor
       name = os.path.basename (fileName)

       inx = self.firstTabWidget.addTab (editor, name)
       self.firstTabWidget.setTabToolTip (inx, fileName)
       return editor

   def loadFile (self, fileName, line = 0, column = 0, refreshFile = False, reloadFile = False, rewriteFile = False) :
       fileName = qstring_to_str (fileName)
       # print ("LOAD FILE", fileName)
       if not rewriteFile and (fileName == "" or not os.path.isfile (fileName)) :
          # raise  IOError ("bad file name: " + fileName)
          return None
       else :
          fileName = os.path.abspath (fileName)
          if fileName in self.editors :
             editor = self.editors [fileName]
             if refreshFile :
                self.checkModifiedOnDisk (editor)
             if reloadFile :
                editor.readFile (fileName)
             if rewriteFile :
                editor.setPlainText ("")
                editor.writeFile (fileName)
          else :
             editor = self.newEditor (fileName)
             if rewriteFile :
                editor.writeFile (fileName)
             else :
                editor.readFile (fileName)
          self.firstTabWidget.setCurrentWidget (editor)
          if line != None and line != 0 :
             editor.selectLine (line)
          editor.setFocus ()
          return editor

   def refreshFile (self, fileName) :
       "check if data on disk are newer"
       return self.loadFile (fileName, refreshFile = True)

   def reloadFile (self, fileName) :
       "read data from disk"
       return self.loadFile (fileName, reloadFile = True)

   def rewriteFile (self, fileName) :
       "create empty file"
       return self.loadFile (fileName, rewriteFile = True)

   # File menu

   def onShowFileMenu (self) :
       is_edit = self.getEditor() != None
       for act in self.fileMenu.actions () :
           if hasattr (act, "need_editor") :
              act.setEnabled (is_edit)

   def openFile (self) :
       fileName = QFileDialog.getOpenFileName (self, "Open File")
       fileName = dialog_to_str (fileName)
       if fileName != "" :
          self.loadFile (fileName)

   def saveFile (self) :
       editor = self.getEditor ()
       if editor != None :
          # editor.saveFile ()
          editor.writeFile (editor.getFileName ())

   def saveFileAs (self) :
       editor = self.getEditor ()
       if editor != None :
          # editor.saveFileAs ()
          oldFileName = editor.getFileName ()
          fileName = QFileDialog.getSaveFileName (self, "Save File As", editor.getFileName ())
          fileName = dialog_to_str (fileName)
          if fileName != "" :
             del self.editors [editor.getFileName ()]
             editor.writeFile (fileName)
             # after writeFile, getFileName is updated
             self.editors [editor.getFileName ()] = editor
             # set tab title
             fileName = editor.getFileName ()
             name = os.path.basename (fileName)
             tab = editor.parent()
             while tab != None and not isinstance (tab, QTabWidget) :
                tab = tab.parent ()
             if isinstance (tab, QTabWidget) :
                inx = tab.indexOf (editor)
                tab.setTabText (inx, name)
                tab.setTabToolTip (inx, fileName)
                tab.setCurrentIndex (inx)


       inx = self.firstTabWidget.addTab (editor, name)
       self.firstTabWidget.setTabToolTip (inx, fileName)

   def closeFile (self) :
       editor = self.getEditor ()
       if editor != None :
          if self.checkSave (editor) :
             del self.editors [editor.getFileName ()]
             inx = self.firstTabWidget.indexOf (editor)
             if inx >= 0 :
                self.firstTabWidget.removeTab (inx)

   def checkSave (self, editor) :
       if not editor.isModified () or editor.closeWithoutQuestion :
          return True
       else :
          dialog = QMessageBox (self)
          dialog.setIcon (QMessageBox.Warning)
          dialog.setText ("The " + editor.getFileName () + " has been modified")
          dialog.setInformativeText ("Do you want to save your changes ?")
          dialog.setStandardButtons (QMessageBox.Save | QMessageBox.Cancel | QMessageBox.Discard)
          dialog.setDefaultButton (QMessageBox.Save)
          answer = dialog.exec_ ()
          if answer == QMessageBox.Save :
             editor.writeFile (editor.getFileName ())
             return True
          elif answer == QMessageBox.Discard :
             return True
          else :
             return False

   def checkModifiedOnDisk (self, editor) :
       if editor.isModified () or editor.isModifiedOnDisk () :
          dialog = QMessageBox (self)
          dialog.setIcon (QMessageBox.Warning)
          dialog.setText ("The " + editor.getFileName () + " has been modified")
          dialog.setInformativeText ("Do you want to save your changes or discard them ?")
          dialog.setStandardButtons (QMessageBox.Save | QMessageBox.Discard)
          dialog.setDefaultButton (QMessageBox.Save)
          answer = dialog.exec_ ()
          if answer == QMessageBox.Save :
             editor.writeFile (editor.getFileName ())
          elif answer == QMessageBox.Discard :
             editor.readFile (editor.getFileName ())
          else :
             pass
       elif editor.isDifferentOnDisk () :
          editor.readFile (editor.getFileName ())

   def closeEvent (self, e) :
       for key in self.editors :
           editor = self.editors [key]
           if not self.checkSave (editor) :
              e.ignore ()
              return
       self.storeSession ()
       for w in self.window_list :
           if w != self:
              w.close ()
       for item in self.process_list :
           item.terminate ()
       e.accept ()

   def quit (self) :
       QApplication.instance().quit()

   # Edit menu

   def onShowEditMenu (self) :
       is_edit = self.getEditor() != None
       for act in self.editMenu.actions () :
          act.setEnabled (is_edit)

   def indent (self) :
       e = self.getEditor ()
       if e != None :
          e.indent ()

   def unindent (self) :
       e = self.getEditor ()
       if e != None :
          e.unindent ()

   def comment (self) :
       e = self.getEditor ()
       if e != None :
          e.comment ()

   def uncomment (self) :
       e = self.getEditor ()
       if e != None :
          e.uncomment ()

   def findText (self) :
       e = self.getEditor ()
       if e != None :
          e.findText ()

   def findNext (self) :
       e = self.getEditor ()
       if e != None :
          e.findNext ()

   def findPrev (self) :
       e = self.getEditor ()
       if e != None :
          e.findPrev ()

   def replaceText (self) :
       e = self.getEditor ()
       if e != None :
          e.replaceText ()

   def findSelected (self) :
       e = self.getEditor ()
       if e != None :
          e.findSelected ()

   def findIncremental (self) :
       e = self.getEditor ()
       if e != None :
          e.findIncremental ()

   def goToLine (self) :
       e = self.getEditor ()
       if e != None :
          e.goToLine ()

   def setBookmark (self, markType = 1) :
       e = self.getEditor ()
       if e != None :
          e.setBookmark (markType)

   def clearBookmarks (self) :
       e = self.getEditor ()
       if e != None :
          e.clearBookmarks ()

   def moveLinesUp (self) :
       e = self.getEditor ()
       if e != None :
          e.moveLinesUp ()

   def moveLinesDown (self) :
       e = self.getEditor ()
       if e != None :
          e.moveLinesDown ()

   # View menu

   def onShowViewMenu (self) :
       is_edit = self.getEditor() != None
       for act in self.viewMenu.actions () :
           if hasattr (act, "need_editor") :
              act.setEnabled (is_edit)

   def gotoPrevFunction (self) :
       e = self.getEditor ()
       if e != None :
          e.gotoPrevFunction ()

   def gotoNextFunction (self) :
       e = self.getEditor ()
       if e != None :
          e.gotoNextFunction ()

   def gotoPrevBookmark (self) :
       e = self.getEditor ()
       if e != None :
          e.gotoPrevBookmark ()

   def gotoNextBookmark (self) :
       e = self.getEditor ()
       if e != None :
          e.gotoNextBookmark ()

   def addToMemo (self) :
       e = self.getEditor ()
       if e != None :
          e.showMemo ()

   def addToReferences (self) :
       e = self.getEditor ()
       if e != None :
          e.showReferences ()

   def enlargeFont (self) :
       e = self.getEditor ()
       if e != None :
          e.enlargeFont ()

   def shrinkFont (self) :
       e = self.getEditor ()
       if e != None :
          e.shrinkFont ()

   def showOutputStructure (self) :
       self.leftTabs.setCurrentWidget (self.structure)
       self.structure.clear ()
       self.structure.showTextDocument (self.info)

   # Store session

   def storeSession (self) :
       self.session.clear ()
       inx = 0
       for key in self.editors :
           editor = self.editors [key]
           inx = inx + 1
           self.session.beginGroup ("edit-" + str (inx))
           self.session.remove ("")
           self.session.setValue ("fileName", editor.getFileName ())
           cursor = editor.textCursor ()
           self.session.setValue ("line", cursor.blockNumber () + 1)
           self.session.setValue ("column", columnNumber (cursor) + 1)

           bookmarks = editor.getBookmarks ()
           self.session.beginWriteArray ("bookmarks")
           n = 0
           for item in bookmarks :
               self.session.setArrayIndex (n)
               self.session.setValue ("line", item.line)
               self.session.setValue ("column", item.column)
               self.session.setValue ("mark", item.mark)
               n = n + 1
           self.session.endArray ()
           self.session.endGroup ()

   def reloadSession (self) :
       groups = self.session.childGroups ()
       for group in groups :
           group_name = str (group)
           if group_name.startswith ("edit") :
              self.session.beginGroup (group_name)
              fileName = self.session.value ("fileName", "", str)
              line = self.session.value ("line", 0, int)
              column = self.session.value ("column", 0, int)
              editor = self.loadFile (fileName) # , line, column)

              bookmarks = [ ]
              count = self.session.beginReadArray ("bookmarks")
              for inx in range (count) :
                  self.session.setArrayIndex (inx)
                  answer = Bookmark ()
                  answer.line = self.session.value ("line", 0, int)
                  answer.column = self.session.value ("column", 0, int)
                  answer.mark =  self.session.value ("mark", 0, int)
                  bookmarks.append (answer)
              self.session.endArray ()
              self.session.endGroup ()
              editor.setBookmarks (bookmarks)

   # Editors

   def getCurrentTab (self) :
       return self.active_tab_widget.currentWidget ()

   def getEditor (self) :
       e = self.active_tab_widget.currentWidget ()
       if isinstance (e, Editor) :
          return e
       else :
          return None

   def hasExtension (self, editor, extension) :
       if editor == None :
          return False
       else :
          name, ext = os.path.splitext (editor.getFileName ())
          return ext == extension

   # Status Bar

   def showStatus (self, text) :
       self.status.showMessage (text)

   # Memo and References

   def showMemo (self, editor, name) :
       pass

   def showReferences (self, editor, name) :
       pass

# --------------------------------------------------------------------------

if __name__ == '__main__' :
   app = QApplication (sys.argv)
   setApplStyle (app)

   win = CentralWindow ()
   win.additionalMenuItems ()

   app.win = win
   win.appl = app
   win.show ()

   win.info.redirectOutput ()

   app.exec_ ()

# --------------------------------------------------------------------------

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
