# pas_comp.py

from __future__ import print_function

from ev3pas_parser import *
from output import Output

from bytecodes_instr import *

from bytecodes_par import *
from encode import *
from cmdlib import *

# --------------------------------------------------------------------------

class Compiler (Parser) :
   def __init__ (self) :
       super (Compiler, self).__init__ ()

       self.support = None
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

   # procedure

   def open_proc (self, proc) :
       pass

   def on_proc (self, proc) :
       proc.item_name = proc.name
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

       self.size = 0
       self.real = False

       self.local = False
       self.const = False
       self.label = False

       self.position = 0
       self.register = False

# --------------------------------------------------------------------------

class Jump (object) :
   def __init__ (self) :
       self.source = 0
       self.target = 0
       self.size = 4
       self.location = None

# --------------------------------------------------------------------------

class Instructions (Output) :
   def __init__ (self) :
      super (Instructions, self).__init__ ()

      self.instr_table = { }
      for oc in OpCodes :
          self.instr_table [oc.cmd_txt] = oc

      self.module = None
      self.objects = [ ]

      self.lab_cnt = 0
      self.label_dict = { }
      self.jump_list = [ ]
      self.code = bytearray ([ ])

      self.show_hex = True
      self.short_jumps = True
      # self.short_jumps = False

   def error (self, text) :
       raise IOError (text)

   def location (self) :
       cursor = self.sections.cursor
       return (cursor.blockNumber (), cursor.columnNumber ())

   def goto (self, loc) :
       cursor = self.sections.cursor
       cursor.movePosition (cursor.Start)
       cursor.movePosition (cursor.NextBlock, cursor.MoveAnchor, loc [0])
       cursor.movePosition (cursor.NextCharacter, cursor.MoveAnchor, loc [1])

   def goto_end (self) :
       cursor = self.sections.cursor
       cursor.movePosition (cursor.End)

   def remove (self, cnt) :
       cursor = self.sections.cursor
       for k in range (cnt) :
           cursor.deleteChar ()

   def add_lines (self, cnt) :
       for i in range (cnt) :
           self.putEol ()

   def remove_lines (self, cnt) :
       if cnt > 0 :
          self.remove (cnt-1)

   # instructions

   def alloc_lab (self) :
       self.lab_cnt = self.lab_cnt + 1
       return "label_" + str (self.lab_cnt)

   def place_lab (self, label) :
       self.setInk ("orange")
       self.put (label)
       self.setInk (None)
       self.put (" :")
       self.putEol ()

       if not label.startswith ("label_") :
          self.error ("Invalid label name: " + label)
       inx = int (label [6:])
       self.label_dict [inx] = len (self.code)

   def update_labels (self) :
       for jump in self.jump_list :
           target = self.label_dict [jump.target]
           source = jump.source
           if jump.size == 2 :
              value = target-source-3
              if value < DATA8_MIN or value > DATA8_MAX :
                 self.error ("Relative jump too long")
              sequence = LC2 (value)
              self.code [source:source+3] = sequence # 3 bytes
           if jump.size == 4 :
              value = target-source-5
              sequence = LC4 (value)
              self.code [source:source+5] = sequence # 5 bytes
              # print ("at ", source, "place", value)

           if self.show_hex :
              loc = self.location ()
              self.goto (jump.location)
              self.remove (3 * len(sequence))
              self.setInk ("red")
              for n in sequence :
                 self.put (format (n, "02x"))
                 self.put (" ")
              self.goto (loc)

       # clear data for next procedure
       self.label_dict = { }
       self.jump_list = [ ]

   def put_item (self, item) :

       if item.label :
          if self.short_jumps :
             params = LC2 (0)
          else :
             params = LC4 (0)
          inx = item.position
          jump = Jump ()
          jump.source = len (self.code)
          jump.target = inx
          jump.size = len (params) - 1
          jump.location = self.location ()
          self.jump_list.append (jump)
       elif item.const :
          params = LC (int (item.position))
       elif item.local :
          params = LV (int (item.position))
       else :
          params = GV (int (item.position))

       self.code += params

       if self.show_hex :
          for n in params :
             self.put (format (n, "02x"))
             self.put (" ")

   def put_item_text (self, item) :

       if item.label :
          inx = item.position
          self.setInk ("orange")
          self.put ("label_" + str (inx))
          self.setInk (None)
       elif item.const :
          self.setInk ("cornflowerblue")
          self.put ("LC(")
          self.put (str (item.position))
          self.put (")")
          self.setInk (None)
       elif item.local :
          self.setInk ("lime")
          self.put ("LV(")
          self.put (str (item.position))
          self.put (")")
          self.setInk (None)
       else :
          self.setInk ("green")
          self.put ("GV(")
          self.put (str (item.position))
          self.put (")")
          self.setInk (None)
       if item.name != "" :
          self.setInk ("gray")
          self.put ("/*" + item.name + "*/")
          self.setInk (None)

   def put_instr (self, name, items) :

       if name not in self.instr_table :
          self.error ("Invalid instruction name: " + name)
       oc = self.instr_table [name]
       cmd = oc.cmd

       if self.show_hex :
          self.setInk ("gray")
          pos = len (self.code)
          self.put (format (pos, "04x"))
          self.put (" ")

          self.setInk ("peru")
          self.code.append (cmd)
          self.put (format (cmd, "02x"))
          self.put (" ")

       for item in items :
          self.put_item (item)

       self.setInk ("blue")
       self.put (name)
       self.setInk (None)

       first = True
       for item in items :
          if first :
             first = False
          else :
             self.put (",")
          self.put (" ")
          self.put_item_text (item)
       self.putEol ()

   def put_stat (self, name) :
       self.setInk ("gray")
       self.putLn ("/* " + name + " */")
       self.setInk (None)

   def put_note (self, text) :
       self.setInk ("plum")
       self.putLn ("/* " + text + " */")
       self.setInk (None)

   def put_bytes (self, text, code) :
       self.setInk ("red")
       self.put (text + ": ")
       self.setInk ("peru")
       for c in code :
          self.put (format (c, "02x"))
          self.put (" ")
       self.putEol ()
       self.setInk (None)

   # -----------------------------------------------------------------------

   def alloc_reg (self, size) :
       scope = self.display [-1]
       answer = Answer ()
       answer.size = size
       answer.real = False
       answer.const = False
       answer.local = True
       answer.position = scope.used_bytes
       scope.used_bytes = scope.used_bytes + size
       if scope.used_bytes > scope.local_bytes :
          scope.local_bytes = scope.used_bytes
       answer.register = True
       self.setInk ("mediumpurple")
       self.putLn ("/* register LV(" + str (answer.position) + ") */")
       # ", used_bytes = " + str (scope.used_bytes) + ", local_bytes = " + str (scope.local_bytes)
       self.setInk (None)
       return answer

   def remember_reg (self) :
       scope = self.display [-1]
       scope.reg_list.append (scope.used_bytes)
       pass

   def free_reg (self) :
       scope = self.display [-1]
       used = scope.reg_list [-1]
       scope.used_bytes = used
       scope.reg_list.pop ()
       pass

   def describe_var (self, var) :
       answer = Answer ()
       answer.name = getattr (var, "name", "")
       answer.size = var.size
       answer.real = False
       answer.const = False
       answer.local = not var.global_variable
       answer.position = var.position
       answer.register = False
       return answer

   def describe_const (self, value) :
       answer = Answer ()
       answer.size = 4
       answer.real = False
       answer.const = True
       answer.local = False
       answer.position = value
       answer.register = False
       return answer

   def lookup (self, name) :
       result = None
       inx = len (self.display) - 1
       while result == None and inx >= 0 :
          result = self.display [inx].item_dict.get (name)
          inx = inx - 1
       return result

   def code_instr (self, name, *args) :

       # print ("args", args)
       items = [ ]
       inx = 0
       for item in args :
           if isinstance (item, int) :
              value = item
              item = Answer ()
              item.const = True
              item.position = value

           elif isinstance (item, str) and item.startswith ("label_") :
              num = int (item [6:])
              item = Answer ()
              item.label = True
              item.position = num

           if not isinstance (item, Answer) :
              self.error ("Invalid parameter type")
           # print ("item", item)
           items.append (item)
           inx = inx + 1

       # print ("items", items)
       self.put_instr (name, items)

   def code_jump (self, name, *args) :
       self.code_instr (name, *args)

   # -----------------------------------------------------------------------

   def code_builtin (self, name, expr_list) :
       oc = self.instr_table [name]
       detail = None
       args = [ ]
       inx = 0
       sub_inx = 0
       for expr in expr_list :
           if detail == None :
              par = oc.params [inx]
              if par == PAR8 and oc.params [inx+1] == SUBP :
                 sub_key = oc.params [inx+2]
                 inx = inx + 2
                 if isinstance (expr.value, TIdentExpr) :
                    sub_name = expr.value.name.upper ()
                    for sc in SubCodes :
                        if sc.cmd_key == sub_key and sc.sub_code_txt == sub_name :
                           detail = sc
                           args.append (detail.sub_code)
              elif par == PAR8 or par == PAR16 or par == PAR32 :
                 answer = self.code_expr (expr.value)
                 args.append (answer)
              inx = inx + 1
           else :
              par = detail.sub_params [sub_inx]
              if par == PAR8 or par == PAR16 or par == PAR32 :
                 answer = self.code_expr (expr.value)
                 args.append (answer)
              sub_inx = sub_inx + 1
       self.code_instr (name, *args)

   # -----------------------------------------------------------------------

   def code_cond (self, expr, direction, label) :
       if isinstance (expr, TSubExpr) :
          expr = expr.value # expression inside parenthesis
       self.openSection (expr)
       done = False
       if isinstance (expr, TNotExpr) :
            self.put_note ("not, direction=" + str (direction))
            self.code_cond (expr.param, not direction, label)
            done = True
       elif isinstance (expr, TTermExpr) :
          if expr.fce == expr.AndExp :
             self.put_note ("and, direction=" + str (direction))
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
             self.put_note ("or, direction=" + str (direction))
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
            instr = ""
            if direction :
               if expr.fce == expr.EqExp :
                  instr = "JR_EQ32"
               elif expr.fce == expr.NeExp :
                  instr = "JR_NE32"
               elif expr.fce == expr.LtExp :
                  instr = "JR_LT32"
               elif expr.fce == expr.GtExp :
                  instr = "JR_GT32"
               elif expr.fce == expr.LeExp :
                  instr = "JR_LTEQ32"
               elif expr.fce == expr.GeExp :
                  instr = "JR_GTEQ32"
            else :
               if expr.fce == expr.EqExp :
                  instr = "JR_NE32"
               elif expr.fce == expr.NeExp :
                  instr = "JR_EQ32"
               elif expr.fce == expr.LtExp :
                  instr = "JR_GTEQ32"
               elif expr.fce == expr.GtExp :
                  instr = "JR_LTEQ32"
               elif expr.fce == expr.LeExp :
                  instr = "JR_GT32"
               elif expr.fce == expr.GeExp :
                  instr = "JR_LT32"
            if instr != "" :
               self.put_note ("compare, direction=" + str (direction))
               self.code_jump (instr, left, right, label)
               done = True
       if not done :
          self.put_note ("expression, direction=" + str (direction))
          answer = self.code_expr (expr)
          if direction :
             self.code_jump ("JR_TRUE", answer, label)
          else :
             self.code_jump ("JR_FALSE", answer, label)
       self.closeSection ()

   def code_arit (self, name, left, right) :
       if left.register :
          answer = left
       elif right.register :
          answer = right
       else :
          answer = self.alloc_reg (left.size)

       self.code_instr (name, left, right, answer)
       return answer

   def code_expr (self, expr) :
       answer = None
       self.openSection (expr)

       if isinstance (expr, TIdentExpr) :
          # self.put_note ("variable " + expr.name)
          var = self.lookup (expr.name) # !?
          answer = self.describe_var (var)

       elif isinstance (expr, TIntValueExpr) :
          # self.put_note ("integer constant " + str (expr.value))
          answer = self.describe_const (expr.value)

       elif isinstance (expr, TCallExpr) :
          if isinstance (expr.func, TIdentExpr) :
             name = expr.func.name
             name = name.upper ()
             if name in self.instr_table :
                self.code_builtin (name, expr.list.items)
             else :
                parameters = [ ]
                for param in expr.list.items :
                    value = self.code_expr (param.value)
                    parameters.append (value)
                function = self.describe_const (2) # !? first procedure
                count = self.describe_const (len (parameters))
                self.code_instr ("CALL", function, count, *parameters)

       elif isinstance (expr, TTermExpr) :
          left = self.code_expr (expr.left)
          right = self.code_expr (expr.right)
          if expr.fce == expr.MulExp :
             answer = self.code_arit ("MUL32", left, right)
          elif expr.fce == expr.DivExp :
             answer = self.code_arit ("DIV32", left, right)
          elif expr.fce == expr.AndExp :
             answer = self.code_cond (left, right)

       elif isinstance (expr, TSimpleExpr) :
          left = self.code_expr (expr.left)
          right = self.code_expr (expr.right)
          if expr.fce == expr.AddExp :
             answer = self.code_arit ("ADD32", left, right)
          elif expr.fce == expr.SubExp :
             answer = self.code_arit ("SUB32", left, right)
          elif expr.fce == expr.OrExp :
             answer = self.code_cond (left, right)

       elif isinstance (expr, TCompleteExpr) :
          left = self.code_expr (expr.left)
          right = self.code_expr (expr.right)
          instr = ""
          if expr.fce == expr.EqExp :
             instr = "CP_EQ32"
          elif expr.fce == expr.NeExp :
             instr = "CP_NE32"
          elif expr.fce == expr.LtExp :
             instr = "CP_LT32"
          elif expr.fce == expr.GtExp :
             instr = "CP_GT32"
          elif expr.fce == expr.LeExp :
             instr = "CP_LTE32"
          elif expr.fce == expr.GeExp :
             instr = "CP_GTE32"
          answer = self.code_arit (instr, left, right)

       if answer == None :
          answer = Answer ()
          answer.name = "unknown"

       self.closeSection ()
       return answer

   # -----------------------------------------------------------------------

   def code_stat (self, stat) :
       self.openSection (stat)
       self.remember_reg ()
       if isinstance (stat, TAssignStat) :
          self.put_stat ("assign")
          right = self.code_expr (stat.right_expr)
          left = self.code_expr (stat.left_expr)
          self.code_instr ("MOVE32_32", right, left)
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
             self.code_jump ("JR", lab_end)
             self.put_stat ("else")
             self.incIndent ()
             self.place_lab (lab_else)
             self.code_stat (stat.else_stat)
             self.place_lab (lab_end)
             self.decIndent ()
       elif isinstance (stat, TForStat) :
          self.put_stat ("for")
          lab_begin = self.alloc_lab ()
          lab_end = self.alloc_lab ()
          # initialize loop variable
          var = self.code_expr (stat.var_expr)
          init_value = self.code_expr (stat.from_expr)
          self.code_instr ("MOVE32_32", init_value, var)
          # store limit
          limit_value = self.code_expr (stat.to_expr)
          limit = self.alloc_reg (4)
          self.code_instr ("MOVE32_32", limit_value, limit)
          # begin of loop
          self.place_lab (lab_begin)
          # compare
          if stat.incr :
             instr = "JR_GT32"
          else :
             instr = "JR_LT32"
          self.code_jump (instr, var, limit, lab_end)
          # inner statement
          self.incIndent ()
          self.code_stat (stat.body_stat)
          self.decIndent ()
          # increment or decrement
          one = self.describe_const (1)
          if stat.incr :
             self.code_instr ("ADD32", var, one, var)
          else :
             self.code_instr ("ADD32", var, one, var)
          # end of loop
          self.code_jump ("JR", lab_begin)
          self.place_lab (lab_end)
       elif isinstance (stat, TWhileStat) :
          self.put_stat ("while")
          lab_begin = self.alloc_lab ()
          self.place_lab (lab_begin)
          lab_end = self.alloc_lab ()
          self.code_cond (stat.cond_expr, False, lab_end)
          self.incIndent ()
          self.code_stat (stat.body_stat)
          self.decIndent ()
          self.code_jump ("JR", lab_begin)
          self.place_lab (lab_end)
       elif isinstance (stat, TRepeatStat) :
          self.put_stat ("repeat")
          lab_begin = self.alloc_lab ()
          self.place_lab (lab_begin)
          self.incIndent ()
          self.code_stat (stat.body_stat)
          self.decIndent ()
          self.code_cond (stat.cond_expr, False, lab_begin)
       elif isinstance (stat, TBlockStat) :
          self.put_stat ("begin")
          self.incIndent ()
          for item in stat.body_seq.items :
              self.code_stat (item)
          self.decIndent ()
          self.put_stat ("end")
       self.free_reg ()
       self.closeSection ()

   # -----------------------------------------------------------------------

   def code_alloc (self, item, decl, scope) :
       size = 0
       type_name = ""
       if isinstance (decl.typ, TAliasType) :
          type_name = decl.typ.name
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

          if scope.global_scope :
             pos = scope.global_bytes
          else :
             pos = scope.local_bytes

          rem = pos % align
          if rem != 0 :
             pos = pos + align - rem

          item.size = size
          item.global_variable = scope.global_scope
          item.position = pos

          if scope.global_scope :
             scope.global_bytes = pos + size
          else :
             scope.used_bytes = pos + size
             scope.local_bytes = pos + size

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

   # -----------------------------------------------------------------------

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
       self.addDefinition (proc.item_name, "procedure " + proc.item_name)
       self.setInk (None)
       self.putEol ()
       self.incIndent ()

       proc.global_scope = False
       proc.used_bytes = 0
       proc.local_bytes = 0
       proc.reg_list = [ ]

       self.code = bytearray ([ ])
       proc.subroutine_cursor = self.location ()
       self.add_lines (4)

       self.display.append (proc)
       self.code_param_list (proc.param_list, proc)
       self.code_declarations (proc.local, proc)
       if proc.body != None :
          for stat in proc.body.items :
              self.code_stat (stat)
          self.code_instr ("RETURN")
          self.code_instr ("OBJECT_END")
       self.decIndent ()
       self.putLn ()
       self.display.pop ()
       self.closeSection ()

       self.update_labels ()
       proc.code = self.code # store generated code
       self.objects.append (proc) # store object
       self.code = bytearray ([ ])

   # -----------------------------------------------------------------------

   def code_main (self, module) :
       body = module.init
       if body != None :
          self.openSection (body)

       self.setInk ("orange")
       self.put ("proc ")
       self.put ("main")
       self.setInk (None)
       self.putEol ()
       self.incIndent ()

       self.code = bytearray ([ ])
       self.main_cursor = self.location ()
       self.add_lines (3)

       # lab = self.alloc_lab ()
       # self.place_lab (lab)

       if module.init != None :
          for stat in module.init.items :
              self.code_stat (stat)

       # self.code_instr ("JR", lab)

       self.code_instr ("OBJECT_END")

       self.update_labels ()
       module.code = self.code
       self.code = bytearray ([ ])

       self.decIndent ()
       self.putLn ()

       if body != None :
          self.closeSection ()

   def code_module_decl (self, module) :

       self.openSection (module)
       self.module_cursor = self.location ()
       self.add_lines (5)
       module.global_scope = True
       module.global_bytes = 0
       module.used_bytes = 0
       module.local_bytes = 0
       module.reg_list = [ ]
       self.display = [module]
       self.code_declarations (module.impl_decl, module)
       self.code_main (module)
       self.display.pop ()
       self.closeSection ()

       # program header
       version = 0
       self.program = PROGRAMHeader (version, 1 + len (self.objects), module.global_bytes)

       pos = len (self.program) + 12 + 12 * len (self.objects) # position for first instruction

       # main function header
       header = VMTHREADHeader (pos, module.local_bytes)
       self.program += header
       module.first_instr = pos
       pos += len (module.code)

       self.goto (self.main_cursor)
       self.remove_lines (3)
       self.put_bytes ("offset to instruction", header [0:4])
       self.put_bytes ("object id / trigger count", header [4:8])
       self.put_bytes ("local bytes", header [8:12])
       self.goto_end ()

       # procedure headers
       for obj in self.objects :
          parameters = bytearray ([ ])
          cnt = 0
          for decl in obj.param_list.items :
              for item in decl.items :
                  parameters.append (IN_32)
                  cnt = cnt + 1
          parameters = ByteToBytes (cnt) + parameters
          obj.code = parameters + obj.code

          header = SUBCALLHeader (pos, obj.local_bytes)
          self.program += header
          obj.first_instr = pos
          pos += len (obj.code)

          self.goto (obj.subroutine_cursor)
          self.remove_lines (4)
          self.put_bytes ("offset to instruction", header [0:4])
          self.put_bytes ("object id / trigger count", header [4:8])
          self.put_bytes ("local bytes", header [8:12])
          self.put_bytes ("parameters", parameters)
          self.goto_end ()

       # main function instructions
       if len (self.program) != module.first_instr :
          self.error ("Bad position of main fuction")
       self.program += module.code

       # procedure instructions
       for obj in self.objects :
          if len (self.program) != obj.first_instr :
             self.error ("Bad procedure position")
          self.program += obj.code

       if len (self.program) != pos :
          self.error ("Bad program size")

       # update program size
       self.program [4:8] = LongToBytes (len (self.program))

       self.goto (self.module_cursor)
       self.remove_lines (5)
       self.put_bytes ("header", self.program [0:4])
       self.put_bytes ("program size", self.program [4:8])
       self.put_bytes ("bytecode version", self.program [8:10])
       self.put_bytes ("number of objects", self.program [10:12])
       self.put_bytes ("global bytes", self.program [12:16])
       self.goto_end ()

       # print Program
       self.setInk ("peru")
       n = 0
       for c in self.program :
          self.put (format (c, "02x") + " ")
          print (format (c, "02x"), end=" ")
          n = n + 1
          if n % 16 == 0 :
             self.putLn ()
             print ()
          elif n % 4 == 0 :
             self.put ("| ")
             print ("|", end=" ")
       self.putEol ()
       self.setInk (None)
       print ()

       prog_list = self.program
       if 0 :
          connectToEV3 ()
          print ("battery info:", batteryInfo ())
          deleteFile ("../prjs/test/test.rbf")
          writeFile ("../prjs/test/test.rbf", prog_list)
          listFiles ("../prjs/test")
          runFile ("../prjs/test/test.rbf")
          print ("======")
          time.sleep (5)
          print ("======")
          # stopProgram ()
          Off (15)

# --------------------------------------------------------------------------

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
