
# c2py.py

from __future__ import print_function

from output import Output
from code import *
from cmm_parser import *
from input import quoteString
from util import use_pyside2, use_qt5

# --------------------------------------------------------------------------

class ToPy (Output) :

   def __init__ (self) :
       super (ToPy, self).__init__ ()
       self.class_stack = [ ]
       self.empty_stack = [ True ] # !?

   def openBlock (self) :
       self.empty_stack.append (True)

   def addBlockItem (self) :
       self.empty_stack[-1] = False

   def closeBlock (self) :
       return self.empty_stack.pop ()

   def put_dot (self) :
       self.style_no_space ()
       self.send (".")
       self.style_no_space ()

   # -----------------------------------------------------------------------

   def custom_prefix (self, obj) :
       ctx = obj.item_context
       if isinstance (ctx, Class) :
          self.send ("self")
          self.put_dot ()

   def custom_block_statement (self, param) :
       return False

   def custom_begin_of_constructor (self, cls, obj) :
       pass

   def custom_variable_initialization (self, simple_item) :
       self.send ("=")
       self.send ("None")

   def custom_variable_placement (self, simple_item) :
       pass

   # -----------------------------------------------------------------------

   def send_simple_name (self, param) :
       self.send (param.id)

   def send_qualified_name (self, param) :
       if param.kind == param.simpleName :
          if getattr (param, "item_decl", None) != None :
             self.custom_prefix (param.item_decl)
       if param.kind == param.simpleName :
          self.send_simple_name (param)
       elif param.kind == param.globalName : # !?
          self.send_qualified_name (param.inner_name)
       elif param.kind == param.compoundName :
          self.send_qualified_name (param.left)
          self.put_dot ()
          self.send_qualified_name (param.right)
       elif param.kind == param.contName :
          self.send_simple_name (param)

   # -----------------------------------------------------------------------

   def send_expr_list (self, param) :
       first = True
       for item in param.items :
           if not first :
              self.send (",")
           first = False
           self.send_expr (item)

   # -----------------------------------------------------------------------

   def send_nested_stat (self, param) :
       self.style_indent ()
       self.send_stat (param)
       self.style_unindent ()

   def send_empty_stat (self, param) :
       self.send ("pass")
       self.style_new_line ()

   def send_compound_stat (self, param) :
       self.openBlock ()
       for item in param.items :
           if item.mode != item.emptyStat :
              self.send_stat (item)
       empty = self.closeBlock ()
       if empty :
          self.send ("pass")
          self.style_new_line ()

   def send_if_stat (self, param) :
       self.addBlockItem ()
       self.send ("if")
       self.send_expr (param.cond)
       self.send (":")
       self.style_new_line ()
       self.send_nested_stat (param.then_stat)
       if param.else_stat != None :
          self.send ("else")
          self.send (":")
          self.style_new_line ()
          self.send_nested_stat (param.else_stat)

   def send_while_stat (self, param) :
       self.addBlockItem ()
       self.send ("while")
       self.send_expr (param.cond)
       self.send (":")
       self.style_new_line ()
       self.send_nested_stat (param.body)

   def send_for_stat (self, param) :
       self.addBlockItem ()
       if param.iter_expr != None :
          self.send ("for")
          if param.from_expr != None :
             self.send_condition (param.from_expr)
          self.send ("in")
          self.send_expr (param.iter_expr)
          self.send (":")
          self.style_new_line ()
          self.send_nested_stat (param.body)
       else:
          if param.from_expr != None :
             self.send_condition (param.from_expr)
          self.style_new_line ()
          self.send ("while")
          if param.to_expr != None :
             self.send_expr (param.to_expr)
          else :
             self.send ("True")
          self.send (":")
          self.style_new_line ()
          self.style_indent ()
          self.send_stat (param.body)
          if param.cond_expr != None :
             self.send_expr (param.cond_expr)
             self.style_new_line ()
          self.style_unindent ()

   def send_return_stat (self, param) :
       self.addBlockItem ()
       self.send ("return")
       if param.return_expr != None :
          self.send_expr (param.return_expr)
       self.style_new_line ()

   # -----------------------------------------------------------------------

   def send_declaration_list (self, param) :
       for item in param.items :
          self.send_declaration (item)

   def send_type_specifiers (self, param) :
       # if param.kind == param.simpleName : # !?
       #    self.send_qualified_name (param)
       # elif param.kind == param.globalName : # !?
       #    self.send_qualified_name (param)
       # elif param.basic_name != None :
       #    self.send_qualified_name (param.basic_name)
       if param.a_short or param.a_int or param.a_long :
          self.send ("int")
       elif param.a_bool :
          self.send ("bool")
       elif param.a_char == True :
          self.send ("char")
       elif param.a_wchar == True :
          self.send ("wchar_t")
       elif param.a_float == True :
          self.send ("float")
       elif param.a_double == True :
          self.send ("double")
       elif param.a_void == True :
          self.send ("void")

   def send_parameter_declaration_list (self, param) :
       first = True
       if len (self.class_stack) != 0 :
          self.send ("self")
          first = False
       for item in param.items :
           if not first :
              self.send (",")
           first = False
           self.send_parameter_declaration (item)

   def send_parameter_declaration (self, param) :
       if param.kind == param.plainParam :
          self.send_declarator (param.decl)
          if param.init != None :
             self.send_initializer (param.init)

   def send_simple_stat (self, param) :
       self.addBlockItem ()
       self.send_expr (param.inner_expr)
       self.style_new_line ()

   def send_block_stat (self, param) :
       done = self.custom_block_statement (param)
       if not done :
          self.addBlockItem ()
          self.send_expr (param.inner_expr)
          self.style_new_line ()

   def send_simple_declaration (self, param, new_line = True) :
       for simple_item in param.items :
           self.send_simple_item (simple_item, new_line)

   def send_simple_item (self, simple_item, new_line = True) :
       obj = simple_item.item_ref
       if not obj.is_function :
          if not isinstance (obj.item_context, Class) :
             self.addBlockItem ()
             var = obj
             self.send_declarator (simple_item.decl)
             if simple_item.init != None :
                self.send_initializer (simple_item.init)
             else :
                self.custom_variable_initialization (obj)
             if new_line :
                self.style_new_line ()
             self.custom_variable_placement (var)
             if var.item_body != None :
                self.send_compound_stat (var.item_body)
       else :
         if obj.item_body != None :
            self.addBlockItem ()
            self.openSection (obj)
            self.send ("def")
            if obj.is_constructor :
               self.send ("__init__")
            self.send_declarator (simple_item.decl)
            self.send (":")
            self.style_new_line ()
            self.style_indent ()
            if obj.is_constructor :
               self.custom_begin_of_constructor (obj.item_context, obj)
            self.send_compound_stat (obj.item_body)
            self.style_unindent ()
            self.style_empty_line ()
            self.closeSection ()

   def send_condition (self, cond) :
       if cond.kind == cond.valueCondition :
          self.send_expr (cond.inner_expr)
       elif cond.kind == cond.declarationCondition :
          any = False
          for item in cond.items :
            if any :
               self.send (",")
            self.send_simple_item (item)
            any = True

   def class_base_name (self, cls) :
       result = ""
       if isinstance (cls, Class) :
          base_list = cls.item_code.base_list
          if base_list != None :
             for item in base_list.items :
                 result = item.from_cls.id # !?
       return result

   def send_declarator (self, decl) :
       if decl.kind == decl.basicDeclarator :
          name = decl.qual_name
          if name.kind == name.simpleName :
             self.send (name.id)
       self.send_func_specifier_list (decl.cont_spec)

   def send_function_specifier (self, param) :
       self.send ("(")
       self.send_parameter_declaration_list (param.parameters)
       self.send (")")

   def send_func_specifier_list (self, param) :
       if param != None :
          for item in param.items :
             if isinstance (item, CmmFunctionSpecifier) :
                self.send_function_specifier (item)

   def send_type_id (self, param) :
       self.send_type_specifiers (param.type_spec)
       # self.send_abstract_declarator (param.decl)

   def send_initializer (self, param) :
       self.send ("=")
       self.send_initializer_item (param.value)

   def send_initializer_item (self, param) :
       if isinstance (param, CmmInitSimple) :
          self.send_expr (param.inner_expr)
       elif isinstance (param, CmmInitList) :
          self.send_initializer_list (param)

   def send_initializer_list (self, param) :
       inx = 0
       cnt = len (param.items)
       self.send ("[") # !?
       self.style_indent ()
       for item in param.items :
          self.send_initializer_item (item)
          inx = inx + 1
          if inx < cnt :
             self.send (",")
             self.style_new_line ()
       self.style_unindent ()
       self.send ("]")

   # -----------------------------------------------------------------------

   def default_constructor (self, cls) :
       self.send ("def")
       self.send ("__init__")
       self.send ("(")
       self.send ("self")
       self.send (")")
       self.send (":")
       self.style_new_line ()
       self.style_indent ()
       self.openBlock ()
       self.custom_begin_of_constructor (cls, None)
       empty = self.closeBlock ()
       if empty :
          self.send ("pass")
          self.style_new_line ()
       self.style_unindent ()
       self.style_empty_line ()

   def send_class_declaration (self, param) :
       cls = param.item_ref
       if not cls.skip_code :
          self.class_stack.append (cls)

          self.send ("class")
          self.send_simple_name (param.simp_name)

          if param.members != None :
             if param.base_list != None :
                self.send ("(")
                self.send_base_specifier_list (param.base_list)
                self.send (")")

          self.send (":")
          self.style_new_line ()

          self.openSection (cls)
          self.style_indent ()
          self.openBlock ()

          "default constructor"
          any = False
          for item in cls.item_list :
              if getattr (item, "is_constructor", False) :
                 any = True
          if not any :
             self.addBlockItem ()
             self.default_constructor (cls)

          "send member items"
          if param.members != None :
             for item in param.members.items :
                 if item.mode == item.visibilityDecl :
                    pass
                 elif item.mode == item.simpleDecl :
                    self.send_simple_declaration (item)
                 # else : # !?
                 #    self.send ("another member item")

          "additional (generated) methods"
          for method in cls.methods :
              self.addBlockItem ()
              self.send ("def")
              self.send (method.name)
              self.send ("(")
              self.send ("self")
              self.send (")")
              self.send (":")
              self.style_new_line ()
              self.style_indent ()
              self.send_compound_stat (method.body)
              self.style_unindent ()
              self.style_empty_line ()

          empty = self.closeBlock ()
          if empty :
             self.send ("pass")
             self.style_new_line ()
          self.style_unindent ()
          self.closeSection ()
          self.class_stack.pop ()

   def send_base_specifier_list (self, param) :
       first = True
       for item in param.items :
          if not first :
             self.send (",")
          first = False
          self.send_base_specifier (item)

   def send_base_specifier (self, param) :
       self.send_qualified_name (param.from_cls)

   def send_ctor_initializer (self, param) :
       for item in param.items :
          self.send_member_initializer (item)

   def send_member_initializer (self, param) :
       self.send_qualified_name (param.qual_name)
       self.send ("=")
       self.send_expr_list (param.params)
       self.style_new_line ()

   # -----------------------------------------------------------------------

   def send_empty_declaration (self, param) :
       pass

   def send_enum_declaration (self, param) :
       pass

   def send_namespace_declaration (self, param) :
       self.send_declaration_list (param.body)

   # -----------------------------------------------------------------------

   def send_ident_expression (self, param) :
       ident = getattr (param, "id", "")
       if ident == "true" :
          self.send ("True")
       elif ident == "false" :
          self.send ("False")
       else :
          self.send_qualified_name (param)

   # -----------------------------------------------------------------------

   def send_expr (self, expr) :
       if expr.kind == expr.simpleName : # !?
          self.send_ident_expression (expr)
       if expr.kind == expr.globalName : # !?
          self.send_ident_expression (expr)
       if expr.kind == expr.compoundName:
          self.send_ident_expression (expr)
       if expr.kind == expr.intValue :
          self.send (expr.value)
       if expr.kind == expr.realValue :
          self.send (expr.value)
       if expr.kind == expr.charValue :
          self.sendChr (expr.value)
       if expr.kind == expr.stringValue:
          self.sendStr (expr.value)
          for item in expr.items :
             self.sendStr (item.value)
       if expr.kind == expr.thisExp:
          self.send ("self")
       if expr.kind == expr.subexprExp:
          self.send ("(")
          self.send_expr (expr.param)
          self.send (")")
       if expr.kind == expr.modernCastExp :
          self.send_expr (expr.param)
       if expr.kind == expr.typeIdExp:
          self.send ("typeid")
          self.send ("(")
          self.send_expr (expr.value)
          self.send (")")
       if expr.kind == expr.typeName:
          self.send ("typename")
          self.send_qualified_name (expr.qual_name)
       if expr.kind == expr.typeSpec :
          self.send_type_specifiers (expr)
       if expr.kind == expr.indexExp:
          self.send_expr (expr.left)
          self.send ("[")
          self.send_expr (expr.param)
          self.send ("]")
       if expr.kind == expr.callExp:
          self.send_expr (expr.left)
          self.send ("(")
          self.send_expr_list (expr.param_list)
          self.send (")")
       if expr.kind == expr.fieldExp:
          self.send_expr (expr.left)
          self.style_no_space ()
          self.send (".")
          self.style_no_space ()
          self.send_simple_name (expr.simp_name)
       if expr.kind == expr.ptrFieldExp:
          self.send_expr (expr.left)
          self.style_no_space ()
          self.send (".")
          self.style_no_space ()
          self.send_simple_name (expr.simp_name)
       if expr.kind == expr.postIncExp:
          self.send_expr (expr.left)
          self.send ("++")
       if expr.kind == expr.postDecExp:
          self.send_expr (expr.left)
          self.send ("--")
       if expr.kind == expr.incExp:
          self.send ("++")
          self.send_expr (expr.param)
       if expr.kind == expr.decExp:
          self.send ("--")
          self.send_expr (expr.param)
       if expr.kind == expr.derefExp:
          self.send ("*")
          self.send_expr (expr.param)
       if expr.kind == expr.addrExp:
          # self.send ("&")
          self.send_expr (expr.param)
       if expr.kind == expr.plusExp:
          self.send ("+")
          self.send_expr (expr.param)
       if expr.kind == expr.minusExp:
          self.send ("-")
          self.send_expr (expr.param)
       if expr.kind == expr.bitNotExp:
          self.send ("~")
          self.send_expr (expr.param)
       if expr.kind == expr.logNotExp:
          self.send ("not")
          self.send_expr (expr.param)
       if expr.kind == expr.sizeofExp:
          self.send ("sizeof")
          self.send ("(")
          self.send_expr (expr.value)
          self.send (")")
       if expr.kind == expr.newExp:
          # send ("new")
          if expr.type1 != None :
             self.send_expr (expr.type1.type_spec)
          elif expr.type2 != None :
             self.send ("(")
             self.send_type_id (expr.type2)
             self.send (")")
          self.send ("(")
          if expr.init_list != None :
             self.send_expr_list (expr.init_list)
          self.send (")")
       if expr.kind == expr.deleteExp:
          self.send ("delete")
          if expr.a_array == True :
             self.send ("[")
             self.send ("]")
          self.send_expr (expr.param)
       if expr.kind == expr.typecastExp:
          self.send ("type_cast")
          self.send ("<")
          self.send_type_id (expr.type)
          self.send (">")
          self.send ("(")
          self.send_expr (expr.param)
          self.send (")")
       if expr.kind == expr.dotMemberExp :
          self.send_expr (expr.left)
          self.send (".*")
          self.send_expr (expr.right)
       if expr.kind == expr.arrowMemberExp :
          self.send_expr (expr.left)
          self.send ("->*")
          self.send_expr (expr.right)
       if expr.kind == expr.mulExp :
          self.send_expr (expr.left)
          self.send ("*")
          self.send_expr (expr.right)
       if expr.kind == expr.divExp :
          self.send_expr (expr.left)
          self.send ("/")
          self.send_expr (expr.right)
       if expr.kind == expr.modExp :
          self.send_expr (expr.left)
          self.send ("%")
          self.send_expr (expr.right)
       if expr.kind == expr.addExp :
          self.send_expr (expr.left)
          self.send ("+")
          self.send_expr (expr.right)
       if expr.kind == expr.subExp :
          self.send_expr (expr.left)
          self.send ("-")
          self.send_expr (expr.right)
       if expr.kind == expr.shlExp :
          self.send_expr (expr.left)
          self.send ("<<")
          self.send_expr (expr.right)
       if expr.kind == expr.shrExp :
          self.send_expr (expr.left)
          self.send (">>")
          self.send_expr (expr.right)
       if expr.kind == expr.ltExp :
          self.send_expr (expr.left)
          self.send ("<")
          self.send_expr (expr.right)
       if expr.kind == expr.gtExp :
          self.send_expr (expr.left)
          self.send (">")
          self.send_expr (expr.right)
       if expr.kind == expr.leExp :
          self.send_expr (expr.left)
          self.send ("<=")
          self.send_expr (expr.right)
       if expr.kind == expr.geExp :
          self.send_expr (expr.left)
          self.send (">=")
          self.send_expr (expr.right)
       if expr.kind == expr.eqExp :
          self.send_expr (expr.left)
          self.send ("==")
          self.send_expr (expr.right)
       if expr.kind == expr.neExp :
          self.send_expr (expr.left)
          self.send ("!=")
          self.send_expr (expr.right)
       if expr.kind == expr.bitAndExp :
          self.send_expr (expr.left)
          self.send ("&")
          self.send_expr (expr.right)
       if expr.kind == expr.bitXorExp :
          self.send_expr (expr.left)
          self.send ("^")
          self.send_expr (expr.right)
       if expr.kind == expr.bitOrExp :
          self.send_expr (expr.left)
          self.send ("|")
          self.send_expr (expr.right)
       if expr.kind == expr.logAndExp :
          self.send_expr (expr.left)
          self.send ("and")
          self.send_expr (expr.right)
       if expr.kind == expr.logOrExp :
          self.send_expr (expr.left)
          self.send ("or")
          self.send_expr (expr.right)
       if expr.kind == expr.assignExp :
          self.send_expr (expr.left)
          self.send ("=")
          self.send_expr (expr.right)
       if expr.kind == expr.addAssignExp :
          self.send_expr (expr.left)
          self.send ("+=")
          self.send_expr (expr.right)
       if expr.kind == expr.subAssignExp :
          self.send_expr (expr.left)
          self.send ("-=")
          self.send_expr (expr.right)
       if expr.kind == expr.mulAssignExp :
          self.send_expr (expr.left)
          self.send ("*=")
          self.send_expr (expr.right)
       if expr.kind == expr.divAssignExp :
          self.send_expr (expr.left)
          self.send ("/=")
          self.send_expr (expr.right)
       if expr.kind == expr.modAssignExp :
          self.send_expr (expr.left)
          self.send ("%=")
          self.send_expr (expr.right)
       if expr.kind == expr.shlAssignExp :
          self.send_expr (expr.left)
          self.send ("<<=")
          self.send_expr (expr.right)
       if expr.kind == expr.shrAssignExp :
          self.send_expr (expr.left)
          self.send (">>=")
          self.send_expr (expr.right)
       if expr.kind == expr.andAssignExp :
          self.send_expr (expr.left)
          self.send ("&=")
          self.send_expr (expr.right)
       if expr.kind == expr.xorAssignExp :
          self.send_expr (expr.left)
          self.send ("^=")
          self.send_expr (expr.right)
       if expr.kind == expr.orAssignExp :
          self.send_expr (expr.left)
          self.send ("|=")
          self.send_expr (expr.right)
       if expr.kind == expr.condExp :
          self.send_expr (expr.left)
          self.send ("?")
          self.send_expr (expr.middle)
          self.send (":")
          self.send_expr (expr.right)
       if expr.kind == expr.colonExp :
          self.send_expr (expr.left)
          self.send (":")
          self.send_expr (expr.right)
       if expr.kind == expr.commaExp :
          self.send_expr (expr.left)
          self.send (",")
          self.send_expr (expr.right)
       if expr.kind == expr.throwExp:
          self.send ("throw")
          if expr.param != None :
             self.send_expr (expr.param)

   # -----------------------------------------------------------------------

   def send_stat (self, stat) :
       if stat.mode == stat.simpleStat :
          self.send_simple_stat (stat)
       elif stat.mode == stat.blockStat :
          self.send_block_stat (stat)
       elif stat.mode == stat.simpleDecl :
          self.send_simple_declaration (stat)
       elif stat.mode == stat.emptyStat :
          self.send_empty_stat (stat)
       # elif stat.mode == stat.labeledStat :
       #    self.send_label_stat (stat)
       elif stat.mode == stat.compoundStat :
          self.send_compound_stat (stat)
       elif stat.mode == stat.caseStat :
          self.send_case_stat (stat)
       elif stat.mode == stat.defaultStat :
          self.send_default_stat (stat)
       elif stat.mode == stat.ifStat :
          self.send_if_stat (stat)
       elif stat.mode == stat.switchStat :
          self.send_switch_stat (stat)
       elif stat.mode == stat.whileStat :
          self.send_while_stat (stat)
       elif stat.mode == stat.doStat :
          self.send_do_stat (stat)
       elif stat.mode == stat.forStat :
          self.send_for_stat (stat)
       elif stat.mode == stat.breakStat :
          self.send_break_stat (stat)
       elif stat.mode == stat.continueStat :
          self.send_continue_stat (stat)
       elif stat.mode == stat.returnStat :
          self.send_return_stat (stat)
       elif stat.mode == stat.gotoStat :
          self.send_goto_stat (stat)
       elif stat.mode == stat.tryStat :
          self.send_try_stat (stat)

       elif stat.mode == stat.textStat :
          self.put (stat.text)
       elif stat.mode == stat.eolStat :
          self.putEol ()
       elif stat.mode == stat.indentStat :
          self.incIndent ()
       elif stat.mode == stat.unindentStat :
          self.decIndent ()
       elif stat.mode == stat.emptyLineStat :
          self.style_empty_line ()
       elif stat.mode == stat.cppOnlyStat :
          pass
       elif stat.mode == stat.pythonOnlyStat :
          self.send_stat (stat.inner_stat)

   # -----------------------------------------------------------------------

   def send_declaration (self, decl) :
       if decl.mode == decl.classDecl :
          self.send_class_declaration (decl)
       elif decl.mode == decl.enumDecl :
          self.send_enum_declaration (decl)
       # elif decl.mode == decl.typedefDecl) :
       #    self.send_typedef_declaration (decl)
       # elif decl.mode == decl.friendDecl :
       #    self.send_friend_declaration (decl)
       elif decl.mode == decl.namespaceDecl :
          self.send_namespace_declaration (decl)
       # elif decl.mode == decl.externDecl :
       #    self.send_extern_declaration (decl)
       # elif decl.mode == decl.usingDecl :
       #    self.send_using_declaration (decl)
       # elif decl.mode == decl.templateDecl :
       #   send_template_declaration (decl)
       else :
          self.send_stat (decl)

   # -----------------------------------------------------------------------

   def send_program (self, param) :
       self.send_declaration_list (param)

# --------------------------------------------------------------------------

class ToExtPy (ToPy) :

   def __init__ (self) :
       super (ToExtPy, self).__init__ ()

   def get_expr_value (self, expr) :
       return getattr (expr, "item_value", None)

   def send_expr (self, expr) :
       done = False

       if expr.kind == expr.simpleName : # !?
          if hasattr (expr, "item_decl")  :
             expr.item_value = self.get_expr_value (expr.item_decl)
             " copy loop parameter "

       value = self.get_expr_value (expr)
       if value != None :
          if value == True :
             self.send ("True")
          elif value == False :
             self.send ("False")
          elif isinstance (value, str) :
             self.sendStr (value)
          else :
             self.send (str (value))
          done = True

       if expr.kind == expr.logAndExp :
          left = self.get_expr_value (expr.left)
          if left == True :
             self.send_expr (expr.right)
             done = True
          elif left == False :
             self.send ("False")
             done = True

       if expr.kind == expr.logOrExp :
          left = self.get_expr_value (expr.left)
          if left == False :
             self.send_expr (expr.right)
             done = True
          elif left == True :
             self.send ("True")
             done = True

       if expr.kind == expr.callExp:
          if self.get_expr_name (expr.left) == "write" : # !?
             self.write_function (expr)
          if getattr (expr, "skip_code", False) :
             done = True

       if not done :
          super (ToExtPy, self). send_expr (expr)

   # -----------------------------------------------------------------------

   def send_if_stat (self, stat) :
       done = False

       value = self.get_expr_value (stat.cond)
       if value == True :
          self.send_stat (stat.then_stat)
          done = True
       elif value == False :
          if stat.else_stat != None :
             self.send_stat (stat.else_stat)
          done = True

       if not done :
          super (ToExtPy, self). send_if_stat (stat)

   def send_for_stat (self, stat) :
       done = False

       target = None
       if stat.from_expr != None :
          expr = stat.from_expr
          target = getattr (expr, "item_decl", None)

       if (stat.iter_expr != None) :
          value = self.get_expr_value (stat.iter_expr)
          if value != None:
             for item in value :
                if target != None :
                   target.item_value = item
                self.style_new_line ()
                self.send_stat (stat.body)
             done = True

       if not done :
          super (ToExtPy, self). send_for_stat (stat)

   # -----------------------------------------------------------------------

   def comment (self, txt) :
       self.send (quoteString (txt))
       self.style_new_line ()

   def custom_begin_of_constructor (self, cls, obj) :
       self.send ("super")
       self.send ("(")
       self.send (cls.item_name) # class name
       self.send (",")
       self.send ("self")
       self.send (")")
       self.put_dot ()
       self.send ("__init__")
       self.send ("(")
       first = True
       if obj != None :
          for par in obj.item_list :
              if not first :
                 self.send (",")
              self.send (par.item_name)
              first = False
       self.send (")")
       self.style_new_line ()

       for var in cls.item_list :
          if isinstance (var, Variable) and not var.is_function :
             if var.item_body != None :
                self.comment (var.item_name)
             self.addBlockItem ()
             self.style_no_space ()
             self.send ("self")
             self.put_dot ()
             self.send (var.item_name)
             if getattr (var, "item_init", None) != None : # !?
                self.send ("=")
                if isinstance (var.item_init, list) :
                   self.send ("[")
                   for item in var.item_init :
                      self.send_expr (item)
                      self.send (",")
                   self.send ("]")
                else :
                   self.send_expr (var.item_init)
                self.style_new_line ()
             elif var.item_code.init != None :
                self.send_initializer (var.item_code.init)
             else :
               self.custom_variable_initialization (var)
             self.style_new_line ()
             self.custom_variable_placement (var)

             if var.item_body != None :
                for item in var.item_body.items :
                    if item.mode != item.emptyStat :
                       self.send_stat (item)

       self.custom_construction (cls)

   # -----------------------------------------------------------------------

   def send_simple_item (self, simple_item, new_line = True) :
       obj = simple_item.item_ref
       if not obj.skip_code :
          super (ToExtPy, self). send_simple_item (simple_item, new_line)

   def expand (self, expr) :
       left = expr.left
       decl = left.item_decl
       # for item in decl.parameters.item_list :
       #     item.item_value = "@" + item.item_name
       #     print (item.item_value)
       self.send_compound_stat (decl.item_body)
       # !? parameters

   # -----------------------------------------------------------------------

   def get_name (self, qual_name) :
       result = ""

       if qual_name.kind == qual_name.simpleName :
          result = qual_name.id
       elif qual_name.kind == qual_name.specialName :
          result = qual_name.spec_func.spec_name # !?
       elif qual_name.kind == qual_name.compoundName :
          result = self.get_name (qual_name.left) + "::" + self.get_name (qual_name.right)
       elif qual_name.kind == qual_name.globalName :
           result = "::" + self.get_name (qual_name.inner_name)
       elif qual_name.kind == qual_name.destructorName :
           result = "~" + self.get_name (qual_name.inner_name)
       elif qual_name.kind == qual_name.templateName :
        result = self.get_name (qual_name.left) + "<???>" # !?

       if result == "" :
          result = "???"
       return result

   def get_expr_name (self, expr) :
       return self.get_name (expr)

   def write_function (self, expr) :
       if len (expr.param_list.items) == 1 :
          a = expr.param_list.items [0]
          a = getattr (a, "item_decl", None)
          if isinstance (a, Class) and a.item_code != None:
             self.send_class_declaration (a.item_code)

   # -----------------------------------------------------------------------

   def parameter_names (self, func) :
       result = [ ]
       for item in func.item_code.decl.cont_spec.items :
           if isinstance (item, CmmFunctionSpecifier) :
              for param in item.parameters.items :
                  if param.param_expr != None and param.param_expr.item_value != None : # !?
                     name = param.param_expr.item_value
                  else :
                     name = self.get_name (param.type_spec.basic_name)
                  result.append (name)
       return result

   def custom_icon (self, cls, func) :
       params = self.parameter_names (func)
       self.send ("self.__icon__")
       self.send ("=")
       self.send (quoteString (params [0]))
       self.putEol ()

   def custom_property (self, cls, func) :
       if not hasattr (cls, "properties") :
          cls.properties = True
          self.putLn ("self._properties_ = []")

       params = self.parameter_names (func)
       self.send ("self._properties_.append")
       self.send ("(")
       self.send (quoteString (params [0]))
       self.send (")")
       self.putEol ()

   def custom_combine (self, cls, func) :
       if not hasattr (cls, "combine") :
          cls.combine = True
          self.putLn ("self.__combine__ = []")

       params = self.parameter_names (func)
       self.send ("self.__combine__.append")
       self.send ("((")
       self.send (quoteString (params [0]))
       self.send (",")
       self.send ("self")
       self.put_dot ()
       self.send (params [1])
       self.send ("))")
       self.putEol ()

   def custom_construction (self, cls):
       for item in cls.item_list :
          if isinstance (item, Variable) and item.is_function :
             func = item
             if func.item_name == "icon" : # !?
                self.custom_icon (cls, func)
             if func.item_name == "combine" : # !?
                self.custom_combine (cls, func)
             if func.item_name == "property" : # !?
                self.custom_property (cls, func)

# --------------------------------------------------------------------------

class ToQtPy (ToExtPy) :

   def __init__ (self) :
       super (ToQtPy, self).__init__ ()

   def custom_prefix (self, obj) :
       ctx = obj.item_context
       names = [ ]
       while ctx != None and not isinstance (ctx, Class) :
          if getattr (ctx, "is_function", False) : # !?
             ctx = None
          else:
             if not ctx.hidden_scope : # !?
                names.insert (0, ctx.item_name)
             ctx = ctx.item_context
       if ctx != None :
          self.send ("self")
          self.put_dot ()
       for name in names :
           self.send (name)
           self.put_dot ()

   # -----------------------------------------------------------------------

   def custom_assign (self, expr) :
       done = False

       special = expr.alt_assign
       if special != "" :
          if special.startswith ("<") :
             if special == "<setIcon>" :
                self.custom_prefix (expr.left.item_decl)
                self.send ("setIcon")
                self.send ("(")
                self.send ("QIcon")
                self.put_dot ()
                self.send ("fromTheme")
                self.send ("(")
                self.send_expr (expr.right)
                self.send (")")
                self.send (")")
                self.style_new_line ()
                done = True
             elif special == "<setShortcut>" :
                self.custom_prefix (expr.left.item_decl)
                self.send ("setShortcut")
                self.send ("(")
                self.send_expr (expr.right)
                self.send (")")
                self.style_new_line ()
                done = True
             else :
                self.custom_prefix (expr.left.item_decl)
                if special == "<text>" :
                   self.send ("setText")
                elif special == "<icon>" :
                   self.send ("setIcon")
                elif special == "<foreground>" :
                   self.send ("setForeground")
                elif special == "<background>" :
                   self.send ("setBackground")
                else :
                   self.send (special) # !?
                self.send ("(")
                self.send ("0")
                self.send (",")
                if special == "<icon>" or special == "<setIcon>" :
                   self.send ("QIcon")
                   self.put_dot ()
                   self.send ("fromTheme")
                   self.send ("(")
                   self.send_expr (expr.right)
                   self.send (")")
                elif special == "<foreground>" or special == "<background>":
                   self.send ("QColor")
                   self.send ("(")
                   self.send_expr (expr.right)
                   self.send (")")
                else :
                   self.send_expr (expr.right)
                self.send (")")
                self.style_new_line ()
                done = True
          else :
             self.custom_prefix (expr.left.item_decl)
             self.send (special)
             self.send ("(")
             self.send_expr (expr.right)
             self.send (")")
             self.style_new_line ()
             done = True

       return done

   # -----------------------------------------------------------------------

   def custom_block_statement (self, stat) :
       expr = stat.inner_expr
       done = False

       if expr.alt_connect != "" :
          self.send_expr (expr.left)
          self.put_dot ()
          self.send ("connect")
          self.send ("(")
          self.send ("self")
          self.put_dot ()
          self.send (expr.alt_connect)
          self.send (")")
          self.style_new_line ()
          done = True

       return done

   # -----------------------------------------------------------------------

   def put_place (self, var) :
       if isinstance (var.item_place, Class) :
          self.send ("self")
       else :
          self.custom_prefix (var.item_place)
          self.send (var.item_place.item_name)

   def put_variable (self, var) :
       self.custom_prefix (var)
       self.send (var.item_name)

   def custom_variable_initialization (self, var) :
       self.send ("=")

       done = False
       special = var.alt_create
       if special != "" and not var.alt_ignore :
          done = True
          if special.startswith ("<") :
              if special == "<menuBar>" :
                 self.send ("self.menuBar ()")
              elif special == "<addToolBar>" :
                 self.send ("self.addToolBar (\"\")")
              elif special == "<statusBar>" :
                 self.send ("self.statusBar ()")
              elif special == "<addMenu>" :
                 self.send ("self.addMenu (\"\")")
              elif special == "<addAction>" :
                 self.send ("self.addAction (\"\")")

              elif special == "<false>" :
                 self.send ("False")
              elif special == "<char_zero>" :
                 self.send ("0")
              elif special == "<zero>" :
                 self.send ("0")
              elif special == "<real_zero>" :
                 self.send ("0.0")
              elif special == "<empty_string>" :
                 self.send ("\"\"")
              elif special == "<null>" :
                 self.send ("None")
          else :
             self.send (special)
             self.send ("(")
             if var.alt_create_owner :
                self.send ("self")
             if var.alt_create_place :
                self.put_place (var)
             self.send (")")
             done = True

       if not done :
          self.send ("None")

   def custom_variable_placement (self, var) :

       special = var.alt_setup
       if special != "" and not var.alt_ignore :
          if special == "<layout>" :
             self.send ("temp = QWidget (self)")
             self.style_new_line ()
             self.send ("temp.setLayout (")
             self.put_variable (var)
             self.send (")")
             self.style_new_line ()
             self.send ("self.setCentralWidget (temp)")
             self.style_new_line ()
          elif special == "<setCentralWidget>"  :
             self.send ("self.setCentralWidget (")
             self.put_variable (var)
             self.send (")")
             self.style_new_line ()
          else :
             func_name = var.alt_setup
             func_param = var.alt_setup_param
             self.put_place (var)
             self.put_dot ()
             self.send (func_name)
             self.send ("(")
             self.put_variable (var)
             if func_param != "" :
                self.send (",")
                self.send (func_param)
             self.send (")")
             self.style_new_line ()

   # -----------------------------------------------------------------------

   def get_declarator_name (self, declarator) :
       result = ""
       while declarator != None :
          if declarator.kind == declarator.nestedDeclarator :
             declarator = declarator.inner_declarator
          else :
             if declarator.kind == declarator.basicDeclarator :
                result = self.get_name (declarator.qual_name)
             declarator = None
       return result

   def send_expr (self, expr) :
       done = False
       if expr.kind == expr.assignExp :
          done = self.custom_assign (expr)
       "new QApplication (argc, argv)"
       if expr.kind == expr.newExp :
          if expr.type1 != None :
             # if str (getattr (expr.type1.type_spec, "item_type", "")) == "QApplication" :
             if str (getattr (expr.type1.type_spec, "id", "")) == "QApplication" : # !?
                params = [ ]
                for item in expr.init_list.items :
                    name = self.get_expr_name (item)
                    params.append (name)
                if params == ["argc", "argv"] :
                   self.send ("QApplication (sys.argv)")
                   done = True
       ".exec or ->exec"
       if expr.kind == expr.fieldExp or expr.kind == expr.ptrFieldExp :
          if expr.simp_name.id == "exec" :
             self.send_expr (expr.left)
             self.put_dot ()
             self.send ("exec_")
             done = True
       if not done :
          super (ToQtPy, self).send_expr (expr)

   def send_simple_declaration (self, param, new_line = True) :
       "int main (int argc, char * * argv)"
       done = False
       if param.body != None and len (param.items) != 0:
          name = self.get_declarator_name (param.items[0].decl)
          if name == "main" :
             self.putLn ("if __name__ == '__main__' :")
             self.style_indent ()
             self.send_compound_stat (param.body)
             self.style_unindent ()
             self.style_empty_line ()
             done = True
       if not done :
          super (ToQtPy, self).send_simple_declaration (param, new_line)

   def send_program (self, param) :

       self.putLn ("#!/usr/bin/env python")
       self.putLn ("")
       self.putLn ("from __future__ import print_function")
       self.putLn ("")
       self.putLn ("import sys")

       if use_pyside2 :
          self.putLn ("from PySide2.QtCore import *")
          self.putLn ("from PySide2.QtGui import *")
          self.putLn ("from PySide2.QtWidgets import *")
       elif use_qt5 :
          self.putLn ("from PyQt5.QtCore import *")
          self.putLn ("from PyQt5.QtGui import *")
          self.putLn ("from PyQt5.QtWidgets import *")
       elif 1 :
          self.putLn ("from PyQt4.QtCore import *")
          self.putLn ("from PyQt4.QtGui import *")
       else :
          self.putLn ("try :")
          self.style_indent ()
          self.putLn ("from PyQt5.QtCore import *")
          self.putLn ("from PyQt5.QtGui import *")
          self.putLn ("from PyQt5.QtWidgets import *")
          self.style_unindent ()
          self.putLn ("except :")
          self.style_indent ()
          self.putLn ("from PyQt4.QtCore import *")
          self.putLn ("from PyQt4.QtGui import *")
          self.style_unindent ()
       self.putLn ("")

       super (ToQtPy, self).send_program (param)

# --------------------------------------------------------------------------

class ToCustomPy (ToQtPy) :

   def __init__ (self) :
       super (ToCustomPy, self).__init__ ()

# --------------------------------------------------------------------------

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
