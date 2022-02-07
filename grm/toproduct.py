
# toproduct.py

from __future__ import print_function

from grammar import Grammar, Rule, Expression, Alternative, Ebnf, Nonterminal, Terminal, Directive, Assign, Style, New, Execute
from output import Output
# from output import incIndent, decIndent, put, putEol, putCondEol, putLn

# --------------------------------------------------------------------------

class ToProduct (Output) :

   def __init__ (self) :
       super (ToProduct, self).__init__ ()
       # self.enable_subst = True

   def conditionFromAlternative (self, grammar, alt) :
       for item in alt.items :
           if isinstance (item, Nonterminal) :
              if item.variable != "" :
                 return "param." + item.variable + " != None"
              elif item.add :
                 return "inx < cnt"
              elif item.select_item or item.continue_item :
                 rule_ref = item.rule_ref
                 if rule_ref.tag_name != "" :
                    return "param." + rule_ref.tag_name + " == " + "param." + rule_ref.tag_value
                 else :
                    return "isinstance (param, " + rule_ref.rule_type + ")"
           elif isinstance (item, Terminal) :
              if item.multiterminal_name != "" :
                 return "param." + item.variable + " != " + '"' + '"'
           elif isinstance (item, New) :
              # type = grammar.type_dict [item.new_type]
              # if type.tag_name != "" : # !?
              #    return "param." + type.tag_name + " == " + "param." + type.tag_value
              # else :
                 return "isinstance (param, " + item.new_type + ")"
           elif isinstance (item, Assign) :
              prefix = ""
              if item.value != "True" and item.value != "False" :
                 prefix = "param."
              return "param." + item.variable + " == " + prefix + item.value
       return "unknown"
       # grammar.error ("Cannot find condition")

   def conditionFromExpression (self, grammar, expr) :
       result = ""
       for alt in expr.alternatives :
           if result != "" :
              result = result + " or "
           result = result + self.conditionFromAlternative (grammar, alt)
       return result

   def conditionIsUnknown (self, cond) :
       return (cond == "unknown")

   def conditionIsLoop (self, grammar, expr) :
       result = False
       for alt in expr.alternatives :
           cond = self.conditionFromAlternative (grammar, alt)
           if cond == "inx < cnt" :
              result = True
       return result

# --------------------------------------------------------------------------

   def productFromRules (self, grammar) :
       self.last_rule = None
       for rule in grammar.rules :
           self.setupGroup (grammar, rule)
       for rule in grammar.rules :
           if rule.hide_group == None :
              self.productFromRule (grammar, rule)

   def productFromRule (self, grammar, rule) :
       grammar.updatePosition (rule)
       self.last_rule = rule
       if rule.rule_mode != "" :
          grammar.charLineNum = rule.src_line # !?
          grammar.charColNum = rule.src_column
          self.putLn ("def send_" + rule.name + " (self, param) :")
          self.incIndent ()
          if rule.add_used :
             self.putLn ("inx = 0")
             self.putLn ("cnt = len (param.items)")
          self.productFromExpression (grammar, rule, rule.expr)
          self.decIndent ()
          self.putEol ()

   def productChooseItem (self, grammar, rule, alt, field, enable_recursion) :
       proc = self.ruleOrGroupName (grammar, alt.select_nonterm.rule_name)
       if enable_recursion :
          mark = alt.continue_ebnf.mark
          if mark == "+" or mark == "*" :
             proc = rule.name
       self.putLn ("self.send_" + proc + " (" + field + ")")

   def productFromExpression (self, grammar, rule, expr) :
       cnt = len (expr.alternatives)
       inx = 0
       for alt in expr.alternatives :
           if cnt > 1 or expr.continue_expr :
              cond = self.conditionFromAlternative (grammar, alt)
              if self.conditionIsUnknown (cond) :
                 if inx < len (expr.alternatives) - 1 :
                    grammar.error ("Cannot find condition (rule: " + self.last_rule.name+ ")")
                 else :
                    self.putLn ("else :")
              else :
                 if inx == 0 :
                    self.putLn ("if " + cond + " :")
                 else :
                    self.putLn ("elif " + cond + " :")
              self.incIndent ()
           self.productFromAlternative (grammar, rule, alt)
           if cnt > 1  or expr.continue_expr :
              self.decIndent ()
           inx = inx + 1
       if expr.continue_expr :
          self.putLn ("else :")
          self.incIndent ()
          self.productChooseItem (grammar, rule, expr.expr_link, "param", False)
          self.decIndent ()

   def productFromAlternative (self, grammar, rule, alt) :
       grammar.updatePosition (alt)
       any = False
       for item in alt.items :
           if isinstance (item, Terminal) :
              self.productFromTerminal (grammar, item)
              any = True
           elif isinstance (item, Nonterminal) :
              if item.continue_item :
                 if item.rule_ref.store_name != "" :
                    self.productChooseItem (grammar, rule, alt.alt_link, "param." + item.rule_ref.store_name, True)
              choose = item.select_item and item.item_link.continue_ebnf != None
              if not choose :
                 self.productFromNonterminal (grammar, item)
                 any = True
           elif isinstance (item, Ebnf) :
              self.productFromEbnf (grammar, rule, item)
              any = True
           elif isinstance (item, Style) :
              self.productFromStyle (grammar, item)
              any = True
           elif isinstance (item, New) :
              self.productChooseItem (grammar, rule, alt.alt_link, "param." + item.store_name, True)
              any = True
           elif isinstance (item, Directive) :
              pass
           else :
              raise Exception ("Unknown alternative item")
       if not any :
          self.putLn ("pass")

   def productFromEbnf (self, grammar, rule, ebnf) :
       grammar.updatePosition (ebnf)
       block = False
       if not ebnf.expr.continue_expr :
          cond = self.conditionFromExpression (grammar, ebnf.expr)
          if ebnf.mark == '?' :
             self.putLn ("if " + cond + " :")
             block = True
          if ebnf.mark == '*' or ebnf.mark == '+' :
             loop = self.conditionIsLoop (grammar, ebnf.expr)
             if loop :
                self.putLn ("while " + cond + " :")
             else :
                self.putLn ("if " + cond + " :")
             block = True

       if block :
          self.incIndent ()

       self.productFromExpression (grammar, rule, ebnf.expr)

       if block :
          self.decIndent ()

   def productFromNonterminal (self, grammar, item, field = "") :
       grammar.updatePosition (item)
       proc = self.ruleOrGroupName (grammar, item.rule_name)

       self.put ("self.send_" + proc)
       self.put (" (")
       if field != "" :
          self.put ("param." + field)
       elif item.variable :
          self.put ("param." + item.variable)
       elif item.add :
          self.put ("param.items [inx]")
       elif item.modify or item.select_item or item.continue_item :
          self.put ("param")
       self.putLn (")")

       if item.add :
          self.putLn ("inx = inx + 1")

   def productFromTerminal (self, grammar, item) :
       if item.multiterminal_name != "" :
          if item.variable != "" :
             quote1 = item.multiterminal_name == "character_literal";
             quote2 = item.multiterminal_name == "string_literal";

             if quote1 :
                self.put ("self.sendChr (")
             elif quote2 :
                self.put ("self.sendStr (")
             else :
                self.put ("self.send (")
             self.put ("param." + item.variable)
             self.putLn (")")
       else :
          self.putLn ("self.send (" + '"' + item.text + '"' + ")")

   def productFromStyle (self, grammar, item) :
       self.putLn ("self.style_" + item.name + " ()")

# --------------------------------------------------------------------------

   def isDerivedType (self, grammar, rule, target_name) :
       result = False
       if rule.rule_type != "" :
          type = grammar.type_dict.get (rule.rule_type, None)
          while type != None and type.name != target_name :
             type = type.super_type
          if type != None :
             result = True
       return result

   def setupGroup (self, grammar, rule) :
       cnt = 0
       for group in grammar.group_list :
           result = False
           # grammar.info ("Testing " + rule_name + " : " + group.group_name + " : " + str (group.rule_list))

           if group.from_type != "" :
              result = self.isDerivedType (grammar, rule, group.from_type)
              if rule.name in group.include_list :
                 result = True
              if rule.name in group.exclude_list :
                 result = False
              if result  :
                 cnt = cnt + 1
                 rule.hide_group = group
                 rule.rewrite_group = group
                 rule.subst_group = group

           if group.ctrl_type != "" :
              if rule.name in group.include_list :
                 cnt = cnt + 1
                 rule.hide_group = group
                 rule.subst_group = group
              else :
                 result = self.isDerivedType (grammar, rule, group.ctrl_type)
                 if rule.name in group.exclude_list :
                    result = False
                 if result :
                    cnt = cnt + 1
                    rule.reuse_group = group

       if cnt > 1 :
          grammar.error ("Rule " + rule.name + "is in two groups")

   def ruleOrGroupName (self, grammar, rule_name) :
       rule = grammar.rule_dict [rule_name]
       group = rule.subst_group
       if group != None :
          proc = group.group_name
       else :
          proc = rule_name
       return proc

   def productFromGroups (self, grammar) :
       for group in grammar.group_list :
           self.productFromGroup (grammar, group)

   def productFromGroup (self, grammar, group) :
       proc = "send_" + group.group_name
       self.putLn ("def " + proc + " (self, param) :")
       self.incIndent ()

       self.artificialItems (grammar, group)

       for rule in grammar.rules :
          grammar.updatePosition (rule)
          grammar.charLineNum = rule.src_line # !?
          grammar.charColNum = rule.src_column
          if rule.rule_mode != "" :
             if rule.reuse_group == group :
                self.ruleFromReuseGroup (grammar, group, rule)
             if rule.rewrite_group == group :
                self.ruleFromRewriteGroup (grammar, group, rule)

       self.decIndent ()
       self.putLn ("")

       self.artificialFunctions (grammar, group)

   def ruleFromReuseGroup (self, grammar, group, rule) :
       # proc = "send_" + group.group_name
       proc = "send_expr" # !?
       if rule.rule_mode == "new" :
          if rule.tag_name != "" :
             self.putLn ("if param." + rule.tag_name + " == param." + rule.tag_value + ":")
          else :
             self.putLn ("if isinstance (param, " + rule.rule_type + ") :")
          self.incIndent ()
          if rule.store_name != "" :
               self.putLn ("self." + proc + " (param." + rule.store_name + ")")
          self.putLn ("self.send_" + rule.name + " (param)")
          # self.productFromExpression (grammar, rule, rule.expr)
          self.decIndent ()

   def ruleFromRewriteGroup (self, grammar, group, rule) :
       proc = "send_" + group.group_name
       if rule.rule_mode == "new" :
          if rule.tag_name != "" :
             self.putLn ("if param." + rule.tag_name + " == param." + rule.tag_value + ":")
          else :
             self.putLn ("if isinstance (param, " + rule.rule_type + ") :")
          self.incIndent ()
          if rule.add_used :
             self.putLn ("inx = 0")
             self.putLn ("cnt = len (param.items)")
          if rule.store_name != "" :
               self.putLn ("self.send_expr (param." + rule.store_name + ")") # !?
          self.productFromExpression (grammar, rule, rule.expr)
          self.decIndent ()
       elif rule.rule_mode == "select" :
          # self.putLn ("# Add " + rule.name + " to " + proc)
          for alt1 in rule.expr.alternatives :
             for item1 in alt1.items :
                 """
                 if isinstance (item1, Nonterminal) :
                    cond = self.conditionFromAlternative (grammar, alt1)
                    self.putLn ("if " + cond + " :")
                    self.incIndent ()
                    self.productFromAlternative (grammar, rule, alt1)
                    self.decIndent ()
                 elif isinstance (item1, Ebnf) :
                 """
                 if isinstance (item1, Ebnf) :
                    expr1 = item1.expr
                    if expr1.continue_expr :
                       for alt2 in expr1.alternatives :
                           cnt2 = len (alt2.items)
                           if cnt2 == 4 or cnt2 == 5 :
                              if isinstance (alt2.items [cnt2-2], Execute) :
                                 cnt2 = cnt2 - 1
                           if cnt2 == 1 :
                              pass
                           elif cnt2 == 3 :
                              a = alt2.items [0]
                              b = alt2.items [1]
                              c = alt2.items [2]
                              if isinstance (a, New) and isinstance (b, Ebnf) and isinstance (c, Nonterminal) and c.variable != "" :
                                 for alt3 in b.expr.alternatives :
                                     cond = self.conditionFromAlternative (grammar, alt3)
                                     self.putLn ("if " + cond + " :")
                                     self.incIndent ()
                                     self.putLn ("self." + proc + " (param." + a.store_name + ")")
                                     self.productFromAlternative (grammar, rule, alt3)
                                     self.putLn ("self." + proc + " (param." + c.variable + ")")
                                     self.decIndent ()
                              else :
                                 self.putLn ("# unknown rule " + rule.name)
                           elif cnt2 == 4 :
                              a = alt2.items [0]
                              b = alt2.items [1]
                              c = alt2.items [2]
                              d = alt2.items [3]
                              if isinstance (a, New) and isinstance (b, Terminal) and isinstance (c, Assign) and isinstance (d, Nonterminal) and d.variable != "":
                                 cond = self.conditionFromAlternative (grammar, alt2)
                                 self.putLn ("if param." + c.variable + " == param." + c.value + " :")
                                 self.incIndent ()
                                 self.putLn ("self." + proc + " (param." + a.store_name + ")")
                                 self.productFromTerminal (grammar, b)
                                 self.putLn ("self." + proc + " (param." + d.variable + ")")
                                 self.decIndent ()
                              else :
                                 self.putLn ("# unknown rule" + rule.name)
                           else :
                              self.putLn ("# unknown rule " + rule.name)
                 # else :
                 #    self.putLn ("# unknown item " + rule.name)

# --------------------------------------------------------------------------

   def artificialItems (self, grammar, group) :
       # start = True
       for artificial in group.artificial_list :
              type = grammar.type_dict.get (artificial.struct_name, None)
              if type == None :
                 grammar.error ("Unknown stucture: " +  artificial.struct_name)

              if type.tag_name != "" :
                 cond =  "param." + type.tag_name + " == " + "param." + type.tag_value
              else :
                 cond = "isinstance (param, " + type.struct_name + ")"

              self.putLn ("if " + cond + " :")
              # if start :
              #    self.putLn ("if " + cond + " :")
              # else :
              #    self.putLn ("elif " + cond + " :")
              # start = False

              self.incIndent ()
              self.putLn ("self.send_" + artificial.call_name + " (param)")
              self.decIndent ()

   def artificialFunctions (self, grammar, group) :
       for artificial in group.artificial_list :
           self.putLn ("def send_" + artificial.call_name + " (self, param) :")
           self.incIndent ()
           self.putLn ("pass")
           self.decIndent ()
           self.putLn ()

# --------------------------------------------------------------------------

   def productFromGrammar (self, grammar, parser_module = "") :

       self.putLn ()
       if parser_module != "" :
          self.putLn ("from " + parser_module + " import *")
       self.putLn ("from output import Output")
       self.putLn ()

       self.putLn ("class Product (Output) :")
       self.putLn ("")
       self.incIndent ()

       self.productFromRules (grammar)
       self.productFromGroups (grammar)

       self.decIndent ()

# --------------------------------------------------------------------------

if __name__ == "__main__" :
    grammar = Grammar ()
    grammar.openFile ("../pas/pas.g")
    grammar.parseRules ()

    product = ToProduct ()
    product.productFromGrammar (grammar)

# --------------------------------------------------------------------------

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
