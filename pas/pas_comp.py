# pas_comp.py

from __future__ import print_function

from pas_parser import *
from output import Output

# --------------------------------------------------------------------------

class Compiler (Parser) :
   def __init__ (self) :
       super (Compiler, self).__init__ ()

       self.current_type = None

       self.global_scope = TModule () # !?
       self.global_scope.item_name = ""
       self.global_scope.item_qual = ""
       self.global_scope.item_dict = { }
       self.global_scope.item_list = [ ]
       self.display = [ self.global_scope ]

   # scope

   def setupName (self, item) :
       # if len (self.display) == 0 :
       #    item.item_qual = item.item_name
       # else :
          top = self.display [-1]
          if top.item_qual == "" :
             item.item_qual = item.item_name
          else :
             item.item_qual = top.item_qual + "." + item.item_name

   def enter (self, item) :
       # if len (self.display) == 0 :
       #    self.display.append (item)
       # else :
          top = self.display [-1]
          top.item_dict [item.item_name] = item
          top.item_list.append (item)
          item.item_context = top

   def openScope (self, item) :
       if not hasattr (item, "item_dict") :
          item.item_dict = { }
          item.item_list = [ ]
       if not hasattr (item, "item_qual") :
          item.item_qual = ""
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

   # module

   def open_module (self, module) :
       self.module = module

   def on_module (self, module) :
       module.item_name = module.name
       module.item_expand = True
       module.item_icon = "module"
       self.setupName (module)
       self.enter (module)
       self.markDefn (module)
       self.markOutline (module)
       self.openScope (module)
       self.openCompletion (module, outside = True)

   def on_import (self, param) :
       # param.item_name = param.name
       # self.markUsage (param)
       pass

   def close_module (self, module) :
       self.closeCompletion (module, outside = True)
       self.closeScope ()

   # class

   def open_class (self, cls) :
       self.named_type (cls)
       cls.item_expand = True
       cls.item_icon = "class"
       self.setupName (cls)
       self.markOutline (cls) # next/prev function/class
       self.openRegion (cls) # region with background color
       self.openScope (cls) # scope for identifiers
       self.openCompletion (cls, outside = True) # mark for text completion

   def close_class (self, cls) :
       self.closeCompletion (cls, outside = True)
       self.closeScope ()
       self.closeRegion ()

   def on_field (self, field) :
       field.item_name = field.name
       self.setupName (field)
       self.markDefn (field)

   def add_field (self, fields) :
       for field in fields.items :
          self.enter (field)

   # interface

   def open_interface (self, ifc) :
       ifc.item_name = ifc.name
       self.named_type (ifc)
       self.setupName (ifc)
       self.openRegion (ifc)
       self.openScope (ifc)
       self.markOutline (ifc)
       self.openCompletion (ifc, outside = True)

   def close_interface (self, ifc) :
       self.closeCompletion (ifc, outside = True)
       self.closeScope ()
       self.closeRegion ()

   # procedure

   def open_proc (self, proc) :
       pass

   def on_proc (self, proc) :
       if len (proc.proc_name.items) == 0 :
          proc.item_name = proc.proc_name.id
       else :
          proc.item_name = proc.proc_name.items[-1].id
       proc.item_icon = "function"
       self.setupName (proc)
       self.enter (proc)
       self.markDefn (proc)
       self.markOutline (proc)
       self.openRegion (proc)
       self.openScope (proc)
       self.openCompletion (proc, outside = True)

   def on_param (self, param) :
       param.item_name = param.name
       self.setupName (param)
       self.markDefn (param)

   def add_param (self, params) :
       for param in params.items :
           self.enter (param)

   def on_begin_proc (self, proc) :
       self.setInk ("lime")
       self.addToolTip ("begin of procedure " + proc.item_name)
       pass

   def on_end_proc (self, proc) :
       self.setInk ("red")
       self.addToolTip ("end of procedure " + proc.item_name)
       pass

   def on_tail_proc (self, proc) :
       pass

   def close_proc (self, proc) :
       self.closeCompletion (proc, outside = True)
       self.closeScope ()
       self.closeRegion ()

   # constant declarations

   def on_const (self, const) :
       const.item_name = const.name
       self.setupName (const)
       self.markDefn (const)

   def add_const (self, const) :
       self.enter (const)

   # type declarations

   def on_type (self, type) :
       type.item_name = type.name
       self.current_type = type
       self.setupName (type)
       self.markDefn (type)

   def add_type (self, type) :
       self.enter (type)

   def simple_type (self, type) :
       self.current_type = None

   def named_type (self, type) :
       if self.current_type == None :
          self.error ("Class or interface without identifier")
       else :
          self.current_type.item_obj = type
          type.item_name = self.current_type.name
          self.current_type = None # value for nested types

   # variable declarations

   def on_var (self, var) :
       var.item_name = var.name
       var.item_icon = "variable"
       self.setupName (var)
       self.markDefn (var)

   def add_var (self, variables) :
       for var in variables.items :
           self.enter (var)

   # expressions

   def on_ident_expr (self, expr) :
       expr.item_decl = self.lookup (expr.name)
       if expr.item_decl != None :
          expr.item_qual = expr.item_decl.item_qual
       self.markUsage (expr)

   def on_field_expr (self, expr) :
       # expr.item_qual = self.lookup (expr.name) # !?
       # self.markUsage (expr)
       pass

# --------------------------------------------------------------------------

class Answer (object) :
   def __init__ (self) :
       self.name = ""
       self.type = ""

# --------------------------------------------------------------------------

class Instructions (Output) :
   def __init__ (self) :
      super (Instructions, self).__init__ ()
      self.module = None
      self.lab_cnt = 0
      self.reg_cnt = 0

   # instructions

   def alloc_lab (self) :
       self.lab_cnt = self.lab_cnt + 1
       return "label_" + str (self.lab_cnt)

   def place_lab (self, label) :
       self.setInk ("peru")
       self.put (label)
       self.setInk (None)
       self.put (" :")
       self.putEol ()

   def jump (self, name, label) :
       self.setInk ("blue")
       self.put (name)
       self.setInk (None)
       self.put (" ")
       self.setInk ("peru")
       self.put (label)
       self.setInk (None)
       self.putEol ()

   def alloc_reg (self) :
       self.reg_cnt = self.reg_cnt + 1
       return "R" + str (self.reg_cnt)

   def free_reg (self) :
       self.reg_cnt = self.reg_cnt - 1

   def put_item (self, answer) :
       if answer.name.startswith ("R") : # !?
          self.setInk ("lime")
          self.put (answer.name)
          self.setInk (None)
       else :
          self.setInk ("limegreen")
          self.addUsage (answer.name, answer.name)
          self.setInk (None)

   def put_instr (self, name, *arg) :
       self.setInk ("blue")
       self.put (name)
       self.setInk (None)
       first = True
       for item in arg :
          if first :
             first = False
          else :
             self.put (",")
          self.put (" ")
          if isinstance (item, Answer) :
             self.put_item (item)
          else :
             self.put (item)
       self.putEol ()

   def put_stat (self, name) :
       self.setInk ("gray")
       self.putLn ("/* " + name + " */")
       self.setInk (None)

   def code_cond (self, expr, direction, label) :
       self.openSection (expr)
       done = False
       if isinstance (expr, TNotExpr) :
            self.code_cond (expr.param, not direction, label)
            done = True
       elif isinstance (expr, TTermExpr) :
          if expr.fce == expr.AndExp :
             if direction == True :
                temp_lab = self.alloc_lab ()
                self.code_cond (expr.left, False, temp_lab)
                self.code_cond (expr.right, True, label)
                self.place_lab (temp_lab)
             else :
                self.code_cond (expr.left, False, label)
                self.code_cond (expr.right, False, label)
             done = True
       elif isinstance (expr, TSimpleExpr) :
          if expr.fce == expr.OrExp :
             if direction == True :
                self.code_cond (expr.left, True, label)
                self.code_cond (expr.right, True, label)
             else :
                temp_lab = self.alloc_lab ()
                self.code_cond (expr.left, True, temp_lab)
                self.code_cond (expr.right, False, label)
                self.place_lab (temp_lab)
             done = True
       elif isinstance (expr, TCompleteExpr) :
            left = self.code_expr (expr.left)
            right = self.code_expr (expr.right)
            self.put_instr ("cmp", left, right)
            if direction :
               self.jump ("JT", label)
            else :
               self.jump ("JF", label)
            done = True
       if not done :
          answer = self.code_expr (expr)
          self.put_instr ("cmp", answer, "1")
          if direction :
             self.jump ("JT", label)
          else :
             self.jump ("JF", label)
       self.closeSection ()

   def code_instr (self, name, left, right) :
       answer = Answer ()
       answer.name = self.alloc_reg ()
       self.put_instr (name, left, right, answer)
       return answer

   def code_expr (self, expr) :
       answer = None
       self.openSection (expr)

       if isinstance (expr, TIdentExpr) :
          answer = Answer ()
          answer.name = expr.name

       elif isinstance (expr, TIntValueExpr) :
          answer = Answer ()
          answer.name = self.alloc_reg ()
          self.put_instr ("mov", expr.value, answer)

       elif isinstance (expr, TTermExpr) :
          left = self.code_expr (expr.left)
          right = self.code_expr (expr.right)
          if expr.fce == expr.MulExp :
             answer = self.code_instr ("mul", left, right)
          elif expr.fce == expr.AndExp :
             answer = self.code_cond (left, right)

       elif isinstance (expr, TSimpleExpr) :
          left = self.code_expr (expr.left)
          right = self.code_expr (expr.right)
          if expr.fce == expr.AddExp :
             answer = self.code_instr ("add", left, right)
          elif expr.fce == expr.SubExp :
             answer = self.code_instr ("sub", left, right)
          elif expr.fce == expr.OrExp :
             answer = self.code_cond (left, right)

       elif isinstance (expr, TCompleteExpr) :
          left = self.code_expr (expr.left)
          right = self.code_expr (expr.right)
          answer = self.code_instr ("cmp", left, right)

       if answer == None :
          answer = Answer ()
          answer.name = "unknown"

       self.closeSection ()
       return answer

   def code_stat (self, stat) :
       self.openSection (stat)
       if isinstance (stat, TAssignStat) :
          self.put_stat ("assign")
          self.code_expr (stat.right_expr)
          self.code_expr (stat.left_expr)
       elif isinstance (stat, TCallStat) :
          self.put_stat ("call")
          self.code_expr (stat.call_expr)
       elif isinstance (stat, TIfStat) :
          self.put_stat ("if")
          lab_else = self.alloc_lab ()
          self.code_cond (stat.cond_expr, False, lab_else)
          self.incIndent ()
          self.code_stat (stat.then_stat)
          self.decIndent ()
          if stat.else_stat == None :
             self.place_lab (lab_else)
          else :
             lab_end = self.alloc_lab ()
             self.jump ("JMP", lab_end)
             self.put_stat ("else")
             self.incIndent ()
             self.place_lab (lab_else)
             self.code_stat (stat.else_stat)
             self.place_lab (lab_end)
             self.decIndent ()
       elif isinstance (stat, TWhileStat) :
          self.put_stat ("while")
          lab_begin = self.alloc_lab ()
          self.place_lab (lab_begin)
          lab_end = self.alloc_lab ()
          self.code_cond (stat.cond_expr, False, lab_end)
          self.incIndent ()
          self.code_stat (stat.body_stat)
          self.decIndent ()
          self.jump ("JMP", lab_begin)
          self.place_lab (lab_end)
       elif isinstance (stat, TBlockStat) :
          self.put_stat ("begin")
          self.incIndent ()
          for item in stat.body_seq.items :
              self.code_stat (item)
          self.decIndent ()
          self.put_stat ("end")
       self.closeSection ()

   def code_alloc (self, item, decl, scope) :
       size = 0
       type_name = ""
       if isinstance (decl.typ, TAliasType) :
          if len (decl.typ.alias_name.items) == 0 :
             type_name = decl.typ.alias_name.id
       elif isinstance (decl.typ, TStringType) :
             type_name = "string"
       if type_name == "integer" :
          size = 4
       if type_name == "shortint" :
          size = 2
       if type_name == "byteint" or type_name == "char" or type_name == "boolean" :
          size = 1
       if type_name == "real" :
          size = 4
       if type_name == "string" :
          size = 4
       if size != 0 :
          align = size
          if align > 4 :
             align = 4
          rem = scope.allocated_bytes % align
          if rem != 0 :
             scope.allocated_bytes = scope.allocated_bytes + align - rem

          item.size = size
          item.global_variable = scope.global_scope
          item.position = scope.allocated_bytes
          scope.allocated_bytes = scope.allocated_bytes + size
          self.put (", " + str (item.size) + " bytes")
          self.put (", position " + str (item.position))

   def code_var_decl (self, decl, scope) :
       for item in decl.items :
          self.setInk ("green")
          self.put ("var "  + item.name)
          self.code_alloc (item, decl, scope)
          self.setInk ("None")
          self.putLn ()

   def code_decl (self, decl, scope) :
       if isinstance (decl, TConstSect) :
          # self.code_const_sect (decl)
          pass
       elif isinstance (decl, TTypeSect) :
          # self.code_type_sect (decl)
          pass
       elif isinstance (decl, TVarSect) :
          for item in decl.items :
              self.code_var_decl (item, scope)
       elif isinstance (decl, TProcDecl) :
          self.code_proc (decl)

   def code_declarations (self, declarations, scope) :
       for decl in declarations.items :
           self.code_decl (decl, scope)

   def code_param_list (self, parameters, scope) :
       for decl in parameters.items :
           for item in decl.items :
              self.setInk ("red")
              self.put ("param "  + item.name)
              self.code_alloc (item, decl, scope)
              self.setInk ("None")
              self.putLn ()

   def code_proc (self, proc) :
       self.openSection (proc)
       self.setInk ("orange")
       self.put ("proc ")
       self.setInk ("cornflowerblue")
       self.addToolTip (proc.item_name, "procedure " + proc.item_name)
       self.addDefinition (proc.item_name, "procedure " + proc.item_name)
       self.setInk (None)
       self.putEol ()
       self.incIndent ()
       proc.global_scope = False
       proc.allocated_bytes = 0
       self.code_param_list (proc.param_list, proc)
       self.code_declarations (proc.local, proc)
       if proc.body != None :
          for stat in proc.body.items :
              self.code_stat (stat)
       self.decIndent ()
       self.putLn ()
       self.closeSection ()

   def code_main (self, body) :
       self.openSection (body)
       self.setInk ("orange")
       self.put ("proc ")
       self.put ("main")
       self.setInk (None)
       self.putEol ()
       self.incIndent ()
       for stat in body.items :
              self.code_stat (stat)
       self.decIndent ()
       self.putLn ()
       self.closeSection ()

   def code_module_decl (self, module) :
       self.openSection (module)
       module.global_scope = True
       module.allocated_bytes = 0
       self.code_declarations (module.impl_decl, module)
       if module.init != None :
          self.code_main (module.init)
       self.closeSection ()

# --------------------------------------------------------------------------

if __name__ == "__main__" :

   # PYTHONPATH=directory_with_generated_parser python pas_comp.py

   parser = Compiler ()
   parser.pascal = True
   parser.openFile ("../examples/example.pas")

   result = parser.parse_module_decl ()
   parser.code_module_decl (result)

# --------------------------------------------------------------------------

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
