#!/usr/bin/env python

from __future__ import print_function

import os, sys, importlib, inspect
# import subprocess

use_webkit = True
use_webengine = True
use_javascript = True
use_javascript_debugger = True
use_dbus = True
use_xlib = True

from util import use_pyside2, use_qt5,  use_old_pyqt
if use_pyside2 :
   from PySide2.QtCore import *
   from PySide2.QtGui import *
   from PySide2.QtWidgets import *
   if use_webengine :
      try :
         from PySide2.QtWebEngine import *
         from PySide2.QtWebEngineWidgets import *
         print ("found PySide2.QtWebEngine")
         use_webkit = False
      except :
         use_webengine = False
         print ("missing PySide2.QtWebEngine")
   if use_webkit :
      try :
         from PySide2.QtWebKit import *
         from PySide2.QtWebKitWidgets import *
         print ("found PySide2.QtWebKit")
      except :
         use_webkit = False
         print ("missing PySide2.QtWebKit")
   if use_javascript :
      try :
         from PySide2.QtScript import *
         print ("found PySide2.QtScript")
      except :
         use_javascript = False
         print ("missing PySide2.QtScript")
   if use_javascript_debugger :
      try :
         from PySide2.QtScriptTools import *
      except :
         use_javascript_debugger = False
         print ("missing PySide2.QtScriptTools")
   if use_dbus :
      try :
         from PySide2.QtDBus import *
         print ("found PySide2.QtDBus")
      except :
         use_dbus = False
         print ("missing PySide2.QtDBus")
elif use_qt5 :
   from PyQt5.QtCore import *
   from PyQt5.QtGui import *
   from PyQt5.QtWidgets import *
   if use_webengine :
      try :
         from PyQt5.QtWebEngine import *
         from PyQt5.QtWebEngineWidgets import *
         print ("found PyQt5.QtWebEngine")
         use_webkit = False
      except :
         use_webengine = False
         print ("missing PyQt5.QtWebEngine")
   if use_webkit :
      try :
         from PyQt5.QtWebKit import *
         from PyQt5.QtWebKitWidgets import *
         print ("Found PyQt5.QtWebKit")
      except :
         use_webkit = False
         print ("missing PyQt5.QtWebKit")
   if use_javascript :
      try :
         from PyQt5.QtScript import *
         print ("Found PyQt5.QtScript")
      except :
         use_javascript = False
         print ("missing PyQt5.QtScript")
   if use_javascript_debugger :
      try :
         from PyQt5.QtScriptTools import *
      except :
         use_javascript_debugger = False
         print ("missing PyQt5.QtScriptTools")
   if use_dbus :
      try :
         from PyQt5.QtDBus import *
         print ("found PyQt5.QtDBus")
      except :
         use_dbus = False
         print ("missing PyQt5.QtDBus")
else :
   from PyQt4.QtCore import *
   from PyQt4.QtGui import *
   use_webengine = False
   if use_webkit :
      try :
         from PyQt4.QtWebKit import *
         print ("found PyQt4.QtWebKit")
      except :
         use_webkit = False
         print ("missing PyQt4.QtWebKit")
   if use_javascript :
      try :
         from PyQt4.QtScript import *
         print ("found PyQt4.QtScript")
      except :
         use_javascript = False
         print ("missing PyQt4.QtScript")
   if use_javascript_debugger :
      try :
         from PyQt4.QtScriptTools import *
         print ("found PyQt4.QtScriptTools")
      except :
         use_javascript_debugger = False
         print ("missing PyQt4.QtScriptTools")
   if use_dbus :
      try :
         from PyQt4.QtDBus import *
         print ("found PyQt4.QtDBus")
      except :
         use_dbus = False
         print ("missing PyQt4.QtDBus")

if use_xlib :
   try :
      import Xlib
      import Xlib.display
      import Xlib.XK
      import time
   except :
      use_xlib = False
      print ("missing Xlib")

from util import findIcon,qstring_starts_with
from info import Info

# --------------------------------------------------------------------------

class WebWin (QWidget) :

    def __init__ (self, win) :
        super (WebWin, self).__init__ (win)
        self.win = win

        if use_webengine :
           self.view = QWebEngineView (self)
        else :
           self.view = QWebView (self)

        self.progress = 0

        self.view.loadFinished.connect (self.adjustLocation)
        self.view.titleChanged.connect (self.adjustTitle)
        self.view.loadProgress.connect (self.setProgress)
        self.view.loadFinished.connect (self.finishLoading)

        self.locationEdit = QLineEdit (self)
        self.locationEdit.setSizePolicy (QSizePolicy.Expanding,
                                         self.locationEdit.sizePolicy().verticalPolicy())
        self.locationEdit.returnPressed.connect (self.changeLocation)

        toolBar = QToolBar ()
        if use_webengine :
           toolBar.addAction (self.view.pageAction (QWebEnginePage.Back))
           toolBar.addAction (self.view.pageAction (QWebEnginePage.Forward))
           toolBar.addAction (self.view.pageAction (QWebEnginePage.Reload))
           toolBar.addAction (self.view.pageAction (QWebEnginePage.Stop))
        else :
           toolBar.addAction (self.view.pageAction (QWebPage.Back))
           toolBar.addAction (self.view.pageAction (QWebPage.Forward))
           toolBar.addAction (self.view.pageAction (QWebPage.Reload))
           toolBar.addAction (self.view.pageAction (QWebPage.Stop))
        toolBar.addWidget (self.locationEdit)

        layout = QVBoxLayout ()
        self.setLayout (layout)
        layout.addWidget (toolBar)
        layout.addWidget (self.view)

    def load (self, url) :
        self.view.load (url)

    def adjustLocation (self) :
        self.locationEdit.setText (str (self.view.url().toString()))

    def changeLocation (self) :
        url = QUrl.fromUserInput (self.locationEdit.text ())
        self.view.load (url)
        self.view.setFocus ()

    def adjustTitle (self) :
        if 0 < self.progress < 100:
           self.setWindowTitle ("%s (%s%%)" % (self.view.title(), self.progress))
        else:
           self.setWindowTitle (self.view.title())

    def setProgress (self, p) :
        self.progress = p
        self.adjustTitle ()

    def finishLoading (self) :
        self.progress = 100
        self.adjustTitle ()

# https://github.com/Werkov/PyQt4/blob/master/examples/webkit/fancybrowser/fancybrowser.py

# --------------------------------------------------------------------------

class InfoWithTools (Info) :

   def __init__ (self, win) :
       super (InfoWithTools, self).__init__ (win)
       self.work_dir = ""
       self.env_dict = { }

   def selectValues (self, name) :
       result = [ ]
       keys = self.win.commands.allKeys ()
       for qkey in keys :
          key = str (qkey)
          ok = False
          if key == name :
             ok = True
          elif key.startswith (name) :
             first = key [ len (name) ]
             if first == '-' or first == '_' or first >= '0' and first <= '9' :
              ok = true
          if ok :
             result.append (self.win.commands.string (key))
       return result

   def readEnvironment (self, group) :
       "env"
       self.win.commands.beginGroup (group)
       env_name = self.win.commands.string ("env");
       self.win.commands.endGroup ()

       if env_name != "" :
          self.readEnvironment (env_name); # read other environment

       self.win.commands.beginGroup (group)

       "cd"
       self.work_dir = self.win.commands.string ("cd")
          # print ("DIRECTORY", self.work_dir)

       "set, var"
       keys = self.win.commands.allKeys ()
       for qkey in keys :
          key = str (qkey)
          if key.startswith ("set") or key.startswith ("var") :
             text = str (self.win.commands.string (key))
             answer = text.split ("=", 1)
             name = answer [0]
             value = answer [1]
             name = name.strip ()
             value = value.strip ()
             self.env_dict [name] = value
             # print ("SET", name + "=" + value)

       self.win.commands.endGroup ()

   def runGroup (self, group, fileName = "") :
       self.work_dir = ""
       self.env_dict = { }
       self.readEnvironment (group)

       # read run parameters from commands group
       self.win.commands.beginGroup (group)

       "url"
       url = None
       inx = 1
       while url == None and inx < 10 :
          key = self.win.commands.string ("url" + str (inx))
          if key != "" :
             url = QUrl (key)
             if not url.isValid () :
                url = None
             else:
                if use_old_pyqt:
                   path = url.toLocalFile ()
                   if path != None and path != "" :
                      if not QFile.exists (path) :
                         url = None
                else :
                   if url.isLocalFile () :
                      path = url.toLocalFile ()
                      if not QFile.exists (path) :
                         url = None
          inx = inx + 1
       if url == None :
          url = ""
       else :
          url = url.toString ()

       "title"
       title = self.win.commands.string ("title")

       "cmd"
       cmd = self.win.commands.string ("cmd")

       "jscript"
       jscript = self.win.commands.string ("jscript")

       "module cls func param outputSuffix"
       module = self.win.commands.string ("module")
       cls = self.win.commands.string ("cls")
       func = self.win.commands.string ("func")
       param = self.win.commands.string ("param")

       "loaded_module"
       loaded_module = self.win.commands.string ("loaded_module")

       "addWin"
       addWin = self.win.commands.boolean ("addWin")

       "addFileName"
       addFileName = self.win.commands.boolean ("addFileName")

       if fileName != "" :
          addFileName = True

       if addFileName :
          if fileName == "" :
             e = self.win.getEditor ()
             fileName = e.getFileName ()
          if cmd != "" :
             if cmd.find ("$") != -1 :
                cmd = cmd.replace ("$", fileName)
             else :
                cmd = cmd + " " + fileName
          else :
             param = fileName

       "cmm"
       cmm = self.win.commands.boolean ("cmm")

       "example"
       example = self.win.commands.string ("example")

       self.win.commands.endGroup () # return to top-level group

       if url != "" :
          # print ("URL", url)
          self.showUrl (url, title)

       elif cmd != ""  or jscript != "" :
          try :
             if self.work_dir != "" :
                save_dir = os.getcwd ()
                os.chdir (self.work_dir)
             if cmd != "" :
                self.runCommand (cmd)
             elif jscript != "" :
                self.runJavaScript (jscript)
          finally :
             if self.work_dir != "" :
                os.chdir (save_dir)

       else :
          try :
             if self.work_dir != "" :
                sys.path.insert (0, self.work_dir)
                # do not change current directory when importing Python module

             for load in self.selectValues ("load") :
                 self.win.loadModule (load)

             if cmm or example != "" :
                self.runCmmModule (group)

             elif module != "" :
                self.runPythonModule (module, cls, func, addWin, param)

             elif loaded_module != "" :
                self.runLoadedModule (loaded_module, cls, func, addWin, param)

          finally :
             if self.work_dir != "" :
                del sys.path [0]

   def showUrl (self, url, title = "") :
       if self.win != None and ( use_webengine or use_webkit ) :
          widget = WebWin (self.win)
          self.win.firstTabWidget.addTab (widget, title)
          self.win.firstTabWidget.setCurrentWidget (widget)
          widget.load (QUrl (url))

   def runCommand (self, cmd) :
       # os.system (cmd)
       # subprocess.call (str (cmd), shell=True)

       self.process = QProcess (self.win)

       if self.work_dir != "" :
          self.process.setWorkingDirectory (self.work_dir)

       env = QProcessEnvironment.systemEnvironment () # important
       for name in self.env_dict :
           value = self.env_dict [name]
           env.insert (name, value)
           # print ("SET", name + "=" + value)
       self.process.setProcessEnvironment (env)

       self.process.setProcessChannelMode (QProcess.MergedChannels)
       self.process.readyRead.connect (self.commandDataReady)
       self.process.finished.connect (self.commandDataFinished)

       if self.stopAction != None :
          self.process.started.connect (lambda: self.stopAction.setEnabled (True))
          self.process.finished.connect (lambda: self.stopAction.setEnabled (False))

       print ("RUN", cmd)
       self.process.start ("/bin/sh", [ "-c", cmd ] ) # !?

       self.win.process_list.append (self.process)
       self.process.finished.connect (lambda param1, param2, self=self, process=self.process: self.forgetProcess (process))

   def forgetProcess (self, process) :
       self.win.process_list.remove (process)

   def runJavaScript (self, fileName) :
       if use_javascript :
          with open (fileName, "r") as f :
               code = f.read ()
               engine = QScriptEngine ()
               if use_javascript_debugger :
                  debugger = QScriptEngineDebugger ()
                  debugger.attachTo (engine)
                  debugWindow = debugger.standardWindow ()
                  debugWindow.resize (1024, 640)
                  self.debugWindow = debugWindow # important: keep reference
               infoObject = engine.newQObject (self.win.info)
               engine.globalObject().setProperty ("info", infoObject)
               engine.evaluate (code, fileName)

   def runPythonFunc (self, f, addWin, param) :
       result = None
       if addWin :
          if param != "" :
             result = f (self.win, param)
          else :
             result = f (self.win)
       else :
          if param != "" :
             result = f (param)
          else :
             result = f ()
       return result

   def runPythonMethod (self, m, cls, func, addWin, param) :
       result = None
       if m != None and (cls != "" or func != "") :
          # cls and func are not empty ... add window to class, add parameters to func
          # cls is empty ... add parameters to func
          # func is empty ... add parameters to cls
          if cls != "" :
             c = getattr (m, cls)
             if inspect.isclass (c) or inspect.isfunction (c) :
                c = self.runPythonFunc (c, addWin, "")
                addWin = False
             if func != "" :
                c = getattr (c, func)
             result = self.runPythonFunc (c, addWin, param)
          else :
             f = getattr (m, func)
             result = self.runPythonFunc (f, addWin, param)
       return result

   def runPythonModule (self, module, cls, func, addWin, param) :
       m = self.win.loadModule (module)
       self.runPythonMethod (m, cls, func, addWin, param)

   def runLoadedModule (self, module, func, addWin, param) :
       m = sys.modules [module]
       self.runPythonMethod (m, cls, func, addWin, param)

   def runCmmModule (self, group) :
       m = sys.modules ["cmm_plugin"]
       c = m.cmm_instance
       c.runCmmGroup (self.win.commands, group)

   # -- run --

   def run (self, group, fileName = "") :
       self.runGroup (group, fileName)

   def stop (self) :
       self.process.terminate ()

   def clearOutput (self) :
       self.clear ()

   # -- mouse click --

   def goToCtrlLocation (self, fileName, line, column) :
       self.goToKDevelop (fileName, line, column)

   def goToKDevelop (self, fileName, line, column) :
       fileName = os.path.abspath (fileName)
       line = line - 1
       # print ("KDEVELOP", fileName, "line:", line)
       if use_dbus :
          connection = QDBusConnection.sessionBus()
          serviceNames = connection.interface().registeredServiceNames().value();
          prefix = "org.kdevelop.kdevelop-"
          for name in serviceNames :
              if qstring_starts_with (name, prefix) :
                 # print ("SERVICE", name)
                 ifc = QDBusInterface(name, "/org/kdevelop/DocumentController", "", connection)
                 ifc.call ("openDocumentSimple", fileName, line, column)

# --------------------------------------------------------------------------

class ClickAction (QAction) :

    def __init__ (self, win, group) :
        super (ClickAction, self).__init__ (win)
        self.win = win
        self.group = group

        # read menu parameters
        self.win.commands.beginGroup (self.group)

        "title shortcut tooltip icon ext example"

        title = self.win.commands.string ("title")
        if title != "" :
           self.setText (title)

        shortcut = self.win.commands.string ("shortcut")
        if shortcut != "" :
           self.setShortcut (shortcut)

        tooltip = self.win.commands.string ("tooltip")
        if tooltip != "" :
           self.setToolTip (tooltip)
           self.setStatusTip (tooltip)

        icon = self.win.commands.string ("icon")
        if icon != "" :
           icon = findIcon (icon)
           if icon != None :
              self.setIcon (icon)

        ext = self.win.commands.string ("ext")
        if ext != "" :
           has_ext = self.win.hasExtension (self.win.getEditor(), ext)
           self.setEnabled (has_ext)

        example = self.win.commands.string ("example")
        if title == "" and example != ""  :
           self.setText (example)

        if title == "" and example == ""  :
           self.setText (group)

        self.win.commands.endGroup () # return to top-level group

        self.triggered.connect (self.click)

    def click (self) :
        self.win.info.run (self.group)

# --------------------------------------------------------------------------

def setupItem (win, menu, group) :
    separator = win.commands.string (group + "/separator", "0") != "0"
    if separator :
       act = menu.addSeparator ()
       act.dynamic = True
    else :
       act = ClickAction (win, group)
       act.dynamic = True
       menu.addAction (act)

def setupItems (win, menu, prefix) :
    groups = win.commands.childGroups ()
    for group in groups :
        group_name = str (group)
        if group_name.startswith (prefix) :
           setupItem (win, menu, group_name)

def removeItems (win, menu) :
    for act in menu.actions () :
        if hasattr (act, "dynamic") :
           menu.removeAction (act)
           # del act

# --------------------------------------------------------------------------

if use_xlib :

   def get_property (disp, target, property_name)  :
       result = target.get_full_property (disp.intern_atom(property_name), Xlib.X.AnyPropertyType)
       if result != None :
          result = result.value
       return result

   def addBrowserWindows (target, win_list) :
       disp = Xlib.display.Display ()
       root = disp.screen().root
       window_list = get_property (disp, root, '_NET_CLIENT_LIST')

       for window_id in window_list :
           window = disp.create_resource_object ('window', window_id)
           title = get_property (disp, window, '_NET_WM_NAME')
           if title != None and title.endswith ("Mozilla Firefox") :
              target.addItem ("Firefox:" + title)
              win_list.append (window_id)

   if 1 :
      def sendKey (window_id, cmd) :
          disp = Xlib.display.Display ()
          root = disp.screen().root
          window = disp.create_resource_object ('window', window_id)

          print ("sendKey", cmd)
          state = 0
          if cmd.startswith ("ctrl+") or cmd.startswith ("Ctrl+") :
             state = Xlib.X.ControlMask
             cmd = cmd [5:]
          keysym = Xlib.XK.string_to_keysym (cmd)
          keycode = disp.keysym_to_keycode (keysym)

          event = Xlib.protocol.event.KeyPress (
                   time = int (time.time()),
                   root = root,
                   window = window_id,
                   same_screen = 0,
                   child = Xlib.X.NONE,
                   root_x = 0,
                   root_y = 0,
                   event_x = 0,
                   event_y = 0,
                   state = state,
                   detail = keycode)
          window.send_event (event, propagate = True)
          disp.sync()

          event = Xlib.protocol.event.KeyRelease (
                   time = int (time.time()),
                   root = root,
                   window = window_id,
                   same_screen = 0,
                   child = Xlib.X.NONE,
                   root_x = 0,
                   root_y = 0,
                   event_x = 0,
                   event_y = 0,
                   state = state,
                   detail = keycode)
          window.send_event (event, propagate = True)
          disp.sync()

   if 0 :
      def sendKey (cmd) :
          disp = Xlib.display.Display ()
          root = disp.screen().root
          window_list = get_property (disp, root, '_NET_CLIENT_LIST')

          for window_id in window_list :
              window = disp.create_resource_object ('window', window_id)
              title = get_property (disp, window, '_NET_WM_NAME')
              if title != None and title.endswith ("Mozilla Firefox") :
                 browser_win = window
                 browser_id = window_id

                 print ("sendKey", browser_id, cmd)
                 state = 0
                 if cmd.startswith ("ctrl+") or cmd.startswith ("Ctrl+") :
                    state = Xlib.X.ControlMask
                    cmd = cmd [5:]
                 keysym = Xlib.XK.string_to_keysym (cmd)
                 keycode = disp.keysym_to_keycode (keysym)

                 event = Xlib.protocol.event.KeyPress (
                          time = int (time.time()),
                          root = root,
                          window = browser_id,
                          same_screen = 0,
                          child = Xlib.X.NONE,
                          root_x = 0,
                          root_y = 0,
                          event_x = 0,
                          event_y = 0,
                          state = state,
                          detail = keycode)
                 browser_win.send_event (event, propagate = True)
                 disp.sync()

                 event = Xlib.protocol.event.KeyRelease (
                          time = int (time.time()),
                          root = root,
                          window = browser_id,
                          same_screen = 0,
                          child = Xlib.X.NONE,
                          root_x = 0,
                          root_y = 0,
                          event_x = 0,
                          event_y = 0,
                          state = state,
                          detail = keycode)
                 browser_win.send_event (event, propagate = True)
                 disp.sync()

   if 0 :
      browser_win = None
      browser_id = None

      def lookupWindow () :
          global browser_win
          global browser_id

          disp = Xlib.display.Display ()
          root = disp.screen().root
          window_list = get_property (disp, root, '_NET_CLIENT_LIST')

          for window_id in window_list :
              window = disp.create_resource_object ('window', window_id)
              title = get_property (disp, window, '_NET_WM_NAME')
              pid = get_property (disp, window, '_NET_WM_PID') [0]
              print ("WIN", title)
              if title != None and title.endswith ("Mozilla Firefox") :
                 browser_win = window
                 browser_id = window_id
                 print ("FOUND", browser_id)
                 break

      import ctypes
      X11 = ctypes.CDLL("libX11.so")

      class Display (ctypes.Structure) :
         pass

      class XKeyEvent (ctypes.Structure) :
         _fields_ = [
            ('type', ctypes.c_int),
            ('serial', ctypes.c_ulong),
            ('send_event', ctypes.c_int),
            ('display', ctypes.POINTER(Display)),
            ('window', ctypes.c_ulong),
            ('root', ctypes.c_ulong),
            ('subwindow', ctypes.c_ulong),
            ('time', ctypes.c_ulong),
            ('x', ctypes.c_int),
            ('y', ctypes.c_int),
            ('x_root', ctypes.c_int),
            ('y_root', ctypes.c_int),
            ('state', ctypes.c_uint),
            ('keycode', ctypes.c_uint),
            ('same_screen', ctypes.c_int),
         ]

      class XEvent(ctypes.Union) :
         _fields_ = [
            ('type', ctypes.c_int),
            ('xkey', XKeyEvent),
            ('pad', ctypes.c_long*24),
         ]

      X11.XOpenDisplay.restype = ctypes.POINTER(Display)

      def sendKey (cmd) :
          if browser_win == None :
             lookupWindow ()
          if browser_win != None :
             print ("sendKey (2)", cmd)
             state = 0
             if cmd.startswith ("ctrl+") or cmd.startswith ("Ctrl+") :
                state = Xlib.X.ControlMask
                cmd = cmd [5:]
             code = Xlib.XK.string_to_keysym (cmd)
             display = X11.XOpenDisplay (None)
             key = XEvent (type = Xlib.X.KeyPress).xkey # KeyPress
             # key.keycode = X11.XKeysymToKeycode(display, Xlib.XK.XK_Page_Down)
             key.keycode = X11.XKeysymToKeycode (display, code)
             key.root = X11.XDefaultRootWindow (display)
             key.window = browser_id
             key.state = state
             X11.XSendEvent (display, key.window, True, 1, ctypes.byref(key))
             X11.XCloseDisplay(display)

if not use_xlib :

   def sendKey (window_id, cmd) :
       pass

   def addBrowserWindows (target, win_list) :
       pass

# http://blog.kivy.org/2011/05/kivy-window-management-on-x11/
# http://unix.stackexchange.com/questions/5999/setting-the-window-dimensions-of-a-running-application

# --------------------------------------------------------------------------

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
