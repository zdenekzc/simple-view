
# cecko4_compiler.py

from __future__ import print_function

from cecko4_parser import *

# --------------------------------------------------------------------------

class Compiler (Parser) :

   def __init__ (self) :
       super (Compiler, self).__init__ ()
       self.display = [ ]

   # initialization

   def on_start_program (self, decl_list) :
       decl_list.item_name = ""
       decl_list.item_qual = ""
       decl_list.item_dict = { }
       decl_list.item_list = [ ]
       self.display.append (decl_list)

   # scope

   def enter (self, item) :
       top = self.display [-1]
       top.item_dict [item.item_name] = item
       top.item_list.append (item)
       item.item_context = top
       if top.item_qual == "" :
          item.item_qual = item.item_name
       else :
          item.item_qual = top.item_qual + "." + item.item_name

   def openScope (self, item) :
       if not hasattr (item, "item_dict") :
          item.item_dict = { }
       if not hasattr (item, "item_list") :
          item.item_list = [ ]
       self.display.append (item)

   def closeScope (self) :
       self.display.pop ()

   def lookup (self, name) :
       result = None
       inx = len (self.display) - 1
       while result == None and inx >= 0 :
          result = self.display [inx].item_dict.get (name)
          inx = inx - 1
       return result

   def copy_location (self, obj) :
       obj.src_file = self.prevFileInx
       obj.src_line = self.prevLineNum
       obj.src_column = self.prevColNum
       obj.src_pos = self.prevByteOfs
       obj.src_end = self.prevEndOfs

   # enumeration type

   def open_enum (self, cls) :
       cls.item_name = cls.name
       cls.item_expand = True
       cls.item_icon = "enum"
       self.enter (cls) # add declaration into current scope
       self.selectColor (cls)
       self.markDefn (cls) # mark as definition (in editor)

       self.openScope (cls) # open scope for identifiers
       self.openCompletion (cls, outside = True) # area with text completion

   def close_enum (self, cls) :
       self.closeCompletion (cls, outside = True)
       self.closeScope ()

   def on_enum_item (self, decl) :
       decl.item_name = decl.name
       decl.item_icon = "variable"
       self.copy_location (decl)
       self.enter (decl)
       self.selectColor (decl)
       self.markDefn (decl)

   # simple declaration

   def on_simple_decl (self, decl) :
       decl.item_name = decl.name
       decl.item_icon = "variable"
       self.copy_location (decl)
       self.enter (decl)
       self.selectColor (decl)
       self.markDefn (decl)

   def on_local_decl (self, decl) :
       self.on_simple_decl (decl)

   def open_parameters (self, decl) :
       self.openScope (decl)

   def on_param_decl (self, decl) :
       self.on_simple_decl (decl)

   def close_parameters (self, decl) :
       self.closeScope ()

   def open_function (self, decl) :
       decl.item_icon = "function"
       self.openScope (decl)
       self.openCompletion (decl, outside = True)

   def close_function (self, decl) :
       self.closeCompletion (decl, outside = True)
       self.closeScope ()

   # expression

   def on_variable_expr (self, expr) :
       expr.item_name = expr.name
       # print ("ident_expr", expr.item_name)
       expr.item_decl = self.lookup (expr.item_name)
       if expr.item_decl != None :
          expr.item_qual = expr.item_decl.item_qual
       self.markUsage (expr, expr.item_decl)

# --------------------------------------------------------------------------

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
