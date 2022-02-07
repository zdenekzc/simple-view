#!/usr/bin/env python

from __future__ import print_function

import sys, os, inspect, importlib

# --------------------------------------------------------------------------

if sys.version_info >= (3,) :
   use_python3 = True
else :
   use_python3 = False

# --------------------------------------------------------------------------

# enabled libraries
enable_pyside2 = False
enable_qt5 = True

if not use_python3 :
   enable_pyside2 = False
   enable_qt5 = False

# used libraries
use_pyside2 = False
use_qt5 = False

# --------------------------------------------------------------------------

use_simple = False

# --------------------------------------------------------------------------

"""
if enable_pyside2 :
   try :
      print ("trying PySide2")
      from PySide2.QtCore import *
      from PySide2.QtGui import *
      from PySide2.QtWidgets import *
      use_pyside2 = True
      print ("found PySide2")
   except :
      print ("missing PySide2")

if enable_qt5 and not use_pyside2 :
   try :
      print ("trying PyQt5")
      from PyQt5.QtCore import *
      from PyQt5.QtGui import *
      from PyQt5.QtWidgets import *
      use_qt5 = True
      print ("found PyQt5")
   except :
      print ("missing PyQt5")

if not use_pyside2 and not use_qt5 :
   print ("trying PyQt4")
   from PyQt4.QtCore import *
   from PyQt4.QtGui import *
   from PyQt4.Qt import PYQT_VERSION
   print ("found PyQt4")
"""

# --------------------------------------------------------------------------

if enable_pyside2 :
   try :
      print ("trying PySide2")
      from PySide2 import QtCore
      from PySide2 import QtGui
      from PySide2 import QtWidgets
      use_pyside2 = True
      print ("found PySide2")
   except :
      print ("missing PySide2")

if enable_qt5 and not use_pyside2 :
   try :
      print ("trying PyQt5")
      from PyQt5 import QtCore
      from PyQt5 import QtGui
      from PyQt5 import QtWidgets
      use_qt5 = True
      print ("found PyQt5")
   except :
      print ("missing PyQt5")

if not use_pyside2 and not use_qt5 :
   print ("trying PyQt4")
   from PyQt4 import QtCore
   from PyQt4 import QtGui
   print ("found PyQt4")

# --------------------------------------------------------------------------

qt_modules = [ ]
qt_symbols = { }

def store_qt_modules  () :
    global_symbols = globals ()
    for name in global_symbols :
        obj = global_symbols [name]
        if inspect.ismodule (obj) :
           if name.startswith ("Qt") :
              # print ("MODULE", name)
              qt_modules.append (obj)
    for m in qt_modules :
        module_symbols = dir (m)
        for name in module_symbols :
           if not name.startswith ("_") :
              # print ("SYMBOL", name)
              qt_symbols [name] = getattr (m, name)

def additional_qt_module (target, name) :
    if use_pyside2 :
       name = "PySide2." + name
    elif use_qt5 :
       name = "PyQt5." + name
    else :
       name = "PyQt4." + name
    symbols = { }
    m = importlib.import_module (name)
    module_symbols = dir (m)
    for name in module_symbols :
        if not name.startswith ("_") :
           symbols [name] = getattr (m, name)
    target.update (symbols)


def import_qt_modules  (target, additional_names = [ ]) :
    target.update (qt_symbols)
    for name in additional_names :
        additional_qt_module (target, name)

store_qt_modules ()
import_qt_modules (globals ())

# --------------------------------------------------------------------------

def get_module (module_name) :
    if module_name in sys.modules :
       module = sys.modules [module_name]
    else :
       module = importlib.import_module (module_name)
    return module

def import_all_from (target, module_name) :
    module = get_module (module_name)
    module_symbols = dir (module)
    symbols = { }
    for name in module_symbols :
        if not name.startswith ("_") :
           symbols [name] = getattr (module, name)
    target.update (symbols)

def import_from (target, module_name, object_name) :
    module = get_module (module_name)
    target [object_name] = getattr (module, object_name )

def import_module (target, module_name) :
    module = get_module (module_name)
    target [module_name] = module

# --------------------------------------------------------------------------

use_new_qt = use_pyside2 or use_qt5
use_new_api = use_python3 or use_pyside2 or use_qt5
use_old_pyqt = not use_pyside2 and not use_qt5 and (QT_VERSION < 0x040800 or PYQT_VERSION < 0x041100)

def columnNumber (cursor) :
    if use_old_pyqt :
       return cursor.columnNumber ()
    else :
       return cursor.positionInBlock ()

def setResizeMode (header, section, mode) :
    if use_new_qt :
       header.setSectionResizeMode (section, mode)
    else :
       header.setResizeMode (section, mode)
    "mode = QHeaderView.ResizeToContents or QHeaderView.Fixed"

# Debian 6: Qt 4.6, PyQt 4.7
# Fedora 14: Qt 4.7, PyQt 4.7
# Debian 7: Qt 4.8, PyQt 4.9
# Fedora 21: Qt 4.8, PyQt 4.11

# --------------------------------------------------------------------------

def bytearray_to_str (b) :
    if use_pyside2 :
       return str (b.data (), "ascii")
    elif use_python3 :
       return str (b, "ascii")
    else :
       return str (b)

def simple_bytearray_to_str (b) :
    if use_pyside2 :
       return str (b.data (), "ascii")
    elif use_python3 :
       # return str (b, "latin_1",errors="replace")
       # return str (b, "ascii", errors="replace")
       # return str (b, "cp1252", errors="replace")
       return str (b, "ascii", errors="ignore")
    else :
       return str (b)

def variant_to_str (v) :
    if use_new_api :
       return str (v) # boolean -> str
    else :
       return str (v.toString ())

def qstring_to_str (s) :
    if use_new_api :
       return s
    else :
       return str (s)

def qstringref_to_str (s) :
    if use_new_api :
       return s
    else :
       return str (s.toString ())

def qstring_starts_with (s, t) :
    if use_new_api :
       return s.startswith (t)
    else :
       return s.startsWith (t)

def dialog_to_str (s) :
    # get file name from open file dialog results
    if use_new_api :
       return s[0]
    else :
       return str (s)

def list_count (obj) :
    return len (obj)
    # if use_new_api :
    #    return len (obj)
    # else :
    #    return obj.count ()

def sort_list (obj, compare) :
    if use_python3 :
       obj.sort (key = cmp_to_key (compare))
    else :
       obj.sort (compare)

def qstringlist_to_list (obj) :
    if use_new_api :
       return obj
    else :
       return [ str (item) for item in obj ]

# --------------------------------------------------------------------------

# Main Window

main_win = None

def set_win (w) :
    global main_win
    main_win = w

def get_win () :
    global main_win
    return main_win

# --------------------------------------------------------------------------

# Text Properties

class Text (object) :

   bookmarkProperty = QTextFormat.UserProperty
   locationProperty = QTextFormat.UserProperty + 1 # source location in output window
   infoProperty = QTextFormat.UserProperty + 2
   defnProperty = QTextFormat.UserProperty + 3
   openProperty = QTextFormat.UserProperty + 4
   closeProperty = QTextFormat.UserProperty + 5
   outlineProperty = QTextFormat.UserProperty + 6

# --------------------------------------------------------------------------

# Colors

color_cache = { }

def findColor (name):
    global color_cache
    if not isinstance (name, str) :
       return name # !?
    elif name in color_cache :
       return color_cache [name]
    else :
       color = QColor (name)
       color_cache [name] = color
       return color

def defineColor (alias, color):
    global color_cache
    if isinstance (color, QColor) :
       color_cache [alias] = color
    else :
       color_cache [alias] = findColor (color)

# --------------------------------------------------------------------------

color_map = { }
color_names = [ ]

def findColorNames () :
    color_names = [ str (name) for name in QColor.colorNames () ]
    for name in color_names :
        color_map [name] = QColor (name)

# --------------------------------------------------------------------------

class ColorTable (object) :
    def __init__ (self, win, name, table) :
        super (ColorTable, self).__init__ ()
        self.name = name
        self.table = table

        ini = win.settings # view.ini
        ini.beginGroup (name)
        keys = ini.allKeys ()
        if len (keys) != 0 :
           self.table = [ ]
           for key in keys :
               self.table.append (ini.string (key))
        ini.endGroup ()

        self.inx = 0
        self.cnt = len (self.table)

    def nextColor (self) :
        color = findColor (self.table [self.inx])
        self.inx = (self.inx + 1) % self.cnt
        return color

def addColors (win) :
    win.namespaceColors = ColorTable (win, "namespaceColors", [ "olive" ])
    win.classColors = ColorTable (win, "classColors", [ "blue", "orange", "gold" ])
    win.enumColors = ColorTable (win, "enumColors", [ "orange" ])
    win.typedefColors = ColorTable (win, "enumColors", [ "cyan" ])
    # win.variableColors = ColorTable (win, "variableColors", [ "cornflowerblue" ])
    # win.functionColors = ColorTable (win, "functionColors", [ "magenta" ])

    win.variableColors = ColorTable (win, "variableColors", ["#e41a1c", "#377eb8", "#4daf4a", "#984ea3", "#ff7f00"])
    win.functionColors = ColorTable (win, "functionColors", ["#c65c8a", "#70a845", "#a361c7", "#b68f40", "#6587cd", "#cc5a43", "#4aac8d"])

    if 0 :
       # From kdevelop-5.3.2/kdevplatform/language/highlighting
       # Primary colors taken from: http://colorbrewer2.org/?type=qualitative&scheme=Paired&n=12
       win.variableColors = ColorTable (win, "variableColors", [
          "#b15928", "#ff7f00", "#b2df8a", "#33a02c", "#a6cee3",
          "#1f78b4", "#6a3d9a", "#cab2d6", "#e31a1c", "#fb9a99" ])

       # Supplementary colors generated by: http://tools.medialab.sciences-po.fr/iwanthue/
       win.functionColors = ColorTable (win, "functionColors", [
          "#D33B67", "#5EC764", "#6CC82D", "#995729", "#FB4D84",
          "#4B8828", "#D847D0", "#B56AC5", "#E96F0C", "#DC7161",
          "#4D7279", "#01AAF1", "#D2A237", "#F08CA5", "#C83E93",
          "#5D7DF7", "#EFBB51", "#108BBB", "#5C84B8", "#02F8BC",
          "#A5A9F7", "#F28E64", "#A461E6", "#6372D3" ])

# --------------------------------------------------------------------------

# Icons

icon_path = [ ]
icon_cache = { }

def addIconDir (path):
    global icon_path
    path = os.path.expanduser (path)
    path = os.path.abspath (path)
    icon_path.append (path)

def findIcon (name):
    global icon_path, icon_cache
    if name in icon_cache :
       icon = icon_cache [name]
    else :
       icon = None
       for path in icon_path :
           file_name = os.path.join (path, name + ".png")
           if os.path.isfile (file_name) :
              icon = QIcon (os.path.join (path, name + ".png"))
              break
       if icon == None :
          icon = QIcon.fromTheme (name)
       icon_cache [name] = icon
    return icon

def defineIcon (alias, name):
    global icon_cache
    if alias not in icon_cache : # if alias is not already defined
       icon = findIcon (name)
       if icon != None :
          icon_cache [alias] = icon # store icon under new name

# --------------------------------------------------------------------------

# Fonts

def setEditFont (edit) :
    # if not use_simple :
    #    font = QFont ("Luxi Mono", 14)
    #    font.setFixedPitch (True)
    #    edit.setFont (font)
    pass

def setZoomFont (edit) :
    edit.setStyleSheet ("QPlainTextEdit {font-size: 18pt}")
    # font = QFont ("Luxi Mono", 18)
    # font.setPointSize (18)
    # font.setFixedPitch (True)
    # edit.setFont (font)

# --------------------------------------------------------------------------

# Window size

def resizeDetailWindow (window) :
    if not use_simple :
       window.resize (800, 640)

def resizeMainWindow (window) :
    if not use_simple :
       window.resize (1200, 800)
       # window.middle.resize (640, 480)

# --------------------------------------------------------------------------

# Application style

def setApplStyle (app) :

    if not use_simple :
       app.setStyleSheet ("QTabBar::tab:selected {color: blue }"
                          "QWidget {font-size: 12pt}"
                          "Editor {font-family: \"Luxi Mono\" ; font-size: 14pt}"
                          # "QToolTip { color: #000; background-color: yellow; border 1px solid}"
                         )

    if not use_simple :
       app.setStyle (QStyleFactory.create ("Fusion"))

    if not use_simple :
       QIcon.setThemeName ("oxygen")
       if use_qt5 :
          try :
             QIcon.setFallbackThemeName ("mate")
          except :
             pass
       # /usr/share/icons/oxygen
       # dnf install oxygen-icon-theme

    findColorNames ()

    if 0 :
       addIconDir ("/abc/icons/qt4")
       addIconDir ("/abc/icons/glade2")
       addIconDir ("/abc/icons/lazarus")
       addIconDir ("/abc/icons/monodevelop2")
       # addIconDir ("~/temp/monodevelop-2.8.8.4/src/core/MonoDevelop.Ide/icons")
       # addIconDir ("~/temp/monodevelop-4.0.14/src/core/MonoDevelop.Ide/icons")
       # addIconDir ("~/temp/monodevelop-5.7/src/core/MonoDevelop.Ide/icons/light")
       # addIconDir ("~/temp/monodevelop-5.9/src/core/MonoDevelop.Ide/icons")

       defineIcon ("namespace", "element-namespace-16")
       defineIcon ("class",     "element-class-16")
       defineIcon ("function",  "element-method-16")
       defineIcon ("variable",  "element-field-16")
       defineIcon ("enum",      "element-enumeration-16")

    defineIcon ("file", "folder")

    # defineIcon ("module",    "code-block")
    defineIcon ("namespace", "code-block")
    defineIcon ("class",     "code-class")
    defineIcon ("enum",      "code-class")
    defineIcon ("function",  "code-function")
    defineIcon ("variable",  "code-variable")
    defineIcon ("type",      "code-typedef")
    defineIcon ("block",     "code-block")

    defineIcon ("assign",     "edit-rename")
    defineIcon ("call",       "draw-rectangle")
    # defineIcon ("define",     "draw-polygon")
    defineIcon ("with",       "draw-ellipse")
    defineIcon ("nothing",    "draw-donut")

    defineIcon ("local-variable",  "view-list-text")
    defineIcon ("local-declare",   "view-list-tree")
    defineIcon ("local-define",    "view-list-details")

    """
    some icon names:

    edit-rename
    edit-select-all
    draw-ellipse
    shapes
    page-simple
    project-development
    tab-duplicate
    text-field
    view-close
    view-list-details
    view-list-icons
    view-list-text
    view-list-tree
    view-form
    view-form-table
    view-grid
    view-group
    view-process-all
    view-multiple-objects
    view-sidetree
    window-duplicate

    dialog-ok-apply
    games-hint
    liste-remove
    view-statistics
    """

    defineColor ("ink", QColor (0, 0, 0))
    defineColor ("paper", QColor (255, 255, 255))

    defineColor ("namespace", "green")
    defineColor ("class",     "blue")
    defineColor ("function",  "brown")
    defineColor ("variable",  "orange")

    defineColor ("attr",      "orange")
    defineColor ("unknown",   "red")
    defineColor ("foreign",   "green")

# --------------------------------------------------------------------------

# Fedora 21
# ---------
# glade2       glade-2.12.2/glade/graphics
# glade3       glade3-3.8.5/plugins/gtk+/icons/22x22
# lazarus      lazarus-1.2.0/images/componemts
# monodevelop2 monodevelop-2.8.8.4/src/core/MonoDevelop.Ide/icons
# qt4          qt-everywhere-opensource-src-4.8.6/tools/designer/src/components/formeditor/images/widgets
# qt5          qttools-opensource-src-5.3.2/src/designer/src/components/formeditor/images/widgets

# --------------------------------------------------------------------------

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
