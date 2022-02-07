
# input.py

from __future__ import print_function

# --------------------------------------------------------------------------

supportGenerator = None

fileNames = [ "" ] # list of file names

def indexToFileName (inx) :
    global fileNames
    if inx < 0 :
       return ""
    else :
       return fileNames [inx]

def fileNameToIndex (name) :
    global fileNames
    if not name in fileNames :
       fileNames.append (name)
    return fileNames.index (name)

# --------------------------------------------------------------------------

def quoteString (s, quote = '"') :
    result = ""
    length = len (s)
    inx = 0
    for c in s :
       if c > ' ' and ord (c) < 127:
          if c == '\"' : # double quote
             result += "\\" + c
          elif c == '\''  :  # single quote
             result += "\\" + c
          elif c == '\\' : # backslash
             result += "\\" + c
          else :
             result += c
       elif ord (c) <= 255:
          if c == '\a' :   result += "\\a"
          elif c == '\b' : result += "\\b"
          elif c == '\f' : result += "\\f"
          elif c == '\n' : result += "\\n"
          elif c == '\r' : result += "\\r"
          elif c == '\t' : result += "\\t"
          elif c == '\v' : result += "\\v"
          elif c == '\0' and inx == length-1 :
             result += "\\0"
          else :
             result += "\\x" + "{:02x}".format (ord (c))
       else :
          result += "\\u" + "{:04x}".format (ord (c))
       inx = inx + 1
    return quote + result + quote

# --------------------------------------------------------------------------

class Input (object) :

   def __init__ (self) :
       self.support = None # editor support

   def openSupport (self, fileName) :
       if supportGenerator != None :
          self.support = supportGenerator.createSupport (self, fileName)

   # -----------------------------------------------------------------------

   # editor support

   def openRegion (self, obj) :
       if self.support != None :
          self.support.openRegion (obj)

   def closeRegion (self) :
       if self.support != None :
          self.support.closeRegion ()

   def openCompletion (self, obj, outside = False) :
       if self.support != None :
          self.support.openCompletion (obj, outside)

   def closeCompletion (self, obj, outside = False) :
       if self.support != None :
          self.support.closeCompletion (obj, outside)

   def selectColor (self, obj, defn = True, table = "") :
       if self.support != None :
          self.support.selectColor (obj, defn, table)

   def markDefn (self, obj) :
       if self.support != None :
          self.support.markDefn (obj)

   def markUsage (self, obj, ref_obj = None) :
       if self.support != None :
          self.support.markUsage (obj, ref_obj)

   def markText (self, obj, ink = None, paper = None, info = "", tooltip = "") :
       if self.support != None :
          self.support.markText (obj, ink, paper, info, tooltip)

   def markToken (self, ref_obj) :
       if self.support != None :
          self.support.markToken (ref_obj, self.tokenByteOfs, self.charByteOfs)

   def markOutline (self, obj) :
       if self.support != None :
          self.support.markOutline (obj)

   def setInk (self, ink, prev = False) :
       if self.support != None :
           self.support.setInk (ink, prev)

   def setPaper (self, paper, prev = False) :
       if self.support != None :
          self.support.setPaper (paper, prev)

   def addToolTip (self, tooltip, prev = False) :
       if self.support != None :
          self.support.addToolTip (tooltip, prev)

   # -----------------------------------------------------------------------

   def close (self) :
       pass

# --------------------------------------------------------------------------

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
