
# grammar.py

from __future__ import print_function

from lexer import Lexer

# --------------------------------------------------------------------------

class Rule (object) :
   def __init__ (self) :
       self.name = ""
       self.expr = None
       self.rule_mode = ""
       self.rule_type = ""
       self.super_type = ""
       self.tag_name = ""
       self.tag_value = ""
       self.store_name = ""
       self.store_type = ""

       self.hide_group = None
       self.reuse_group = None
       self.rewrite_group = None
       self.subst_group = None

       self.add_used = False
       self.start = False
       self.new_directive = None # local
       self.actual_type = "" # local
       self.above_alt = None # local
       self.predicate_level = 0 # local
       # self.nullable = False
       # self.first = [ ]
       # self.line = 1

class Expression (object) :
   def __init__ (self) :
       self.alternatives = [ ]
       # continue expr
       self.continue_expr = False
       self.expr_link = None # selection alternative
       # self.nullable = False
       # self.first = [ ]
       # self.follow = [ ]
       # self.line = 1

class Alternative (object) :
   def __init__ (self) :
       self.items = [ ]
       self.level = 0
       self.silent = False
       self.leading_required = False # local
       self.predicate = None
       self.semantic_predicate = None
       # selection alternative
       self.select_alt = False # top level alternative in <select> rule
       self.select_nonterm = None
       # continue selection alternative
       self.continue_ebnf = None
       self.continue_alt = False # alternative in ( ... ) expression in <select> rule
       self.alt_link = None # selection alternative
       # self.nullable = False
       # self.first = [ ]
       # self.follow = [ ]
       # self.line = 1

class Ebnf (object) :
   def __init__ (self) :
       self.mark = ""
       self.expr = None
       # self.nullable = False
       # self.first = [ ]
       # self.follow = [ ]
       # self.line = 1

class Nonterminal (object) :
   def __init__ (self) :
       self.variable = ""
       self.rule_name = ""
       self.add = False
       self.modify = False
       # selection item
       self.select_item = False
       self.item_link = None # selection alternative
       # continue item
       self.continue_item = False
       # self.rule_ref = None
       # self.nullable = False
       # self.first = [ ]
       # self.line = 1

class Terminal (object) :
   def __init__ (self) :
       self.text = ""

       self.variable = ""
       self.multiterminal_name = ""

       # self.symbol_ref = None
       # self.nullable = False
       # self.first = [ ]
       # self.line = 1

# --------------------------------------------------------------------------

class Directive (object) :
   def __init__ (self) :
       pass

class Assign (Directive) :
   def __init__ (self) :
       self.variable = ""
       self.value = ""

class Execute (Directive) :
   def __init__ (self) :
       self.name = ""
       self.no_param = False

class New (Directive) :
   def __init__ (self) :
       self.new_type = ""
       self.new_super_type = ""
       self.store_name = ""
       self.store_type = ""
       # self.tag_name = ""
       # self.tag_value = ""

class Style (Directive) :
   def __init__ (self) :
       self.name = ""

# class SyntacticPredicate (object) :
#    def __init__ (self) :
#        self.expr = None

# --------------------------------------------------------------------------

class Options (object) :
   def __init__ (self) :
       self.add = False
       self.modify = False
       self.need_nonterminal = False

# --------------------------------------------------------------------------

class GroupDecl (object) :
   def __init__ (self) :
       self.group_name = ""
       self.from_type = ""
       self.ctrl_type = ""
       self.include_list = [ ]
       self.exclude_list = [ ]
       self.artificial_list = [ ]

class ArtificialDecl (object) :
   def __init__ (self) :
       self.group_name = ""
       self.call_name = ""
       self.struct_name = ""

# --------------------------------------------------------------------------

class StructDecl (object) :
   def __init__ (self) :
       self.struct_name = ""
       self.super_type = ""
       self.tag_name = ""
       self.tag_value = ""
       self.fields = [ ]

class FieldDecl (object) :
   def __init__ (self) :
       self.field_type = ""
       self.field_name = ""

# --------------------------------------------------------------------------

class Type (object) :
    def __init__ (self) :
        self.name = ""
        self.super_type = None
        self.fields = { }
        self.field_list = [ ]
        self.enums = { }
        self.enum_list = [ ]
        self.tag_name = ""
        self.tag_value = ""

class Field (object) :
    def __init__ (self) :
        self.name = ""
        self.field_type = ""
        self.struct_type = None

class Enum (object) :
    def __init__ (self) :
        self.name = ""
        self.values = [ ]

# --------------------------------------------------------------------------

class Grammar (Lexer) :

   def __init__ (self) :
       super (Grammar, self).__init__ ()
       self.rules = [ ]
       self.struct_decl = [ ]
       self.multiterminals = [ "identifier",
                               "number",
                               "real_number",
                               "character_literal",
                               "string_literal" ]

       self.type_list = [ ]
       self.type_dict = { }
       self.methods = [ ]
       self.methods_no_param = [ ]

       self.predicates = [ ]
       self.semantic_predicates = [ ]
       self.test_list = [ ]
       self.test_dict = { }

       self.execute_on_begin = { }
       self.execute_on_end = { }
       self.execute_on_begin_no_param = { }
       self.execute_on_entry_no_param = { }
       self.execute_on_fork_no_param = { }
       self.predicate_on_choose = { }
       self.execute_on_choose = { }

       self.group_list = [ ]

       self.check_rules = [ ]

       self.show_tree = False

       # self.multiterminal_dict = { }
       # self.keyword_dict = { }
       # self.separator_dict = { }
       #
       # self.symbol_cnt = 0
       # self.symbols = [ ]
       # self.symbol_dict = { }
       #
       # self.rule_dict = { }
       # self.nullableChanged = True
       # self.firstChanged = True
       # self.followChanged = True
       #
       # self.collections = { }

   # -- types --

   def declareType (self, name, super_type_name = "") :
       if super_type_name != "" :
          super_type = self.declareType (super_type_name)

       if name in self.type_dict :
          type = self.type_dict [name]
       else :
          type = Type ()
          type.name = name
          self.type_dict [name] = type
          self.type_list.append (type)

       if super_type_name != "" :
          if type.super_type != None and type.super_type != super_type :
             self.error ("Super type for " + type.name + " already defined")
          type.super_type = super_type

          # if type (without super_type) was already in type_list, correct type_list
          if self.type_list.index (super_type) > self.type_list.index (type) :
             self.type_list.remove (type)
             self.type_list.append (type)

       return type

   def findField (self, type, field_name) :
       while type != None and field_name not in type.fields :
          type = type.super_type
       field = None
       if type != None :
          field = type.fields [field_name]
       return field

   def declareField (self, type_name, field_name, field_type) :
       type = self.declareType (type_name)
       field = self.findField (type, field_name)
       if field != None :
          if field_type != field.field_type :
             self.error ("Field " + type_name + "." + field_name + " already defined with different type")
       else :
          field = Field ()
          field.name = field_name
          field.field_type = field_type
          field.struct_type = type
          type.fields [field_name] = field
          type.field_list.append (field)
       return field

   def declareEnumType (self, type, enum_name) :
       if enum_name in type.enums :
          enum = type.enums [enum_name]
       else :
          enum = Enum ()
          enum.name = enum_name
          type.enums [enum_name] = enum
          type.enum_list.append (enum)
       return enum

   def declareEnumValue (self, type, enum_name, enum_value) :
       enum = self.declareEnumType (type, enum_name)
       if enum_value not in enum.values :
          enum.values = enum.values + [enum_value]

   def declareFieldVariable (self, type_name, field_name, field_type) :
       field = self.declareField (type_name, field_name, field_type)
       if field_type == "enum" :
          self.declareEnumType (field.struct_type, field_name)

   def declareFieldValue (self, type_name, field_name, field_value) :
       if field_value == "True" or field_value == "False" :
          self.declareField (type_name, field_name, "bool")
       else :
          field = self.declareField (type_name, field_name, "enum")
          self.declareEnumValue (field.struct_type, field_name, field_value)

   def declareTagField (self, type_name, field_name, field_value) :
       self.declareFieldValue (type_name, field_name, field_value)
       type = self.type_dict [type_name]
       if type.tag_name != "" :
          self.error ("Type " + type_name + " already has tag " + type.tag_name)
       type.tag_name = field_name
       type.tag_value = field_value

   def declareMethod (self, method_name, no_param = False) :
       if no_param :
           methods = self.methods_no_param
       else :
           methods = self.methods

       if method_name not in methods :
          methods.append (method_name)

   # -- read directive --

   """
   def skipDirective (self) :
       while self.isSeparator ('<') :
          self.nextToken ()
          while not self.isEndOfSource () and not self.isSeparator ('>') :
             self.nextToken ()
          if self.isEndOfSource () :
             self.error ("Unfinished directive")
          self.nextToken () # skip '>'
   """

   # -- rule directive --

   def ruleDirective (self, rule) :
       if self.isSeparator ('<') :
          self.nextToken ()

          if not self.isSeparator ('>') :

             if self.isKeyword ("new") :
                rule.rule_mode = "new"
                self.nextToken ()
             elif self.isKeyword ("modify") :
                rule.rule_mode = "modify"
                self.nextToken ()
             elif self.isKeyword ("select") or self.isKeyword ("choose") or self.isKeyword ("return") :
                rule.rule_mode = "select"
                self.nextToken ()
             else :
                rule.rule_mode = "new"

             rule.rule_type = self.readIdentifier ("Type name expected")

             if self.isSeparator (':') :
                self.nextToken ()
                rule.super_type = self.readIdentifier ("Super-type expected")

             if self.isSeparator (',') :
                self.nextToken ()
                rule.tag_name = self.readIdentifier ("Tag identifier expected")
                self.checkSeparator ('=')
                rule.tag_value = self.readIdentifier ("Tag value expected")
                if rule.rule_mode != "new" :
                   self.error ("Tag only allowed for \"new\" mode")

          self.checkSeparator ('>')

       "second < > directive"
       if self.isSeparator ('<') :
          self.nextToken ()
          if self.isKeyword ("start") :
             rule.start = True
             self.nextToken ()
          else :
             self.error ("Unknown directive")
          self.checkSeparator ('>')

   # -- item directive --

   def itemDirective (self, rule, alt, opt) :
       while self.isSeparator ('<') :
          self.nextToken ()

          if self.isKeyword ("new") :
             self.nextToken ()
             # add New to this alternative
             item = New ()
             item.new_type = self.readIdentifier ("Type identifier expected")
             self.checkSeparator (':')
             item.new_super_type = self.readIdentifier ("Type identifier expected")
             alt.items.append (item)
             rule.new_directive = item
             alt.leading_required = False
             # if self.isSeparator (',') :
             #    self.nextToken ()
             #    rule.tag_name = self.readIdentifier ("Tag identifier expected")
             #    self.checkSeparator ('=')
             #    rule.tag_value = self.readIdentifier ("Tag value expected")

          elif self.isKeyword ("store") :
             self.nextToken ()
             name = self.readIdentifier ("Field identifier expected")
             self.checkSeparator (':')
             type = self.readIdentifier ("Type identifier expected")
             if rule.new_directive != None :
                rule.new_directive.store_name = name
                rule.new_directive.store_type = type
             else :
                rule.store_name = name
                rule.store_type = type

          elif self.isKeyword ("add") :
             self.nextToken ()
             opt.add = True
             opt.need_nonterminal = True

          elif self.isKeyword ("modify") :
             self.nextToken ()
             opt.modify = True
             opt.need_nonterminal = True

          elif self.isKeyword ("set") :
             self.nextToken ()
             variable = self.readIdentifier ("Variable identifier expected")
             self.checkSeparator ('=')
             value = self.readIdentifier ("Value expected")
             if value == "true" :
                value = "True"
             if value == "false" :
                value = "False"
             # add Assign to this alternative
             item = Assign ()
             item.variable = variable
             item.value = value
             alt.items.append (item)

          elif self.isKeyword ("execute") :
             self.nextToken ()
             name = self.readIdentifier ("Method identifier expected")
             # add Execute to this alternative
             item = Execute ()
             item.name = name
             alt.items.append (item)

          elif self.isKeyword ("execute_no_param") :
             self.nextToken ()
             name = self.readIdentifier ("Method identifier expected")
             # add Execute to this alternative
             item = Execute ()
             item.name = name
             item.no_param = True
             alt.items.append (item)

          elif self.isKeyword ("silent") :
             self.nextToken ()
             # set silent field in this alternative
             alt.silent = True

          elif ( self.isKeyword ("indent") or
                 self.isKeyword ("unindent") or
                 self.isKeyword ("no_space") or
                 self.isKeyword ("new_line") or
                 self.isKeyword ("empty_line") ) :
             name = self.tokenText
             self.nextToken ()
             # add Style to this alternative
             item = Style ()
             item.name = name
             alt.items.append (item)
          else :
             self.error ("Unknown directive " + self.tokenText)

          self.checkSeparator ('>')

   # -- source code position --

   def setPosition (self, item) :
       item.src_file = self.tokenFileInx
       item.src_line = self.tokenLineNum
       item.src_column = self.tokenColNum
       item.src_pos = self.tokenByteOfs

   def rememberPosition (self) :
       return (self.tokenFileInx, self.tokenLineNum, self.tokenColNum, self.tokenByteOfs)

   def storePosition (self, item, value) :
       item.src_file = value [0]
       item.src_line = value [1]
       item.src_column = value [2]
       item.src_pos = value [3]

   def updatePosition (self, item) :
       "set position for error reporting"
       inp = self.file_input
       if inp != None :
          if inp.fileInx == item.src_file :
             inp.lineNum = item.src_line
             inp.colNum = item.src_column
             inp.byteOfs = item.src_pos

   # -- directives --

   def structDirective (self) :
       struct = StructDecl ()
       struct.struct_name = self.readIdentifier ("Type identifier expected")
       if self.isSeparator (':') :
          self.nextToken ()
          struct.super_type = self.readIdentifier ("Super-type identifier expected")
       self.struct_decl.append (struct)
       if self.isSeparator (',') :
          self.nextToken ()
          struct.tag_name = self.readIdentifier ("Tag identifier expected")
          self.checkSeparator ('=')
          struct.tag_value = self.readIdentifier ("Tag value expected")
       if self.isSeparator ('{') :
          self.nextToken ()
          while not self.isSeparator ('}') :
             field = FieldDecl ()
             field.field_type = self.readIdentifier ("Type identifier expected")
             field.field_name = self.readIdentifier ("Field identifier expected")
             self.checkSeparator (';')
             struct.fields.append (field)
          self.checkSeparator ('}')
       return struct

   def addMethod (self, func_dict, rule_name, method_name) :
       if rule_name in func_dict :
          self.error ("Cannot register " + method_name + ", rule " + rule_name + "has already registered method " + func_dict [rule_name])
       func_dict [rule_name] = method_name
       self.check_rules.append (rule_name)

   def rememberMethod (self, func_dict, method_name) :
       cont = True
       while cont :
          rule_name = self.readIdentifier ("Rule identifier expected")
          self.addMethod (func_dict, rule_name, method_name)
          cont = False
          if self.isSeparator (',') :
             self.nextToken ()
             cont = True

   def rememberMethods (self, begin_func, end_func) :
       cont = True
       while cont :
          rule_name = self.readIdentifier ("Rule identifier expected")
          if begin_func != "" :
             self.addMethod (self.execute_on_begin, rule_name, begin_func)
          if end_func != "" :
             self.addMethod (self.execute_on_end, rule_name, end_func)
          cont = False
          if self.isSeparator (',') :
             self.nextToken ()
             cont = True

   def executeOnBeginEnd (self) :
       begin_func = ""
       if not self.isSeparator (',') :
          begin_func = self.readIdentifier ("Method identifier expected")
       self.checkSeparator (',')

       end_func = ""
       if not self.isSeparator (':') :
          end_func = self.readIdentifier ("Method identifier expected")
       self.checkSeparator (':')

       self.rememberMethods (begin_func, end_func)

   def executeOnBegin (self) :
       begin_func = self.readIdentifier ("Method identifier expected")
       self.checkSeparator (':')
       self.rememberMethods (begin_func, "")

   def executeOnEnd (self) :
       end_func = self.readIdentifier ("Method identifier expected")
       self.checkSeparator (':')
       self.rememberMethods ("", end_func)

   def executeOnChoose (self) :
       func_name = self.readIdentifier ("Method identifier expected")
       self.checkSeparator (':')
       self.rememberMethod (self.execute_on_choose, func_name)

   def executeOnBeginNoParam (self) :
       func_name = self.readIdentifier ("Method identifier expected")
       self.checkSeparator (':')
       self.rememberMethod (self.execute_on_begin_no_param, func_name)

   def executeOnEntryNoParam (self) :
       func_name = self.readIdentifier ("Method identifier expected")
       self.checkSeparator (':')
       self.rememberMethod (self.execute_on_entry_no_param, func_name)

   def executeOnForkNoParam (self) :
       func_name = self.readIdentifier ("Method identifier expected")
       self.checkSeparator (':')
       self.rememberMethod (self.execute_on_fork_no_param, func_name)

   def predicateOnChoose (self) :
       func_name = self.readIdentifier ("Method identifier expected")
       self.checkSeparator (':')
       self.rememberMethod (self.predicate_on_choose, func_name)

   def readRuleList (self) :
       result = [ ]

       name = self.readIdentifier ("Rule identifier expected")
       result.append (name)
       self.check_rules.append (name)

       while self.isSeparator (',') :
          self.nextToken ()
          name = self.readIdentifier ("Rule identifier expected")
          result.append (name)
          self.check_rules.append (name)

       return result

   def readStructureName (self) :
       name = self.readIdentifier ("Structure identifier expected")

       struct = None
       for item in self.struct_decl :
           if item.struct_name == name :
              struct = item

       if struct == None :
          self.error ("Unknown structure " + name)
       return name

   def readGroup (self) :
       name = self.readIdentifier ("Group identifier expected")

       group = None
       for item in self.group_list :
          if item.group_name == name :
             group = item

       if group == None :
          self.error ("Unknown group " + name)

       return group

   def groupDirective (self) :
       " < group expression * CmmExpr > "
       " < group statement  % CmmStat : stat, flexible_stat, declaration, member_item / nested_stat > "
       group = GroupDecl ()
       group.group_name = self.readIdentifier ("Group identifier expected")

       if self.isSeparator ('*') :
          self.nextToken ()
          group.from_type = self.readStructureName ()
       elif self.isSeparator ('%') :
          self.nextToken ()
          group.ctrl_type = self.readStructureName ()

       if self.isSeparator (':') :
          self.nextToken ()
          group.include_list = self.readRuleList ()

       if self.isSeparator ('/') :
          self.nextToken ()
          group.exclude_list = self.readRuleList ()

       self.group_list.append (group)

   def artificialDirective (self) :
       " < artificial statement, text_stat, CmmTextStat > "
       artificial = ArtificialDecl ()
       group = self.readGroup ()
       group.artificial_list.append (artificial)
       self.checkSeparator (',')
       artificial.call_name = self.readIdentifier ("Sub-rule identifier expected")
       self.checkSeparator (',')
       artificial.struct_name = self.readStructureName ()

   def globalDirective (self) :
       while self.isSeparator ('<') :
          self.nextToken ()
          if self.isKeyword ("struct") :
             self.nextToken ()
             self.structDirective ()
          elif self.isKeyword ("execute_on_begin_end") :
             self.nextToken ()
             self.executeOnBeginEnd ()
          elif self.isKeyword ("execute_on_begin") :
             self.nextToken ()
             self.executeOnBegin ()
          elif self.isKeyword ("execute_on_end") :
             self.nextToken ()
             self.executeOnEnd ()
          elif self.isKeyword ("execute_on_begin_no_param") :
             self.nextToken ()
             self.executeOnBeginNoParam ()
          elif self.isKeyword ("execute_on_entry_no_param") :
             self.nextToken ()
             self.executeOnEntryNoParam ()
          elif self.isKeyword ("execute_on_fork_no_param") :
             self.nextToken ()
             self.executeOnForkNoParam ()
          elif self.isKeyword ("predicate_on_choose") :
             self.nextToken ()
             self.predicateOnChoose ()
          elif self.isKeyword ("execute_on_choose") :
             self.nextToken ()
             self.executeOnChoose ()
          elif self.isKeyword ("group") :
             self.nextToken ()
             self.groupDirective ()
          elif self.isKeyword ("artificial") :
             self.nextToken ()
             self.artificialDirective ()
          else :
             self.error ("Unknown global directive")
          self.checkSeparator ('>')

   # -- rules --

   def parseRules (self) :
       while not self.isEndOfSource () :
          self.globalDirective ()
          if not self.isEndOfSource () :
             self.parseRule ()

   def parseRule (self) :
       rule = Rule ()

       rule.name = self.readIdentifier ("Rule identifier expected")
       self.setPosition (rule)

       self.ruleDirective (rule)
       self.checkSeparator (':')

       rule.expr = self.parseExpression (rule, 1)

       self.checkSeparator (';')
       self.rules.append (rule)

   # -- expression --

   def parseExpression (self, rule, level) :
       expr = Expression ()
       self.setPosition (expr)

       if level == 2 :
          if rule.rule_mode == "select" :
             expr.continue_expr = True
             expr.expr_link = rule.above_alt

       alt = self.parseAlternative (rule, level)
       expr.alternatives.append (alt)

       while self.isSeparator ('|') :
          self.nextToken ()

          alt = self.parseAlternative (rule, level)
          expr.alternatives.append (alt)

       return expr

   def parseAlternative (self, rule, level) :
       alt = Alternative ()
       alt.level = level
       self.setPosition (alt)

       if level == 1 :
          if rule.rule_mode == "select" :
             alt.select_alt = True
             rule.above_alt = alt
             alt.leading_required = True

       if level == 2 :
          if rule.rule_mode == "select" :
             alt.continue_alt = True
             alt.alt_link = rule.above_alt
             alt.leading_required = True

       opt = Options ()
       self.itemDirective (rule, alt, opt)

       while not self.isSeparator ('|') and not self.isSeparator (')') and not self.isSeparator (']') and not self.isSeparator (';') :

          if self.token == self.identifier :
             item = self.parseNonterminal (rule, alt, opt)
             alt.items.append (item)

          elif self.token == self.character_literal or self.token == self.string_literal :
             if opt.need_nonterminal :
                self.error ("Nonterminal expected")
             item = self.parseTerminal ()
             alt.items.append (item)

          elif self.isSeparator ('(') :
             if rule.predicate_level == 0 :
                if opt.need_nonterminal :
                   self.error ("nonterminal expected")
                if alt.leading_required :
                   self.error ("missing nonterminal (in the beginning of sub-expression)")
             ebnf = self.parseEbnf (rule, level)

             if alt.select_alt :
                alt.continue_ebnf = ebnf
             alt.items.append (ebnf)

          elif self.isSeparator ('[') :
             if alt.predicate != None :
                self.error ("Syntactic predicate for this alternative already defined")
             self.checkSeparator ('[')
             rule.predicate_level = rule.predicate_level + 1
             alt.predicate = self.parseExpression (rule, level+1)
             rule.predicate_level = rule.predicate_level - 1
             self.checkSeparator (']')
             self.checkSeparator ('=')
             self.checkSeparator ('>')

          elif self.isSeparator ('{') :
             self.nextToken ()
             if alt.semantic_predicate != None :
                self.error ("Semantic predicate for this alternative already defined")
             alt.semantic_predicate = self.readIdentifier ("Function identifier expected")
             if self.isSeparator ('(') :
                self.nextToken ()
                self.checkSeparator (')')
             self.checkSeparator ('}')
             self.checkSeparator ('?')

          else :
             self.error ("Unknown grammar item")

          # inside while loop
          opt = Options ()
          self.itemDirective (rule, alt, opt)

       # after while lopp
       if rule.predicate_level == 0 :
          if opt.need_nonterminal :
             self.error ("Nonterminal expected")

          if alt.leading_required :
             self.error ("Missing nonterminal (for rule with select attribute)")

       rule.new_directive = None # !?
       return alt

   def parseEbnf (self, rule, level) :
       item = Ebnf ()

       self.setPosition (item)
       self.checkSeparator ('(')
       item.expr = self.parseExpression (rule, level+1)
       self.checkSeparator (')')

       if self.isSeparator ('?') :
          item.mark = '?'
          self.nextToken ()
       elif self.isSeparator ('+') or self.isSeparator ('@') :
          item.mark = '+'
          self.nextToken ()
       elif self.isSeparator ('*') :
          item.mark = '*'
          self.nextToken ()

       return item

   def parseSyntacticPredicate (self, rule, level) :
       # item = SyntacticPredicate ()

       # self.setPosition (item)
       self.checkSeparator ('[')
       item = self.parseExpression (rule, level+2) # increment level to disable leading_required
       self.checkSeparator (']')
       self.checkSeparator ('=')
       self.checkSeparator ('>')

       return item

   def parseNonterminal (self, rule, alt, opt) :

       pos = self.rememberPosition ()
       variable = ""
       rule_name = self.readIdentifier ()

       if self.isSeparator (':') :
          self.nextToken ()
          variable = rule_name
          rule_name = self.readIdentifier ("Rule identifier expected")

       if rule_name in self.multiterminals :
          item = Terminal ()
          self.storePosition (item, pos)
          item.variable = variable
          item.multiterminal_name = rule_name
          if opt.add or opt.modify :
             self.error ("<add> or <modify> not allowed before multiterminal")
          if rule.predicate_level == 0 :
             if alt.leading_required :
                self.error ("Missing nonterminal (for rule with select or choose attribute) (and multiterminal found)")
       else :
          item = Nonterminal ()
          self.storePosition (item, pos)

          item.variable = variable
          item.rule_name = rule_name

          item.add = opt.add
          item.modify = opt.modify

          # opt.need_nonterminal = False

          if alt.leading_required  :
             alt.leading_required = False
             if alt.select_alt :
                item.select_item = True
                item.item_link = alt
                alt.select_nonterm = item
             if alt.continue_alt :
                item.continue_item = True
             if item.variable != "" :
                if rule.predicate_level == 0 :
                   self.error ("Variable identifier not allowed for first nonterminal (in rule with select or choose attribute)")

          if item.add or item.modify :
             if item.variable != "" :
                self.error ("Variable identifier not allowed after <add> or <modify> directive")

          if item.add :
             rule.add_used = True

       return item

   def parseTerminal (self) :
       item = Terminal ()
       self.setPosition (item)
       if self.token != self.character_literal and self.token != self.string_literal :
          self.error ("string expected")
       item.text = self.tokenText
       self.nextToken ()
       return item

# --------------------------------------------------------------------------

if __name__ == "__main__" :
    grammar = Grammar ()
    grammar.openFile ("pas.g")
    grammar.parseRules ()
    for rule in grammar.rules :
       print (rule.name)

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
