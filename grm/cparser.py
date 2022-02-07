
# toparser.py

from __future__ import print_function

from grammar import Grammar, Rule, Expression, Alternative, Ebnf, Nonterminal, Terminal, Assign, Execute, New, Style
from output import Output
from symbols import Symbol, initSymbols
from input import quoteString

from toparser import ToParser

# --------------------------------------------------------------------------

class CParser (ToParser) :

   def prindKeywordItem (self, dictionary, inx, name) :
       self.incIndent ()
       if len (dictionary) == 0 :
          self.putLn ("token = " + "keyword_" + name )
       else :
          self.printKeywordDictionary (dictionary, inx+1, name)
       self.decIndent ()

   def printKeywordDictionary (self, dictionary, inx, name) :
       if len (dictionary) == 1 :
          start_inx = inx
          substr = ""
          while len (dictionary) == 1:
             for c in sorted (dictionary.keys ()) : # only one
                 substr = substr + c
                 dictionary = dictionary [c]
                 inx = inx + 1
                 name = name + c
          inx = inx - 1
          if start_inx == inx :
             self.putLn ("if (s[" + str (inx) + "] == " + "'" + substr + "'" + ")")
          else :
             self.putLn ("if (s[" + str (start_inx) + ":" + str (inx+1) + "] == " + '"' + substr + '"' + ")")
          self.prindKeywordItem (dictionary, inx, name)
       else :
           first_item = True
           for c in sorted (dictionary.keys ()) :
               if first_item :
                  cmd = "if"
                  first_item = False
               else :
                  cmd = "else if"
               self.putLn (cmd + " (s[" + str (inx) + "] == "  "'" + c + "'" + ")")
               self.prindKeywordItem (dictionary[c], inx, name+c)

   def selectKeywords (self, grammar) :
       self.putLn ("void " + self.class_name + "::lookupKeyword ()")
       self.putLn ("{")
       self.incIndent ()
       self.putLn ("string s = tokenText;")
       self.putLn ("int n = len (s);")

       lim = 0
       for name in grammar.keyword_dict :
           n = len (name)
           if n > lim :
              lim = n

       size = 1
       first_item = True
       while size <= lim :
          tree = { }
          for name in grammar.keyword_dict :
              if len (name) == size :
                 self.addToDictionary (tree, name)
          if len (tree) != 0 :
             if first_item :
                cmd = "if"
                first_item = False
             else :
                cmd = "elif"
             self.putLn (cmd + " (n == " + str (size) + ")")
             self.putLn ("{")
             self.incIndent ()
             self.printKeywordDictionary (tree, 0, "")
             self.decIndent ()
             self.putLn ("}")
          size = size + 1

       self.decIndent ()
       self.putLn ("}")
       self.putLn ()

   # -----------------------------------------------------------------------

   def printDictionary (self, dictionary) :
       for c in sorted (dictionary.keys ()) :
           self.putLn ("'" + c + "'" + " :")
           self.incIndent ()
           if len (dictionary[c]) == 0 :
              self.putLn ("//")
           else :
              printDictionary (dictionary[c])
           self.decIndent ()

   def selectBranch (self, grammar, dictionary, level, prefix) :
       for c in sorted (dictionary.keys ()) :
           if level == 1 :
              self.putLn ("if (tokenText == " + "'" + c + "'" + ")")
           else :
              self.putLn ("if (ch == " + "'" + c + "'" + ")")
           self.putLn ("{")
           self.incIndent ()
           name = prefix + c
           if name in grammar.separator_dict :
              self.putLn ("token = " + str ( grammar.separator_dict[name].inx)) # !?
           if level > 1 :
              self.putLn ("tokenText = tokenText + ch;")
              self.putLn ("nextChar ();")
           if len (dictionary[c]) != 0 :
              self.selectBranch (grammar, dictionary[c], level+1, prefix+c)
           self.decIndent ()
           self.putLn ("}")

   def selectSeparators (self, grammar) :
       self.putLn ("void " + self.class_name + "::processSeparator ()")
       self.putLn ("{")
       self.incIndent ()

       tree = { }
       for name in grammar.separator_dict :
           self.addToDictionary (tree, name)

       self.selectBranch (grammar, tree, 1, "")

       self.putLn ("if (token == separator)")
       self.putLn ("{")
       self.incIndent ()
       self.putLn ("error (" + '"' + "Unknown separator" + '"' + ");")
       self.decIndent ()
       self.putLn ("}")

       self.decIndent ()
       self.putLn ("}")
       self.putLn ()

   # -----------------------------------------------------------------------

   def executeMethod (self, grammar, func_dict, rule_name, no_param = False) :
       if rule_name in func_dict :
          method_name = func_dict [rule_name]
          self.declareMethod (grammar, method_name, no_param)
          if no_param :
             self.putLn (method_name + " ();")
          else :
             self.putLn (method_name + " (result);")

   def declareField (self, grammar, cls, name, type) :
       pass

   def declareType (self, grammar, rule_type, super_type) :
       pass

   def declareFieldValue (self, grammar, cls, variable, value) :
       pass

   def declareTypes (self, grammar) :
       for type in grammar.type_list :
           self.declareClass (grammar, type)

   def declareClass (self, grammar, type) :
       self.put ("class " + type.name)
       if type.super_type != None :
          self.put (" : public " + type.super_type.name)
       self.putEol ()
       self.putLn ("{")
       self.incIndent ()
       self.putLn ("public:")
       self.incIndent ()

       for enum_name in type.enums :
           enum = type.enums [enum_name]
           self.putLn ("enum Enum_" + enum.name)
           self.putLn ("{")
           self.incIndent ()
           any = False
           for value in enum.values :
               if any :
                  self.putLn (",")
               any = True
               self.put (value)
           if any :
              self.putLn ()
           self.decIndent ()
           self.putLn ("};")
           self.putLn ()

       "field declaration"
       for field in type.field_list :
          if field.field_type == "bool" :
             self.put ("bool")
          elif field.field_type == "str" :
             self.put ("string")
          elif field.field_type == "list" :
             self.put ("list")
          elif field.field_type == "enum" :
             self.put ("Enum_" + field.name)
          else :
             self.put (field.field_type + " *")
          self.putLn (" " + field.name + ";")

       if len (type.field_list) != 0 :
          self.putLn ()

          self.incIndent ()
          any = False
          if type.super_type != None :
             self.put (type.super_type.name + "()")
             any = True
          for field in type.field_list :
              if field.name != type.tag_name :
                 if any :
                    self.putLn (",")
                 any = True
                 self.put (field.name + " (")
                 if field.field_type == "bool" :
                    self.put ("False")
                 elif field.field_type == "str" :
                    self.put ('"' + '"')
                 elif field.field_type == "list" :
                    self.put ("[ ]")
                else :
                   self.put ("None")
              self.put (")")
          self.decIndent ()

          "constructor body"
          self.putLn ("{")
          self.incIndent ()
          if type.tag_name != "" :
             self.putLn (type.tag_name + " = " + type.tag_value)

          self.decIndent ()
          self.putLn ("};")
          self.putLn ()

       "end of class"
       self.decIndent ()
       self.decIndent ()
       self.putLn ("};")
       self.putLn ()

   # -----------------------------------------------------------------------

   def declareTerminals (self, grammar) :
       for symbol in grammar.symbols :
           if symbol.keyword :
              self.putLn ("const int " + symbol.ident + " = " + str (symbol.inx) + ";")
           elif symbol.separator :
              if symbol.ident != "" :
                 self.putLn ("const int " + symbol.ident + " = " + str (symbol.inx) + "; // " + symbol.text)
              else :
                 self.putLn ("// " + symbol.text + " = " + str (symbol.inx))
           else :
              self.putLn ("// " + symbol.ident + " = " + str (symbol.inx))

   def convertTerminals (self, grammar) :
       self.putLn ("string " + self.class_name + "::tokenToString (Token value)")
       self.putLn ("{")
       self.incIndent ()

       for symbol in grammar.symbols :
           self.putLn ("if (value == " + str (symbol.inx) + ") " + "return " + '"' + symbol.alias + '"' + ";")

       self.putLn ("return " + '"' + "<unknown symbol>" + '"' + ";")
       self.decIndent ()
       self.putLn ("}")
       self.putLn ()

   # --------------------------------------------------------------------------

   def declareStoreLocation (self, grammar) :
       self.putLn ("void " + self.class_name + "::storeLocation (item)")
       self.putLn ("{")
       self.incIndent ()
       self.putLn ("item.src_file = tokenFileInx") # !?
       self.putLn ("item.src_line = tokenLineNum")
       self.putLn ("item.src_column = tokenColNum")
       self.putLn ("item.src_pos = tokenByteOfs")
       self.putLn ("item.src_end = charByteOfs")
       self.decIndent ()
       self.putLn ("}")
       self.putLn ()

   def declareAlloc (self, grammar) :
       self.putLn ("bool * " + self.class_name + "::alloc (items) :")
       self.putLn ("{")
       self.incIndent ()
       self.putLn ("result = new bool [" + str (grammar.symbol_cnt) + "];")
       self.putLn ("foreach (item : items)")
       self.putLn ("{")
       self.incIndent ()
       self.putLn ("result [item] = true;")
       self.decIndent ()
       self.putLn ("}")
       self.putLn ("return result;")
       self.decIndent ()
       self.putLn ("}")
       self.putLn ()

   def declareCollections (self, grammar) :
       num = 0
       for data in grammar.collections :

           self.put ("set_" + str (num) + " = alloc (" )

           if use_numbers :
              self.put (str (data))
           else:
              self.put ("[")
              any = False
              for inx in data :
                 if any :
                    self.put (", ")
                 any = True
                 symbol = grammar.symbols [inx]
                 if symbol.ident != "" :
                    self.put (symbol.ident)
                 else :
                    self.put (str (inx))
              self.put ("]")

           self.put ( ") //" )

           for inx in data :
               self.put (" ")
               symbol = grammar.symbols [inx]
               if symbol.text != "" :
                  self.put (" " +symbol.text)
               else :
                  self.put (" " +symbol.ident)

           self.putEol ()
           num = num + 1

   def condition (self, grammar, collection, predicate = None, semantic_predicate = None, test = False) :
       cnt = 0
       for inx in range (len (collection)) :
           if collection [inx] :
              cnt = cnt + 1

       complex = False
       if cnt == 0 :
          # grammar.error ("Empty set")
          # return "nothing"
          code = "True" # !?
       elif cnt <= 3 :
          if cnt > 1 :
             complex = True
          code = ""
          start = True
          for inx in range (len (collection)) :
              if collection [inx] :
                 if not start :
                    code = code + " || "
                 start = False
                 symbol = grammar.symbols[inx]
                 if symbol.ident != "" and not (use_strings and symbol.text != "") :
                    code = code + "token == " + symbol.ident
                 elif symbol.text != "" :
                    code = code + "tokenText == " + '"' + symbol.text + '"'
                 else :
                    code = code + "token == " + str (symbol.inx)
       else :
          num = self.registerCollection (grammar, collection)
          code = "set_" + str (num) + " [token]";

       if predicate != None :
          if not self.simpleExpression (predicate) :
             if cnt == 0 :
                code =  ""
             elif complex :
                code = "(" + code + ")" + " and "
                complex = False
             else :
                code = code + " and "
             inx = self.registerPredicateExpression (grammar, predicate)
             code = code + "test_" + str (inx) + " ()"

       if semantic_predicate != None and not test:
          self.registerSemanticPredicate (grammar, semantic_predicate)
          if code == "True" :
             code = ""
          else :
             if complex :
                code = "(" + code + ")"
             code = code + " and "
          code = code + semantic_predicate + " (result)"

       return code

   def conditionFromAlternative (self, grammar, alt, test = False) :
       code = ""
       done = False
       if alt.continue_alt :
          # semantic predicates inside choose
          for item in alt.items :
              if not done and isinstance (item, Ebnf) :
                 ebnf = item
                 code = self.conditionFromExpression (grammar, ebnf.expr, test)
                 done = True
       if not done :
          code = self.condition (grammar, alt.first, alt.predicate, alt.semantic_predicate, test)
       return code

   def conditionFromExpression (self, grammar, expr, test = False) :
       code = ""
       for alt in expr.alternatives :
           if code != "" :
              code = code + " or "
           code = code + self.conditionFromAlternative (grammar, alt, test)
       return code

   def conditionFromRule (self, grammar, name) :
       if name not in grammar.rule_dict :
          grammar.error ("Unknown rule: " + name)
       rule = grammar.rule_dict [name]
       return self.condition (grammar, rule.first)

# --------------------------------------------------------------------------

   def registerPredicateExpression (self, grammar, expr) :
       if expr in grammar.predicates :
          return grammar.predicates.index (expr) + 1
       else :
          grammar.predicates.append (expr)
          return len (grammar.predicates)

   def registerPredicateNonterminal (self, grammar, item) :
       rule = item.rule_ref
       if rule not in grammar.test_dict :
          grammar.test_dict [rule] = True
          grammar.test_list.append (rule)

   def registerSemanticPredicate (self, grammar, name) :
       if name not in grammar.semantic_predicates :
          grammar.semantic_predicates.append (name)

   def declarePredicates (self, grammar) :
       inx = 1
       for expr in grammar.predicates :
          self.putLn ("bool test_" + str (inx) + " ()")
          self.putLn ("{")
          self.incIndent ()
          self.putLn ("result = true;")
          self.putLn ("position = mark ();")
          self.checkFromExpression (grammar, expr)
          self.putLn ("rewind (position);")
          self.putLn ("return result;")
          self.decIndent()
          self.putLn ("{")
          self.putLn ()
          inx = inx + 1

       inx = 0
       while inx < len (grammar.test_list) :
          rule = grammar.test_list [inx]
          self.testFromRule (grammar, rule)
          inx = inx + 1

# --------------------------------------------------------------------------

   def checkFromExpression (self, grammar, expr, reduced = False) :
       cnt = len (expr.alternatives)
       start = True
       for alt in expr.alternatives :
           if cnt > 1 :
              cond = self.conditionFromAlternative (grammar, alt, test = True)
              if start :
                 self.put ("if")
              else :
                 self.put ("else if")
              start = False
              self.putLn (" (" + cond + ")")
              self.putLn ("{")
              self.incIndent ()
           self.checkFromAlternative (grammar, alt, cnt > 1 or reduced)
           if cnt > 1 :
              self.decIndent ()
              self.putLn ("}")
       if cnt > 1 :
          self.putLn ("else")
          self.putLn ("{")
          self.incIndent ()
          self.putLn ("result = false;")
          self.decIndent ()
          self.putLn ("}")

   def checkFromAlternative (self, grammar, alt, reduced) :
       inx = 1
       for item in alt.items :
           if isinstance (item, Terminal) :
              self.checkFromTerminal (grammar, item, inx == 1 and reduced)
           elif isinstance (item, Nonterminal) :
              self.checkFromNonterminal (grammar, item)
           elif isinstance (item, Ebnf) :
              self.checkFromEbnf (grammar, item)
           inx = inx + 1

   def checkFromEbnf (self, grammar, ebnf) :
       if ebnf.mark == '?' :
          self.put ("if")
       elif ebnf.mark == '*' :
          self.put ("while")
       elif ebnf.mark == '+' :
          self.put ("while")

       if ebnf.mark != "" :
          self.put ("result and (")
          cond = self.conditionFromExpression (grammar, ebnf.expr, test = True)
          self.putLn (" (" + cond + ")")
          self.putLn ("{")
          self.incIndent ()

       self.checkFromExpression (grammar, ebnf.expr, ebnf.mark != "")

       if ebnf.mark != "" :
          self.decIndent ()
          self.putLn ("}")

   def checkFromNonterminal (self, grammar, item) :
       self.registerPredicateNonterminal (grammar, item)
       self.putLn ("if (result)")
       self.putLn ("{")
       self.incIndent ()
       self.putLn ("if (! test_" + item.rule_name + " ())")
       self.putLn ("{")
       self.incIndent ()
       self.putLn ("result = false;")
       self.decIndent ()
       self.putLn ("}")
       self.decIndent ()
       self.putLn ("}")

   def checkFromTerminal (self, grammar, item, reduced) :
       if not reduced :
          symbol = item.symbol_ref
          self.put ("if (result && ")
          if symbol.ident != "" and (symbol.multiterminal or not use_strings or symbol.text == "") :
             self.put ("token != " + symbol.ident)
          elif symbol.text != "":
             self.put ("tokenText != " + '"' + symbol.text + '"')
          else :
             self.put ("check (" + str (symbol.inx) + ");")
          self.putLn ("}")
          self.putLn ("{")
          self.incIndent ()
          self.putLn ("result = false;")
          self.decIndent ()
          self.putLn ("}")

       self.putLn ("if (result)")
       self.putLn ("{")
       self.incIndent ()
       self.putLn ("nextToken ();")
       self.decIndent ()
       self.putLn ("}")

# --------------------------------------------------------------------------

   def testFromRule (self, grammar, rule) :
       self.putLn ("void test_" + rule.name + " ()")
       self.putLn ("{")
       self.incIndent ()
       self.testFromExpression (grammar, rule.expr)
       self.putLn ("return true;")
       self.decIndent ()
       self.putLn ("}")
       self.putEol ()

   def testFromExpression (self, grammar, expr, reduced = False) :
       cnt = len (expr.alternatives)
       start = True
       for alt in expr.alternatives :
           if cnt > 1 :
              cond = self.conditionFromAlternative (grammar, alt, test = True)
              if start :
                 self.put ("if")
              else :
                 self.put ("else if")
              start = False
              self.putLn (" (" + cond + ")")
              self.putLn ("{")
              self.incIndent ()
           self.testFromAlternative (grammar, alt, cnt > 1 or reduced)
           if cnt > 1 :
              self.decIndent ()
              self.putLn ("}")
       if cnt > 1 :
          self.putLn ("else")
          self.putLn ("{")
          self.incIndent ()
          self.putLn ("return false;")
          self.decIndent ()
          self.putLn ("}")

   def testFromAlternative (self, grammar, alt, reduced) :
       inx = 1
       for item in alt.items :
           if isinstance (item, Terminal) :
              self.testFromTerminal (grammar, item, inx == 1 and reduced)
           elif isinstance (item, Nonterminal) :
              self.testFromNonterminal (grammar, item)
           elif isinstance (item, Ebnf) :
              self.testFromEbnf (grammar, item)
           inx = inx + 1

   def testFromEbnf (self, grammar, ebnf) :
       if ebnf.mark == '?' :
          self.put ("if")
       elif ebnf.mark == '*' :
          self.put ("while")
       elif ebnf.mark == '+' :
          self.put ("while")

       if ebnf.mark != "" :
          cond = self.conditionFromExpression (grammar, ebnf.expr, test = True)
          self.putLn (" (" + cond + ")")
          self.putLn ("{")
          self.incIndent ()

       self.testFromExpression (grammar, ebnf.expr, ebnf.mark != "")

       if ebnf.mark != "" :
          self.decIndent ()
          self.putLn ("}")

   def testFromNonterminal (self, grammar, item) :
       self.registerPredicateNonterminal (grammar, item)
       self.putLn ("if (!test_" + item.rule_name + " ())")
       self.putLn ("{")
       self.incIndent ()
       self.putLn ("return false;")
       self.decIndent ()
       self.putLn ("}")

   def testFromTerminal (self, grammar, item, reduced) :
       if not reduced :
          symbol = item.symbol_ref
          self.put ("if (")
          if symbol.ident != "" and (symbol.multiterminal or not use_strings or symbol.text == "") :
             self.put ("token != " + symbol.ident)
          elif symbol.text != "":
             self.put ("tokenText != " + '"' + symbol.text + '"')
          else :
             self.put ("check (" + str (symbol.inx) + ")")
          self.putLn (")")
          self.putLn ("{")
          self.incIndent ()
          self.putLn ("return false;")
          self.decIndent ()
          self.putLn ("}")

       self.putLn ("nextToken ();")

   # -----------------------------------------------------------------------

   def parserFromRules (self, grammar) :
       for rule in grammar.rules :
           self.parserFromRule (grammar, rule)

   def headerFromRule (self, grammar, rule, prefix = "", suffix = "") :
       rule.actual_type = rule.rule_type
       if rule.rule_mode != "" :
          if rule.rule_type != "" :
             self.declareType (grammar, rule.rule_type, rule.super_type)

       params = ""
       if rule.rule_mode == "modify" :
          params = "result"
       if rule.tag_name != "" :
          self.declareTagField (grammar, rule.actual_type, rule.tag_name, rule.tag_value)
       if rule.store_name != "" :
          if params != "" :
             params = params + ", "
          params = params + "store"

       self.putLn (rule.rule_type + " * " + prefix + "parse_" + rule.name + " (" + params + ")" + suffix)

   def parserFromRule (self, grammar, rule) :
       grammar.updatePosition (rule)
       self.headerFromRule (grammar, rule, self.class_name + "::", "")

       self.putLn ("{")
       self.incIndent ()

       if rule.rule_mode == "modify" :
          if grammar.show_tree :
             self.putLn ("if (monitor) monitor.reopenObject (result);")

       if rule.rule_mode == "new" :
          self.putLn (rule.rule_type + " * result = new " + rule.rule_type + " ;")
          if rule.tag_name != "" :
             self.putLn ("result." + rule.tag_name + " = result." + rule.tag_value + ";")
             type = grammar.type_dict [rule.rule_type]
             if rule.tag_name != type.tag_name or rule.tag_value != type.tag_value :
                grammar.error ("Internal tag mismatch")

          self.putLn ("storeLocation (result);")
          if grammar.show_tree :
             self.putLn ("if (monitor) monitor.openObject (result);")

       if rule.store_name != "" :
          self.declareField (grammar, rule.actual_type, rule.store_name, rule.store_type)
          self.putLn ("result->" + rule.store_name + " = store;")

       self.executeMethod (grammar, grammar.execute_on_begin, rule.name)
       self.executeMethod (grammar, grammar.execute_on_begin_no_param, rule.name, no_param = True)

       self.parserFromExpression (grammar, rule, rule.expr)

       self.executeMethod (grammar, grammar.execute_on_end, rule.name)

       if rule.rule_mode == "new" or rule.rule_mode == "modify" :
          if grammar.show_tree :
             self.putLn ("if (monitor) monitor.closeObject ();")

       self.putLn ("return result;")
       self.decIndent ()
       self.putLn ("}")
       self.putEol ()

   def parserFromExpression (self, grammar, rule, expr) :
       cnt = len (expr.alternatives)
       start = True
       for alt in expr.alternatives :
           if cnt > 1 :
              cond = self.conditionFromAlternative (grammar, alt)
              if start :
                 self.put ("if")
              else :
                 self.put ("else if")
              start = False
              self.putLn (" (" + cond + ")")
              self.putLn ("{")
              self.incIndent ()
           self.parserFromAlternative (grammar, rule, alt)
           if cnt > 1 :
              self.decIndent ()
              self.putLn ("}")
       if cnt > 1 :
          self.putLn ("else")
          self.putLn ("{")
          self.incIndent ()
          self.putLn ("error (" +  '"' + "Unexpected token" + '"' + ");")
          self.decIndent ()
          self.putLn ("}")
       if expr.continue_expr :
          self.executeMethod (grammar, grammar.execute_on_choose, rule.name)

   def parserFromAlternative (self, grammar, rule, alt) :
       opened_branch = False
       opened_if = False
       for item in alt.items :
           if isinstance (item, Terminal) :
              self.parserFromTerminal (grammar, rule, item)
           elif isinstance (item, Nonterminal) :
              self.parserFromNonterminal (grammar, rule, item)
           elif isinstance (item, Ebnf) :
              if alt.select_alt :
                 if rule.name in grammar.predicate_on_choose :
                    func_name = grammar.predicate_on_choose [rule.name]
                    self.registerSemanticPredicate (grammar, func_name)
                    self.putLn ("if (" + func_name + " (result))")
                    self.putLn ("{")
                    self.incIndent ()
                    opened_if = True
              self.parserFromEbnf (grammar, rule, item)
           elif isinstance (item, Assign) :
              self.declareFieldValue (grammar, rule.actual_type, item.variable, item.value)
              prefix = ""
              if item.value != "True" and item.value != "False" :
                 prefix = "result->"
              self.putLn ("result->" + item.variable + " = " + prefix + item.value)
           elif isinstance (item, Execute) :
              self.declareMethod (grammar, item.name)
              if item.no_param :
                 self.putLn (item.name + " ();")
              else :
                 self.putLn (item.name + " (result);")
           elif isinstance (item, New) :
              self.declareType (grammar, item.new_type, item.new_super_type)
              self.putLn (rule.rule_type + " * store = result;")
              self.putLn ("result = new " + item.new_type + ";")
              self.putLn ("storeLocation (result);")
              self.putLn ("result->"  + item.store_name + " = store;")
              if grammar.show_tree :
                 self.putLn ("if (monitor) monitor.openObject (result);")
                 opened_branch = True
              rule.actual_type = item.new_type
              if item.store_name != "" :
                 self.declareField (grammar, rule.actual_type, item.store_name, item.store_type)
           elif isinstance (item, Style) :
              pass
           else :
              grammar.error ("Unknown alternative item: " + item.__class__.__name__)
       if opened_branch :
          self.putLn ("if (monitor) monitor.closeObject ();")
       if opened_if :
           self.decIndent ()
           self.putLn ("}")
       if alt.continue_alt :
          rule.actual_type = rule.rule_type

   def parserFromEbnf (self, grammar, rule, ebnf) :
       if ebnf.mark == '?' :
          self.put ("if")
       elif ebnf.mark == '*' :
          self.put ("while")
       elif ebnf.mark == '+' :
          self.put ("while")

       if ebnf.mark != "" :
          cond = self.conditionFromExpression (grammar, ebnf.expr)
          self.putLn (" (" + cond + ")")
          self.putLn ("{")
          self.incIndent ()

       self.parserFromExpression (grammar, rule, ebnf.expr)

       if ebnf.mark != "" :
          self.decIndent ()
          self.putLn ("}")

   def parserFromNonterminal (self, grammar, rule, item) :
       if item.variable != "" :
           self.declareField (grammar, rule.actual_type, item.variable, item.rule_ref.rule_type)
       if item.add :
           self.declareField (grammar, rule.actual_type, "items", "list")

       if item.select_item :
          self.executeMethod (grammar, grammar.execute_on_entry_no_param, rule.name, no_param = True)

       if item.add :
          self.put ("result->items.append (")
       if item.select_item or item.choose_item or item.continue_item :
          self.put ("result = ")
       if item.variable != ""  :
          self.put ("result->" + item.variable + " = ")

       self.put ("parse_" + item.rule_name)

       params = ""
       if item.modify or item.rule_ref.rule_mode == "modify" :
          params = "result"
       if item.rule_ref.store_name != "" :
          params = "result"

       self.put (" (")
       if params != "" :
          self.put (params)
       self.put (")")

       if item.add :
          self.put (")") # close append parameters
       self.putLn (";")

       if item.select_item :
          self.executeMethod (grammar, grammar.execute_on_fork_no_param, rule.name, no_param = True)

   def parserFromTerminal (self, grammar, rule, item) :
       symbol = item.symbol_ref
       if symbol.multiterminal :
          if item.variable != "" :
             self.declareField (grammar, rule.actual_type, item.variable, "str")
             self.put ("result->" + item.variable + " = ")

          func = symbol.ident
          if func.endswith ("_number") :
             func = func [ : -7 ]
          if func.endswith ("_literal") :
             func = func [ : -8 ]
          func = "read" + func.capitalize()

          self.putLn (func + " ();")
       else :
          if symbol.ident != "" and not (use_strings and symbol.text != "") :
             self.putLn ("checkToken (" + symbol.ident + ");")
          elif symbol.text != "":
             self.putLn ("check (" + '"' + symbol.text + '"' + ");")
          else :
             self.putLn ("check (" + str (symbol.inx) + ");")

# --------------------------------------------------------------------------

   def parserFromGrammar (self, grammar, class_name = "Parser") :
       grammar.parseRules ()

       initSymbols (grammar)
       self.initCollections (grammar)

       for name in grammar.check_rules :
           if name not in grammar.rule_dict :
              grammar.error ("Unknown rule used in directive: " + name)

       for struct in grammar.struct_decl :
          self.declareType (grammar, struct.struct_name, struct.super_type)
          if struct.tag_name != "" :
             self.declareTagField (grammar, struct.struct_name, struct.tag_name, struct.tag_value)
          for field in struct.fields :
              self.declareFieldVariable (grammar, struct.struct_name, field.field_name, field.field_type)

       self.putLn ()
       self.putLn ("#include " + quoteString ("lexer.h"))
       self.putLn ()

       for type in grammar.type_list :
           self.putLn ("class " + type.name + ";")
       self.putLn ()

       self.putLn ("class " + class_name + " : public Lexer")
       self.putLn ("{")
       self.incIndent ()
       self.putLn ("public:")
       self.incIndent ()

       self.putLn (class_name + " ();") # constructor
       self.putLn ()

       for rule in grammar.rules :
          self.headerFromRule (grammar, rule, "", ";")
       self.putLn ()

       self.putLn ("void lookupKeyword ();")
       self.putLn ("void processSeparator ();")
       self.putLn ("string tokenToString (Token value);")
       self.putLn ("void storeLocation (item);")
       self.putLn ()

       for method_name in grammar.methods :
          self.putLn ("virtual void " +  method_name + " (item) { }")

       for method_name in grammar.methods_no_param :
          self.putLn ("virtual void " +  method_name + " () { }")
       self.style_empty_line ()

       self.decIndent () # end of class
       self.decIndent ()
       self.putLn ("};")
       self.putLn ()

       # constructor
       self.putLn (class_name + "::" + class_name + " () :")
       self.incIndent ()
       self.putLn ("Lexer ()")
       self.decIndent ()
       self.putLn ("{")
       self.incIndent ()
       if grammar.show_tree :
          self.putLn ("monitor = NULL")
       self.putLn ()
       # self.declareTerminals (grammar)
       self.putLn ()
       # self.declareCollections (grammar)
       self.decIndent ()
       self.putLn ("}")
       self.putLn ()

       for method_name in grammar.methods :
          self.putLn ("void " +  method_name + " (item)")
          self.putLn ("{")
          self.putLn ("}")
          self.putLn ()

       for method_name in grammar.methods_no_param :
          self.putLn ("void " +  method_name + " ()")
          self.putLn ("{")
          self.putLn ("}")
          self.putLn ()

       for method_name in grammar.semantic_predicates:
          self.putLn ("bool " +  method_name + " (item) ")
          self.putLn ("{")
          self.incIndent ()
          self.putLn ("return false;")
          self.decIndent ()
          self.putLn ("}")
          self.putLn ()

       self.decIndent () # end of class
       self.decIndent ()
       self.putLn ("};")
       self.putLn ()

       self.parserFromRules (grammar)

       self.selectKeywords (grammar)
       self.selectSeparators (grammar)
       self.convertTerminals (grammar)
       self.declareStoreLocation (grammar)
       self.declareAlloc (grammar)

       self.declareTypes (grammar)

       self.declareTerminals (grammar)
       self.declareCollections (grammar)


# --------------------------------------------------------------------------

if __name__ == "__main__" :
    grammar = Grammar ()
    grammar.openFile ("input/pas.g")

    product = CParser ()
    product.parserFromGrammar (grammar)

# --------------------------------------------------------------------------

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
