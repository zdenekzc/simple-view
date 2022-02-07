
# cecko3_to_python.py

from __future__ import print_function

from input import quoteString
from cecko3_parser import *
from output import Output

class C2Py (Output) :

   # statements

   def send_while_stat (self, stat) :
       self.send ("while")
       self.send_expr (stat.cond)
       self.send (":")
       self.style_new_line ()
       self.send_inner_stat (stat.body_stat)

   def send_if_stat (self, stat) :
       self.send ("if")
       self.send_expr (stat.cond)
       self.send (":")
       self.style_new_line ()
       self.send_inner_stat (stat.then_stat)
       if stat.else_stat != None :
          self.style_new_line ()
          self.send ("else")
          self.send (":")
          self.style_new_line ()
          self.send_inner_stat (stat.else_stat)

   def send_for_stat (self, stat) :
       if stat.from_expr != None :
          self.send_expr (stat.from_expr)
       self.style_new_line ()
       self.send ("while")
       if stat.cond_expr != None :
          self.send_expr (stat.cond_expr)
       else :
          self.send ("True")
       self.send (":")
       self.style_new_line ()
       self.style_indent ()
       self.send_stat (stat.body_stat)
       if stat.step_expr != None :
          self.style_indent ()
          self.send_expr (stat.step_expr)
          self.style_unindent ()
       self.style_unindent ()

   def send_return_stat (self, stat) :
       self.send ("return")
       if stat.return_expr != None :
          self.send_expr (stat.return_expr)
       self.style_new_line ()

   def send_compound_stat (self, stat) :
       self.style_indent ()
       self.send_stat_list (stat)
       self.style_unindent ()

   def send_stat_list (self, stat_list) :
       cnt = len (stat_list.items)
       if cnt == 0 :
          self.style_new_line ()
          self.send ("pass")
       for item in stat_list.items :
           self.style_new_line ()
           self.send_stat (item)

   def send_decl_stat (self, stat) :
       decl = stat.inner_decl
       self.send (decl.name)
       self.send ("=")
       if decl.init_value == None :
          self.send ("None")
       else :
          self.send_expr (decl.init_value)

   def send_simple_stat (self, stat) :
       self.send_expr (stat.inner_expr)

   def send_empty_stat (self, stat) :
       self.send ("pass")

   def send_stat (self, stat) :
      if isinstance (stat, CmmWhileStat) :
         self.send_while_stat (stat)
      elif isinstance (stat, CmmIfStat) :
         self.send_if_stat (stat)
      elif isinstance (stat, CmmForStat) :
         self.send_for_stat (stat)
      elif isinstance (stat, CmmReturnStat) :
         self.send_return_stat (stat)
      elif isinstance (stat, CmmCompoundStat) :
         self.send_compound_stat (stat)
      elif isinstance (stat, CmmDeclStat) :
         self.send_decl_stat (stat)
      elif isinstance (stat, CmmSimpleStat) :
         self.send_simple_stat (stat)
      elif isinstance (stat, CmmEmptyStat) :
         self.send_empty_stat (stat)

   def send_inner_stat (self, stat) :
      self.style_new_line ()
      self.style_indent ()
      self.send_stat (stat)
      self.style_unindent ()

   # expressions

   def send_variable_expr (self, expr) :
       name = expr.name
       if name == "true":
          name = "True"
       if name == "false":
          name = "False"
       self.send (name)

   def send_subexpr_expr (self, expr) :
       self.send ("(")
       self.send_expr (expr.subexpr)
       self.send (")")

   def send_expr_list (self, expr) :
      inx = 0
      cnt = len (expr.items)
      if inx < cnt :
         self.send_expr (expr.items [inx])
         inx = inx + 1
         while inx < cnt :
            self.send (",")
            self.send_expr (expr.items [inx])
            inx = inx + 1

   def send_expression (self, expr) :
       self.send_expr (expr)

   def send_expr (self, expr) :
       if expr.kind == expr.varExp :
          self.send_variable_expr (expr)

       elif expr.kind == expr.intValueExp:
          self.send (expr.value)
       elif expr.kind == expr.realValueExp:
          self.send (expr.value)
       elif expr.kind == expr.charValueExp:
          self.send (quoteString (expr.value, "'"))
       elif expr.kind == expr.stringValueExp:
          self.send (quoteString (expr.value))

       elif expr.kind == expr.subexprExp:
          self.send ("(")
          self.send_expr (expr.inner_expr)
          self.send (")")
       elif expr.kind == expr.sequenceExp:
          self.send ("[")
          self.send_expr_list (expr.expr)
          self.send ("]")
       elif expr.kind == expr.thisExp:
          self.send ("self")
       elif expr.kind == expr.indexExp:
          self.send_expr (expr.left)
          self.send ("[")
          self.send_expr_list (expr.expr)
          self.send ("]")
       elif expr.kind == expr.callExp:
          self.send_expr (expr.left)
          self.send ("(")
          self.send_expr_list (expr.param_list)
          self.send (")")
       elif expr.kind == expr.compoundExp:
          self.send_expr (expr.left)
          self.send ("{")
          self.send_stat_list (expr.body)
          self.send ("}")
       elif expr.kind == expr.fieldExp:
          self.send_expr (expr.left)
          self.style_no_space ()
          self.send (".")
          self.style_no_space ()
          self.send (expr.name)
       elif expr.kind == expr.ptrFieldExp:
          self.send_expr (expr.left)
          self.style_no_space ()
          self.send (".")
          self.style_no_space ()
          self.send (expr.name)
       elif expr.kind == expr.postIncExp:
          self.send_expr (expr.left)
          self.send ("=")
          self.send_expr (expr.left)
          self.send ("+")
          self.send ("1")
       elif expr.kind == expr.postDecExp:
          self.send_expr (expr.left)
          self.send ("=")
          self.send_expr (expr.left)
          self.send ("-")
          self.send ("1")
       elif expr.kind == expr.incExp:
          self.send ("++")
          self.send_expr (expr.expr)
       elif expr.kind == expr.decExp:
          self.send ("--")
          self.send_expr (expr.expr)
       elif expr.kind == expr.derefExp:
          self.send ("*")
          self.send_expr (expr.expr)
       elif expr.kind == expr.addrExp:
          self.send ("&")
          self.send_expr (expr.expr)
       elif expr.kind == expr.plusExp:
          self.send ("+")
          self.send_expr (expr.expr)
       elif expr.kind == expr.minusExp:
          self.send ("-")
          self.send_expr (expr.expr)
       elif expr.kind == expr.bitNotExp:
          self.send ("~")
          self.send_expr (expr.expr)
       elif expr.kind == expr.logNotExp:
          self.send ("!")
          self.send_expr (expr.expr)

       elif expr.kind == expr.newExp:
          self.send (expr.type)
          self.send ("(")
          if expr.init_list != None :
             self.send_expr_list (expr.init_list)
          self.send (")")

       elif expr.kind == expr.deleteExp:
          self.send ("del")
          self.send_expr (expr.expr)

       elif isinstance (expr, CmmBinaryExpr) :
          mark = "??"
          if expr.kind == expr.mulExp :
             mark = "*"
          if expr.kind == expr.divExp :
             mark = "/"
          if expr.kind == expr.modExp :
             mark = "%"
          if expr.kind == expr.addExp :
             mark = "+"
          if expr.kind == expr.subExp :
             mark = "-"
          if expr.kind == expr.shlExp :
             mark = "<<"
          if expr.kind == expr.shrExp :
             mark = ">>"
          if expr.kind == expr.ltExp :
             mark = "<"
          if expr.kind == expr.gtExp :
             mark = ">"
          if expr.kind == expr.leExp :
             mark = "<="
          if expr.kind == expr.geExp :
             mark = ">="
          if expr.kind == expr.eqExp :
             mark = "=="
          if expr.kind == expr.neExp :
             mark = "!="
          if expr.kind == expr.logAndExp :
             mark = "&&"
          if expr.kind == expr.logOrExp :
             mark = "||"
          if expr.kind == expr.assignExp :
             mark = "="
          if expr.kind == expr.addAssignExp :
             mark = "+="
          if expr.kind == expr.subAssignExp :
             mark = "-="
          self.send_expr (expr.left)
          self.send (mark)
          self.send_expr (expr.right)
       else :
          self.send ("???")

   # declarations

   def send_class_decl (self, decl) :
       self.openSection (decl)
       self.send ("class")
       self.send (decl.name)
       self.send (":")
       self.style_new_line ()
       self.style_indent ()
       cnt = len (decl.items)
       if cnt == 0 :
          self.style_new_line ()
          send ("pass")
       for item in decl.items :
          self.style_new_line ()
          self.send_simple_decl (item, method = True)
       self.style_unindent ()
       self.style_new_line ()
       self.closeSection ()

   def send_simple_decl (self, decl, method = False) :
       if decl.variable == True :
          self.send (decl.name)
          self.send ("=")
          self.send ("None")
       elif decl.body != None :
          self.openSection (decl)
          self.send ("def")
          self.send (decl.name)
          self.send ("(")
          first = True
          if method :
             self.send ("self")
             first = False
          for item in decl.param_list.items :
              if not first :
                 self.send (",")
              first = False
              self.send_param_decl (item)
          self.send (")")
          self.send (":")
          self.style_indent ()
          self.send_compound_stat (decl.body)
          self.style_unindent ()
          self.closeSection ()

   def send_param_decl (self, decl) :
       self.send (decl.name)

   def send_decl (self, decl) :
       if isinstance (decl, CmmClass) :
          self.send_class_decl (decl)
       elif isinstance (decl, CmmSimpleDecl) :
          self.send_simple_decl (decl)

   def send_declaration_list (self, decl_list) :
      for decl in decl_list.items :
          self.style_new_line ()
          self.send_decl (decl)
          self.style_empty_line ()

   def send_program (self, decl_list) :
      self.send_declaration_list (decl_list)

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
