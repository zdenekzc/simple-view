# cecko4_instr.py

from __future__ import print_function

from input import indexToFileName
from lexer import LexerException
from cecko4_parser import *
from output import Output

from bytecodes_instr import *
from bytecodes_par import *
from encode import *
# from cmdlib import *

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

      self.report_fileInx = 0
      self.report_lineNum = 0
      self.report_colNum = 0

   def error (self, text) :
       raise IOError (indexToFileName (self.report_fileInx) + ":" +
                       str (self.report_lineNum) + ":" +
                       str (self.report_colNum) + ":" +
                       " error: " + text )

   def updatePosition (self, item) :
       "set position for error reporting"
       self.report_fileInx = item.src_file
       self.report_lineNum = item.src_line
       self.report_colNum = item.src_column
       self.report_byteOfs = item.src_pos

   # text manipulation

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
                 if isinstance (expr, CmmVarExpr) :
                    sub_name = expr.name
                    for sc in SubCodes :
                        if sc.cmd_key == sub_key and sc.sub_code_txt == sub_name :
                           detail = sc
                           args.append (detail.sub_code)
              elif par == PAR8 or par == PAR16 or par == PAR32 :
                 answer = self.code_expr (expr)
                 args.append (answer)
              inx = inx + 1
           else :
              par = detail.sub_params [sub_inx]
              if par == PAR8 or par == PAR16 or par == PAR32 :
                 answer = self.code_expr (expr)
                 args.append (answer)
              sub_inx = sub_inx + 1
       self.code_instr (name, *args)

   # -----------------------------------------------------------------------

   def code_cond (self, expr, direction, label) :
       self.updatePosition (expr)
       self.openSection (expr)
       done = False
       if expr.kind == expr.subexprExp :
          self.code_cond (expr.inner_expr, direction, label) # expression inside parenthesis
          done = True
       elif expr.kind == expr.logNotExp :
            self.put_note ("not, direction=" + str (direction))
            self.code_cond (expr.param, not direction, label)
            done = True
       elif expr.kind == expr.logAndExp :
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
       elif expr.kind == expr.logOrExp :
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
       elif isinstance (expr, CmmRelExpr) or isinstance (expr, CmmEqExpr) :
            left = self.code_expr (expr.left)
            right = self.code_expr (expr.right)
            instr = ""
            if direction :
               if expr.kind == expr.eqExp :
                  instr = "JR_EQ32"
               elif expr.kind == expr.neExp :
                  instr = "JR_NE32"
               elif expr.kind == expr.ltExp :
                  instr = "JR_LT32"
               elif expr.kind == expr.gtExp :
                  instr = "JR_GT32"
               elif expr.kind == expr.leExp :
                  instr = "JR_LTEQ32"
               elif expr.kind == expr.geExp :
                  instr = "JR_GTEQ32"
            else :
               if expr.kind == expr.eqExp :
                  instr = "JR_NE32"
               elif expr.kind == expr.neExp :
                  instr = "JR_EQ32"
               elif expr.kind == expr.ltExp :
                  instr = "JR_GTEQ32"
               elif expr.kind == expr.gtExp :
                  instr = "JR_LTEQ32"
               elif expr.kind == expr.leExp :
                  instr = "JR_GT32"
               elif expr.kind == expr.geExp :
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
       self.updatePosition (expr)
       answer = None
       done = False
       self.openSection (expr)

       if expr.kind == expr.varExp :
          name = expr.name
          # self.put_note ("variable " + name)
          var = self.lookup (name) # !?
          if var == None :
             self.error ("Unknown variable: " + name)
          answer = self.describe_var (var)

       elif expr.kind == expr.intValueExp :
          # self.put_note ("integer constant " + str (expr.value))
          answer = self.describe_const (expr.value)

       elif expr.kind == expr.subexprExp :
          answer = self.code_expr (expr.inner_expr)

       elif expr.kind == expr.assignExp :
          right = self.code_expr (expr.right)
          left = self.code_expr (expr.left)
          self.code_instr ("MOVE32_32", right, left)
          done = True

       elif expr.kind == expr.callExp :
          if expr.left.kind == expr.varExp :
             name = expr.left.name
             if name in self.instr_table :
                self.code_builtin (name, expr.param_list.items)
                done = True
             else :
                parameters = [ ]
                for param in expr.param_list.items :
                    value = self.code_expr (param)
                    parameters.append (value)
                function = self.describe_const (2) # !? first procedure
                count = self.describe_const (len (parameters))
                self.code_instr ("CALL", function, count, *parameters)
                done = True

       elif expr.kind == expr.incExp or expr.kind == expr.decExp :
          left = self.code_expr (expr.param)
          one = self.describe_const (1)
          instr = ""
          if expr.kind == expr.incExp :
             instr = "ADD32"
          elif expr.kind == expr.decExp :
             instr = "SUB32"
          self.code_instr (instr, left, one, left)
          answer = left
          done = True

       elif expr.kind == expr.postIncExp or expr.kind == expr.postDecExp :
          left = self.code_expr (expr.left)
          one = self.describe_const (1)
          answer = self.alloc_reg (left.size)
          self.code_instr ("MOVE32_32", left, answer)
          instr = ""
          if expr.kind == expr.postIncExp :
             instr = "ADD32"
          elif expr.kind == expr.postDecExp :
             instr = "SUB32"
          self.code_instr (instr, left, one, left)

       elif isinstance (expr, CmmMulExpr) :
          left = self.code_expr (expr.left)
          right = self.code_expr (expr.right)
          instr = "??"
          if expr.kind == expr.mulExp :
             instr = "MUL32"
          elif expr.kind == expr.divExp :
             instr = "DIV32"
          answer = self.code_arit (instr, left, right)

       elif isinstance (expr, CmmAddExpr) :
          left = self.code_expr (expr.left)
          right = self.code_expr (expr.right)
          instr = ""
          if expr.kind == expr.addExp :
             instr = "ADD32"
          elif expr.kind == expr.subExp :
             instr = "SUB32"
          answer = self.code_arit (instr, left, right)

       elif expr.kind == expr.logAndExp :
          answer = self.code_cond (left, right)

       elif expr.kind == expr.logOrExp :
          answer = self.code_cond (left, right)

       elif isinstance (expr, CmmRelExpr) or isinstance (expr, CmmEqExpr) :
          left = self.code_expr (expr.left)
          right = self.code_expr (expr.right)
          instr = ""
          if expr.kind == expr.eqExp :
             instr = "CP_EQ32"
          elif expr.kind == expr.neExp :
             instr = "CP_NE32"
          elif expr.kind == expr.ltExp :
             instr = "CP_LT32"
          elif expr.kind == expr.gtExp :
             instr = "CP_GT32"
          elif expr.kind == expr.leExp :
             instr = "CP_LTEQ32"
          elif expr.kind == expr.geExp :
             instr = "CP_GTEQ32"
          answer = self.code_arit (instr, left, right)

       if answer == None and not done:
          self.error ("Not implemented")

       if answer == None :
          answer = Answer ()
          answer.name = "unknown"

       self.closeSection ()
       return answer

   # -----------------------------------------------------------------------

   def code_stat (self, stat) :
       self.updatePosition (stat)
       self.openSection (stat)
       if isinstance (stat, CmmSimpleStat) :
          self.put_stat ("simple statement")
          expr = stat.inner_expr
          self.remember_reg ()
          self.code_expr (expr)
          self.free_reg ()
       elif isinstance (stat, CmmIfStat) :
          self.put_stat ("if")
          lab_else = self.alloc_lab ()
          self.code_cond (stat.cond, False, lab_else)
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
       elif isinstance (stat, CmmForStat) :
          self.put_stat ("for")
          lab_begin = self.alloc_lab ()
          lab_end = self.alloc_lab ()
          # initialize loop variable
          if stat.from_expr != None :
             self.code_expr (stat.from_expr)
          # begin of loop
          self.place_lab (lab_begin)
          # compare
          if stat.cond_expr != None :
             self.code_cond (stat.cond_expr, False, lab_end)
          # inner statement
          self.incIndent ()
          self.code_stat (stat.body_stat)
          self.decIndent ()
          # increment or decrement
          self.put_stat ("end of for")
          if stat.step_expr != None :
             self.code_expr (stat.step_expr)
          # end of loop
          self.code_jump ("JR", lab_begin)
          self.place_lab (lab_end)
       elif isinstance (stat, CmmWhileStat) :
          self.put_stat ("while")
          lab_begin = self.alloc_lab ()
          self.place_lab (lab_begin)
          lab_end = self.alloc_lab ()
          self.code_cond (stat.cond, False, lab_end)
          self.incIndent ()
          self.code_stat (stat.body_stat)
          self.decIndent ()
          self.put_stat ("end of while")
          self.code_jump ("JR", lab_begin)
          self.place_lab (lab_end)
       elif isinstance (stat, CmmCompoundStat) :
          self.put_stat ("{")
          self.incIndent ()
          for item in stat.items :
              self.code_stat (item)
          self.decIndent ()
          self.put_stat ("}")
       elif isinstance (stat, CmmDeclStat) :
          self.code_local_declaration (stat)
       else :
          self.error ("Statement not implemented")
       self.closeSection ()

   # -----------------------------------------------------------------------

   def code_alloc (self, decl, scope, global_alloc) :
       size = 0

       if decl.type == "int" :
          size = 4
       if decl.type == "short" :
          size = 2
       if decl.type == "char" or decl.type == "bool" :
          size = 1
       if decl.type == "float" :
          size = 4
       if decl.type == "string" :
          size = 4

       if size == 0:
          self.error ("Type not implemented")

       if size != 0 :
          align = size
          if align > 4 :
             align = 4

          if global_alloc :
             pos = scope.global_bytes
          else :
             pos = scope.local_bytes

          rem = pos % align
          if rem != 0 :
             pos = pos + align - rem

          decl.size = size
          decl.global_variable = global_alloc
          decl.position = pos

          if global_alloc :
             scope.global_bytes = pos + size
          else :
             scope.used_bytes = pos + size
             scope.local_bytes = pos + size

          self.put (", " + str (decl.size) + " bytes")
          self.put (", position " + str (decl.position))

   def code_variable (self, decl, scope, global_alloc) :
       self.updatePosition (decl)
       self.setInk ("green")
       self.put ("var "  + decl.name)
       self.code_alloc (decl, scope, global_alloc)
       self.setInk ("None")
       self.putLn ()

   def code_local_declaration (self, decl) :
       scope = self.display [-1] # local scope
       self.code_variable (decl, scope, global_alloc = False)

   def code_global_variable (self, decl) :
       scope = self.display [0] # global scope
       self.code_variable (decl, scope, global_alloc = True)

   # -----------------------------------------------------------------------

   def code_param_list (self, parameters, scope) :
       for decl in parameters.items :
           self.setInk ("red")
           self.put ("param "  + decl.name)
           self.code_alloc (decl, scope, global_alloc = False)
           self.setInk ("None")
           self.putLn ()

   def code_function (self, proc, is_main = False) :
       self.updatePosition (proc)

       self.openSection (proc)
       self.setInk ("orange")
       self.put ("proc ")
       self.setInk ("cornflowerblue")
       self.addDefinition (proc.name, "function " + proc.name)
       self.setInk (None)
       self.putEol ()
       self.incIndent ()

       proc.used_bytes = 0
       proc.local_bytes = 0
       proc.reg_list = [ ]

       self.code = bytearray ([ ])
       proc.subroutine_cursor = self.location ()
       if is_main :
          self.add_lines (3)
       else :
          self.add_lines (4)

       self.display.append (proc)
       if not is_main :
          self.code_param_list (proc.param_list, proc)

       for stat in proc.body.items :
           self.code_stat (stat)
       if not is_main :
          self.code_instr ("RETURN")
       self.code_instr ("OBJECT_END")

       self.decIndent ()
       self.putLn ()
       self.display.pop ()
       self.closeSection ()

       self.update_labels ()
       proc.code = self.code # store generated code
       if is_main :
          self.main_code = proc.code
       if not is_main :
          self.objects.append (proc) # store object
       self.code = bytearray ([ ])

# -----------------------------------------------------------------------

   def code_declarations (self, declarations) :
       self.main_func = None
       for decl in declarations.items :
          if decl.body == None :
             self.code_global_variable (decl)
          else :
             is_main = (decl.name == "main")
             self.code_function (decl, is_main)
             if is_main :
               self.main_func = decl
       if self.main_func == None :
          self.error ("Missing main function")

# -----------------------------------------------------------------------

   def code_program (self, module) :
       # module ... declaration list

       self.openSection (module)
       self.module_cursor = self.location ()
       self.add_lines (5)

       module.global_bytes = 0
       # module.used_bytes = 0
       # module.local_bytes = 0
       # module.reg_list = [ ]
       self.display = [module]

       self.code_declarations (module)

       self.display.pop ()
       self.closeSection ()

       # program header
       version = 0
       self.program = PROGRAMHeader (version, 1 + len (self.objects), module.global_bytes)

       pos = len (self.program) + 12 + 12 * len (self.objects) # position for first instruction

       # main function header
       header = VMTHREADHeader (pos, self.main_func.local_bytes)
       self.program += header
       module.first_instr = pos
       pos += len (self.main_func.code)

       self.goto (self.main_func.subroutine_cursor)
       self.remove_lines (3)
       self.put_bytes ("offset to instruction", header [0:4])
       self.put_bytes ("object id / trigger count", header [4:8])
       self.put_bytes ("local bytes", header [8:12])
       self.goto_end ()

       # function headers
       for obj in self.objects :
          parameters = bytearray ([ ])
          cnt = 0
          for decl in obj.param_list.items :
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
       self.program += self.main_func.code

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
