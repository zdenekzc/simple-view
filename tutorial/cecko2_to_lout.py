
from cecko2_parser import *
from output import Output

class ExampleToLout (Output) :

   def send_while_stat (self, param) :
       self.send ("red @Color @Box while")
       self.send_inner_expr (param.cond)
       self.send_inner_stat (param.code, next = True)

   def send_if_stat (self, param) :
       self.send ("red @Color @Circle if")
       self.send_inner_expr (param.cond)
       self.send_inner_stat (param.then_code, next = True)
       if param.else_code != None :
          self.send_inner_stat (param.else_code, next = True)

   def send_compound_stat (self, param) :
       quote = "\""
       self.send ("red @Color @Circle " + quote + "{}" + quote)
       next = False
       for item in param.items  :
          self.send_inner_stat (item, next)
          next = True

   def send_simple_stat (self, param) :
      self.send_expr (param.subexpr)

   def send_empty_stat (self, param) :
      self.send ("@Circle ;")

   def send_stat (self, param) :
      if isinstance (param, TWhileStat) :
         self.send_while_stat (param)
      elif isinstance (param, TIfStat) :
         self.send_if_stat (param)
      elif isinstance (param, TCompoundStat) :
         self.send_compound_stat (param)
      elif isinstance (param, TSimpleStat) :
         self.send_simple_stat (param)
      elif isinstance (param, TEmptyStat) :
         self.send_empty_stat (param)

   def send_expr (self, param) :
      self.send_expression (param)

   def send_expression (self, param) :
      if param.kind == param.varExp:
         self.send ("{ @Xrgb orange } @Color @CurveBox " + param.name)
      elif param.kind == param.valueExp:
         self.send ("gray @Color @Circle " + param.value)
      elif param.kind == param.subexprExp:
         self.send_expr (param.subexpr)
      elif isinstance (param, TBinaryExpr) :
         mark = ""
         if param.kind == param.mulExp :
            mark = "*"
         if param.kind == param.divExp :
            mark = "/"
         if param.kind == param.modExp :
            mark = "%"
         if param.kind == param.addExp :
            mark = "+"
         if param.kind == param.subExp :
            mark = "-"
         if param.kind == param.ltExp :
            mark = "<"
         if param.kind == param.gtExp :
            mark = ">"
         if param.kind == param.leExp :
            mark = "<="
         if param.kind == param.geExp :
            mark = ">="
         if param.kind == param.eqExp :
            mark = "=="
         if param.kind == param.neExp :
            mark = "!="
         if param.kind == param.logAndExp :
            mark = "&&"
         if param.kind == param.logOrExp :
            mark = "||"
         if param.kind == param.assignExp :
            mark = "="

         if param.kind == param.assignExp :
            self.send ("green @Color")
         else :
            self.send ("blue @Color")

         quote = "\""
         self.send ("@Circle " + quote + mark + quote)
         self.send_inner_expr (param.left)
         self.send_inner_expr (param.right, next = True)

      else :
         quote = "\""
         self.send ("@Circle " + quote + "?" + quote)

   def send_inner_stat (self, param, next = False) :
       self.style_new_line ()
       if next :
          self.send ("@NextSub {")
       else :
          self.send ("@FirstSub {")
       self.style_new_line ()
       self.style_indent ()
       self.send_stat (param)
       self.style_unindent ()
       self.style_new_line ()
       self.send ("}")

   def send_inner_expr (self, param, next = False) :
       self.style_new_line ()
       if next :
          self.send ("@NextSub {")
       else :
          self.send ("@FirstSub {")
       self.style_new_line ()
       self.style_indent ()
       self.send_expr (param)
       self.style_unindent ()
       self.style_new_line ()
       self.send ("}")

   def send_program (self, param) :
       self.putLn ("@SysInclude { diag }")
       self.putLn ("@SysInclude { xrgb }") # colors
       self.putLn ("@SysInclude { doc }")
       self.putLn ("@Doc @Text @Begin")
       self.putLn ("")

       self.putLn ("@Diag {")
       self.style_new_line ()
       self.style_indent ()

       self.putLn ("@Tree {")
       self.style_new_line ()
       self.style_indent ()

       self.send_stat (param)

       self.style_unindent ()
       self.style_new_line ()
       self.putLn ("}")

       self.style_unindent ()
       self.style_new_line ()
       self.putLn ("}")

       self.putLn ("@End @Text")

