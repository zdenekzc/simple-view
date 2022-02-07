
# cmm_comp.py

from __future__ import print_function

import os, copy
import inspect

from cmm_parser import *
from cmm_product import *

from input import quoteString
from util import findColor

from code import *
# from cmm_code import *

from grammar import Grammar
from toparser  import ToParser
from toproduct import ToProduct

# --------------------------------------------------------------------------

class NoQuote (object) :
   def __init__ (self, value) :
       self.value = value
   def __repr__ (self) :
       return self.value

# --------------------------------------------------------------------------

class CmmCompiler (Parser) :
   def __init__ (self) :
       super (CmmCompiler, self).__init__ ()

       self.win = None
       self.edit = None

       self.global_scope = Namespace ()
       self.global_scope.item_name = ""
       self.global_scope.hidden_scope = True # do not print scope name

       self.display = [ self.global_scope ]

       self.top_decl_list = None

       self.enable_declaration_stack = [ False ]
       self.remember_compound_name = None

       self.init_types ()

   def compile_program (self) :
       self.top_decl_list = CmmDeclSect ()
       self.storeLocation (self.top_decl_list)
       while self.token != self.eos :
          self.top_decl_list.items.append (self.parse_declaration ())

   # scope

   def enter (self, item) :
       inx = len (self.display) - 1
       scope = self.display [inx]
       while scope.search_only and inx > 0 :
          inx = inx - 1
          scope = self.display [inx]
       if inx < 0 :
          self.error ("All scopes are search-only")
       self.enterIntoScope (scope, item)
       item.item_place = self.display [-1] # last scope , even search_only

   def enterIntoScope (self, scope, item) :
       scope.item_dict [item.item_name] = item
       scope.item_list.append (item)

       item.item_place = scope

       item.item_context = scope

       if hasattr (scope, "item_qual") and scope.item_qual != None and scope.item_qual != "" :
          item.item_qual = scope.item_qual + "." + item.item_name
       else :
          item.item_qual = item.item_name

       # self.selectColor (item, defn = True)

   def openScope (self, scope) :
       self.display.append (scope)

   def closeScope (self) :
       self.display.pop ()

   def searchScope (self, scope, name) :
       return scope.item_dict.get (name, None)

   def lookup (self, name) :
       result = None
       inx = len (self.display) - 1
       while result == None and inx >= 0 :
          result = self.display [inx].item_dict.get (name, None)
          inx = inx - 1
       return result

   def openSearchOnlyScope (self, scope) :
       look = copy.copy (scope)
       look.search_only = True
       self.openScope (look)

   # special scopes

   def register (self, scope, name, item) :
       item.item_name = name
       scope.registered_scopes [name] = item

       item.item_context = scope

       if hasattr (scope, "item_qual") and scope.item_qual != None and scope.item_qual != "" :
          item.item_qual = scope.item_qual + "." + item.item_name
       else :
          item.item_qual = item.item_name

   # namespace

   def on_start_namespace (self, ns_decl) :
       pass

   def on_namespace (self, ns_decl) :
       module = Namespace () # create Namespace object from code.py
       module.link_code (ns_decl) # connect with parsed declaration (module.link_code <--> ns_decl.item_ref)
       module.item_name = ns_decl.simp_name.id # store name
       self.copy_name_location (module, ns_decl.simp_name) # store location
       self.enter (module) # add identifier into scope
       self.selectColor (module, table = "namespaceColors")
       self.markDefn (module) # set attributes in text editor
       self.markOutline (module)
       self.custom_namespace (ns_decl)

   def on_open_namespace (self, ns_decl) :
       module = ns_decl.item_ref
       self.openScope (module) # scope for identifiers
       self.openCompletion (module) # area with text completion

   def on_close_namespace (self, ns_decl) :
       module = ns_decl.item_ref
       self.closeCompletion (module)
       self.closeScope ()

   def on_stop_namespace (self, ns_decl) :
       pass

   # class

   def on_start_class (self, cls_decl) :
       cls = Class ()
       cls.link_code (cls_decl)
       # self.openRegion (cls) # region with background color

   def on_class (self, cls_decl) :
       cls = cls_decl.item_ref
       cls.item_name = cls_decl.simp_name.id
       self.copy_name_location (cls, cls_decl.simp_name)
       self.enter (cls)
       self.selectColor (cls, table = "classColors")
       self.markDefn (cls)
       self.markOutline (cls)
       self.custom_class (cls_decl)

   def on_open_class (self, cls_decl) :
       cls = cls_decl.item_ref
       self.custom_open_class (cls)
       self.openScope (cls)
       self.openCompletion (cls)

   def on_close_class (self, cls_decl) :
       cls = cls_decl.item_ref
       self.closeCompletion (cls)
       self.closeScope ()

   def on_stop_class (self, cls_decl) :
       # self.closeRegion ()
       pass

   # enum

   def on_start_enum (self, enum_decl) :
       enum = Enum ()
       enum.link_code (enum_decl)
       self.openRegion (enum) # region with background color

   def on_enum (self, enum_decl) :
       enum = enum_decl.item_ref
       enum.item_name = enum_decl.simp_name.id
       self.copy_name_location (enum, enum_decl.simp_name)
       self.enter (enum)
       self.selectColor (enum, table = "enumColors")
       self.markDefn (enum)
       self.markOutline (enum)

   def on_open_enum (self, enum_decl) :
       enum = enum_decl.item_ref
       self.openScope (enum)
       self.openCompletion (enum)

   def on_enum_item (self, decl) :
       item = EnumItem ()
       item.item_name = decl.simp_name.id
       item.link_code (decl)
       self.copy_name_location (item, decl.simp_name)
       self.enter (item)
       self.selectColor (item, table = "variableColors")
       self.markDefn (item)

   def on_close_enum (self, enum_decl) :
       enum = enum_decl.item_ref
       self.closeCompletion (enum)
       self.closeScope ()

   def on_stop_enum (self, enum_decl) :
       self.closeRegion ()

   # typedef

   def on_typedef (self, t) :
       typedef = Typedef ()
       typedef.link_code (t)
       self.copy_declarator_name (typedef, t.decl)
       self.copy_declarator_location (typedef, t.decl)
       self.enter (typedef)
       self.selectColor (typedef, table = "typedefColors")
       self.markDefn (typedef)
       self.markOutline (typedef)

   # simple declaration

   def on_simple_item (self, simple_declaration) :
       simple_item = simple_declaration.items [-1] # get above simple declaration
       variable = Variable ()
       variable.link_code (simple_item)
       variable.item_code_decl = simple_declaration # !?

       "is it function"
       func_spec = self.get_function_specifier (simple_item.decl)
       if func_spec != None :
          variable.is_function = True
          variable.item_icon = "function"

       self.copy_declarator_name (variable, simple_item.decl)
       self.copy_declarator_location (variable, simple_item.decl)

       init_type = simple_declaration.type_spec.item_type
       variable.item_type = self.get_declarator_type (init_type, simple_item.decl)

       "constructor or destructor"
       if self.ctor_declarator (simple_item.decl) :
          expr = simple_declaration.type_spec
          if expr.kind == expr.simpleName :
             func_name = expr.id
             variable.item_name = func_name
             cls = self.display [-1]
             if isinstance (cls, Class) :
                if func_name == cls.item_name :
                   variable.is_constructor = True
                   # if func_spec != None :
                   #    if simple_declaration.a_destructor :
                   #       variable.is_destructor = True
                   #    else :
                   #       variable.is_constructor = True

       self.enter (variable)
       if variable.is_function :
          self.selectColor (variable, table = "functionColors")
       else :
          self.selectColor (variable, table = "variableColors")
       self.markDefn (variable)

       self.custom_simple_item (simple_declaration, simple_item)

   def on_simple_declaration (self, simple_decl) :
       self.custom_simple_declaration (simple_decl)

   def on_simple_statement (self, stat) :
       self.custom_simple_statement (stat)

   def on_block_statement (self, stat) :
       self.custom_block_statement (stat)

   def ctor_declarator (self, decl) :
       return ( decl.kind == decl.emptyDeclarator and
                len (decl.ptr_spec.items) == 0 and
                len (decl.cont_spec.items) == 1 and
                isinstance (decl.cont_spec.items[0], CmmFunctionSpecifier))

   def get_simple_name (self, qual_name) :
       result = ""
       if qual_name.kind == qual_name.simpleName :
          result = qual_name.id
       return result

   def copy_declarator_name (self, target, declarator) :
       if declarator != None :
          while declarator.kind == declarator.nestedDeclarator :
             declarator = declarator.inner_declarator
          if declarator.kind == declarator.basicDeclarator :
             target.item_name = self.get_simple_name (declarator.qual_name) # !?
          else :
             target.item_name = ""

   def copy_declarator_location (self, target, declarator) :
       if declarator != None :
          while declarator.kind == declarator.nestedDeclarator :
             declarator = declarator.inner_declarator
          if declarator.kind == declarator.basicDeclarator :
             self.copy_name_location (target, declarator.qual_name)

   # function

   def on_open_function (self, simple_declaration) :
       if len (simple_declaration.items) != 0 : # !?
          simple_item = simple_declaration.items [-1]
          variable = simple_item.item_ref
          if not variable.is_function :
             self.openSearchOnlyScope (variable) # only for lookup, not for declarations
             self.openCompletion (variable, outside = True)
          if variable.is_function :
             func = variable

             self.openRegion (func) # region with background color
             self.openScope (func)

             func_spec = self.get_function_specifier (simple_item.decl)
             self.enter_parameters (func_spec.parameters)

             self.openCompletion (func, outside = True)
             self.markOutline (func)

             self.register (func, "(local)", func.local_scope)
             func.local_scope.hidden_scope = True # do not print (local)
             self.openScope (func.local_scope)

   def on_close_function (self, simple_declaration) :
       if len (simple_declaration.items) != 0 : # !?
          simple_item = simple_declaration.items [-1]
          variable = simple_item.item_ref
          if not variable.is_function :
             variable.item_body = simple_declaration.body
             self.closeCompletion (variable, outside = True)
             self.closeScope ()
          if variable.is_function :
             func = variable
             func.item_body = simple_declaration.body
             self.closeCompletion (func, outside = True)
             self.closeScope () # local variables
             self.closeScope () # parameters
             self.closeRegion ()
             # simple_declaration.body.item_label = func.item_name
          self.custom_statement (variable, simple_declaration.body)

   def get_function_specifier (self, declarator) :
       result = None
       while declarator != None and result == None :
          inx = len (declarator.cont_spec.items) - 1
          while inx >= 0 :
             c = declarator.cont_spec.items [inx]
             if isinstance (c, CmmFunctionSpecifier) :
                result = c
             inx = inx - 1

          if result == None :
             if declarator.kind == declarator.nestedDeclarator :
                declarator = declarator.inner_declarator
             else :
                declarator = None

       return result

   def enter_parameters (self, param_list) :
       for param in param_list.items :
           if param.kind == param.plainParam : # !?
              variable = Variable ()
              variable.link_code (param)

              self.copy_declarator_name (variable, param.decl)
              self.copy_declarator_location (variable, param.decl)

              init_type = getattr (param.type_spec, "item_type", None)
              variable.item_type = self.get_declarator_type (init_type, param.decl)

              self.enter (variable)
              self.selectColor (variable, table = "variableColors")
              self.markDefn (variable)

   # names

   def on_base_name (self, qual_name) :
       decl = None
       if qual_name.kind == qual_name.globalName :
          inner_name = qual_name.inner_name
          if inner_name.kind == inner_name.simpleName :
             decl = self.searchScope (self.global_scope, inner_name.id)
       else :
          if qual_name.kind == qual_name.simpleName :
             decl = self.lookup (qual_name.id)

       if decl != None :
          if isinstance (decl, Class) or isinstance (decl, Enum) or isinstance (decl, Typedef) :
             qual_name.type_flag = True
             # qual_name.item_type = self.get_type_decl (qual_name)

       "add item_decl"
       qual_name.item_decl = decl
       self.custom_base_name (qual_name)

   def is_template (self, qual_name) :
       decl = qual_name.item_decl
       result = decl != None and getattr (decl, "item_code", None) != None and getattr (decl.item_code, "template_decl", None) != None
       return result

   def is_cont_template (self, cont_name) :
       return False

   def on_template_args (self, qual_name) :
       if qual_name.item_decl != None :
          qual_name.item_qual = self.get_instance_identification (qual_name.item_decl)
          self.create_instance (qual_name)
       qual_name.item_decl = qual_name.left.item_decl # !?

   def on_begin_compound_name (self, qual_name) :
       self.remember_compound_name = qual_name

   def on_cont_name (self, qual_name) :
       decl = self.remember_compound_name
       self.remember_compound_name = None
       if decl != None and getattr (decl, "item_dict", None) != None :
          qual_name.item_decl = self.searchScope (decl, qual_name.id)

   def on_compound_name (self, qual_name) :
       cont = qual_name.right
       qual_name.item_decl = cont.item_decl

   # type or expression

   def is_binary_expression (self, expr) :
       # type names cannot be left operand in binary expressions
       return not expr.type_flag

   def is_expression (self, expr) :
       return not expr.type_flag

   def is_value_parameter (self, expr) :
       return not expr.type_flag

   def on_begin_flexible_expr (self) :
       # enable strange declarations (declaration starting with unknown identifier and asterisk)
       self.enable_declaration_stack.append (True)

   def on_end_flexible_expr (self) :
       # disable strange declarations
       self.enable_declaration_stack.pop ()

   def on_name_expr (self, expr) :
       # rember strange declaratrion flag and disable strange declarations
       expr.remember_enable_declaration = self.enable_declaration_stack [-1]
       self.enable_declaration_stack [-1] = False

   def on_other_expr (self) :
       # disable strange declarations
       self.enable_declaration_stack [-1] = False

   def is_multiplicative_expression (self, expr) :
       return not expr.type_flag and not expr.remember_enable_declaration

   def is_and_expression (self, expr) :
       return not expr.type_flag and not expr.remember_enable_declaration

   def on_bit_not_expr (self, expr) :
       expr.type_flag = expr.param.type_flag

   def is_postfix_expression (self, expr) :
       if self.tokenText == "(" :
          return True
          # return not expr.type_flag and not expr.remember_enable_declaration
          # return not expr.type_flag
       else :
          return not expr.type_flag

   def is_mul (self, expr) :
       return False

   def is_add (self, expr) :
       return False

   def is_constructor (self, expr) :
       return False

   # location and style

   def copy_location (self, target, source) :
       target.src_file = source.src_file
       target.src_line = source.src_line
       target.src_column = source.src_column
       target.src_pos = source.src_pos
       target.src_end = source.src_end

   def copy_name_location (self, target, qual_name) :
       source = qual_name
       if source != None :
          if source.kind == source.compoundName :
             source = source.right
          self.copy_location (target, source)

   def copy_style (self, target, source) :
       if source != None :
          if getattr (source, "item_ink", None) != None:
             target.item_ink = source.item_ink
          if getattr (source, "item_paper", None) != None:
             target.item_paper = source.item_paper
          if getattr (source, "item_icon", None) != None:
             target.item_icon = source.item_icon

   # name as a string

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

   # type specifiers

   def on_type_name (self, expr) :
       expr.type_flag = True
       expr.item_type = expr.qual_name.item_type

   def on_cv_specifier (self, expr) :
       expr.type_flag = True

       type = expr.param.item_type

       if isinstance (type, NamedType) :
          new_type = NamedType ()
          new_type.type_const = type.type_const
          new_type.type_volatile = type.type_volatile
          new_type.type_name = type.type_name
          new_type.type_decl = type.type_decl

       if type != None : # !?
          if expr.kind == expr.constSpec :
             type.type_const = True
          if expr.kind == expr.volatileSpec :
             type.type_volatile = True

       expr.item_type = type

   def on_type_specifier (self, expr) :
       expr.type_flag = True

       type = self.get_type_spec (expr)
       expr.item_type = type
       self.copy_location (type, expr)
       self.copy_style (type, expr)

       # if isinstance (type, NamedType) :
       #    self.copy_style (type, type.type_decl)
       #    self.markUsage (type)

       self.custom_type_specifiers (expr, type)

   def get_type_decl (self, obj) :
       result = None
       if obj.item_decl != None :
          if ( isinstance (obj.item_decl, Class) or
               isinstance (obj.item_decl, Enum) or
               isinstance (obj.item_decl, Typedef) or
               isinstance (obj.item_decl, Unknown) ) :
             result = obj.item_decl
       return result

   def get_named_type (self, qual_name) :
       result = NamedType ()
       result.type_name = self.get_name (qual_name)
       result.type_decl = self.get_type_decl (qual_name)
       if isinstance (qual_name, CmmTemplateName) :
          result.type_name = self.get_name (qual_name.left) # !? name without < >
          result.type_args =  qual_name.template_args
          result.type_args = [ ]
          for arg in qual_name.template_args.items :
              # type_spec = arg.value.type_spec
              # result.type_args.append (type_spec.item_type) # !? missing pointers, ...
              param = arg.value
              init_type = getattr (param.type_spec, "item_type", None)
              param_type = self.get_declarator_type (init_type, param.decl)
              result.type_args.append (param_type)
       return result

   def get_type_spec (self, type_spec) :
       result = None
       # qual_name = type_spec.basic_name
       # if qual_name != None :
       #    result = self.get_named_type (qual_name)
       # else :
       if 1 :
          result = SimpleType ()
          if type_spec.a_void : result.type_void = True
          elif type_spec.a_bool : result.type_bool = True
          elif type_spec.a_char : result.type_char = True
          elif type_spec.a_wchar : result.type_wchar = True
          elif type_spec.a_short : result.type_short = True
          elif type_spec.a_int : result.type_int = True
          elif type_spec.a_long : result.type_long = True
          elif type_spec.a_float : result.type_float = True
          elif type_spec.a_double : result.type_double = True

          if type_spec.a_signed :
             result.type_signed = True
          elif type_spec.a_unsigned :
             result.type_unsigned = True

       # if type_spec.a_const :
       #    result.type_const = True
       # if type_spec.a_volatile :
       #    result.type_volatile = True

       return result

   # declarator type

   def get_declarator_type (self, init_type, declarator) :
       result = init_type
       while declarator != None :
          for p in declarator.ptr_spec.items :
             last = result
             if p.kind == p.pointerSpec :
                result = PointerType ()
                result.type_from = last
             if p.kind == p.referenceSpec :
                result = ReferenceType ()
                result.type_from = last
             if p.cv_spec.cv_const :
                result.type_const = True
             if p.cv_spec.cv_volatile :
                result.type_volatile = True

          if declarator.kind != declarator.emptyDeclarator :
             inx = len (declarator.cont_spec.items) - 1
             while inx >= 0 :
                c = declarator.cont_spec.items [inx]
                last = result
                if isinstance (c, CmmFunctionSpecifier) :
                   result = FunctionType ()
                   result.type_from = last
                if isinstance (c, CmmArraySpecifier) :
                   result = ArrayType ()
                   result.type_from = last
                inx = inx - 1

          if declarator.kind == declarator.nestedDeclarator :
             declarator = declarator.inner_declarator
          else :
             declarator = None

       return result

   # expression

   def on_ident_expr (self, expr) :
       self.markUsage (expr, expr.item_decl)

       # !?
       if self.get_type_decl (expr) != None :
          expr.item_type = self.get_named_type (expr)

       if expr.item_decl != None and getattr (expr.item_decl, "item_type", None) != None :
          expr.item_type = expr.item_decl.item_type

       "true or false"
       if expr.kind == expr.simpleName :
          ident = expr.id
          if ident == "true" :
             expr.item_value = True
          elif ident == "false" :
             expr.item_value = False

       if hasattr (expr.item_decl, "item_value") :
          expr.item_value = expr.item_decl.item_value

   def on_field_expr (self, expr) :
       left = expr.left
       right = expr.simp_name
       right.item_name = right.id

       decl = None
       if left.item_type != None :
          decl = getattr (left.item_type, "type_decl", None)
       elif left.item_decl != None :
          decl = left.item_decl # class name or enum type name
          if not isinstance (decl, Class) and not isinstance (decl, Enum) and not isinstance (decl, Typedef) :
             decl = None

       if decl != None and getattr (decl, "item_dict", None) != None :
             right.item_decl = decl.item_dict.get (right.item_name)
             # if expr.item_decl == None :
             #    self.warning ("Unknown field: " + expr.item_name)
             expr.item_decl = right.item_decl
             if getattr (right.item_decl, "item_type", None) != None : # !?.
                expr.item_type = right.item_decl.item_type
             self.markUsage (right, right.item_decl)
       self.custom_field (expr)

   def on_int_value (self, expr) :
       expr.item_type = self.intType
       text = expr.value
       if text.startswith ("0") :
          if text.startswith ("0x") :
             expr.item_value = int (text[2:], 16)
          elif text.startswith ("0b") :
             expr.item_value = int (text[2:], 2)
          elif text.startswith ("0o") :
             expr.item_value = int (text[2:], 8)
          elif text.startswith ("0q") :
             expr.item_value = int (text[2:], 8)
          elif len (text) > 1 :
             expr.item_value = int (text[1:], 8) # starting zero => octal
          else :
             expr.item_value = 0
       else:
          expr.item_value = int (text)

   def on_real_value (self, expr) :
       expr.item_type = self.doubleType
       expr.item_value = float (expr.value)

   def on_char_value (self, expr) :
       expr.item_type = self.charType
       expr.item_value = expr.value

   def on_string_value (self, expr) :
       expr.item_type = self.stringType

       text = expr.value
       for item in expr.items :
          text = text + item.value
       expr.item_value = text

   def on_call_expr (self, expr) :
       self.custom_call (expr)

   def on_binary_expr (self, expr) :
       if expr.kind in [expr.mulExp, expr.divExp, expr.modExp,
                        expr.addExp, expr.subExp,
                        expr.shlExp, expr.shrExp,
                        expr.bitAndExp, expr.bitOrExp, expr.bitXorExp ] :
          "result type"
          a = self.type_number (expr.left)
          b = self.type_number (expr.right)
          inx = a
          if b > inx :
             inx = b
          if inx == self.doubleInx :
             expr.item_type = self.doubleType
          if inx == self.floatInx :
             expr.item_type = self.floatType
          if inx == self.unsignedLongInx :
             expr.item_type = self.unsignedLongType
          if inx == self.longInx :
             expr.item_type = self.longType
          if inx == self.unsignedIntInx :
             expr.item_type = self.unsignedIntType
          if inx == self.intInx :
             expr.item_type = self.intType

          self.custom_binary (expr, inx)

       elif expr.kind in [expr.ltExp, expr.leExp, expr.gtExp, expr.geExp, expr.eqExp, expr.neExp,
                        expr.logAndExp, expr.logOrExp ] :
          expr.item_type = self.boolType
          self.custom_relation (expr)

       elif expr.kind in [expr.assignExp] :
          self.custom_assign (expr)

       self.binary_expr_value (expr)

   # expression value

   def get_expr_value (self, expr) :
       return getattr (expr, "item_value", None)

   def binary_expr_value (self, expr) :
       value = None

       if expr.kind in [ expr.addExp, expr.subExp, expr.mulExp, expr.divExp, expr.modExp,
                         expr.shlExp, expr.shrExp, expr.bitAndExp, expr.bitOrExp, expr.bitXorExp,
                         expr.ltExp, expr.gtExp, expr.leExp, expr.geExp, expr.eqExp, expr.neExp ] :
          left = self.get_expr_value (expr.left)
          right = self.get_expr_value (expr.right)
          if left != None and right != None :
             if expr.kind == expr.addExp : value = left + right
             if expr.kind == expr.subExp : value = left - right
             if expr.kind == expr.mulExp : value = left * right
             if expr.kind == expr.divExp : value = left / right
             if expr.kind == expr.modExp : value = left % right
             if expr.kind == expr.shlExp : value = left << right
             if expr.kind == expr.shrExp : value = left >> right

             if expr.kind == expr.bitAndExp : value = left & right
             if expr.kind == expr.bitOrExp  : value = left | right
             if expr.kind == expr.bitXorExp : value = left ^ right

             if expr.kind == expr.ltExp : value = left < right
             if expr.kind == expr.gtExp : value = left > right
             if expr.kind == expr.leExp : value = left <= right
             if expr.kind == expr.geExp : value = left >= right
             if expr.kind == expr.eqExp : value = left == right
             if expr.kind == expr.neExp : value = left != right

       elif expr.kind == expr.logAndExp :
          left = self.get_expr_value (expr.left)
          if left != None :
             if left == False :
                value = False
             else :
                value = self.get_expr_value (expr.right)

       elif expr.kind == expr.logOrExp :
          left = self.get_expr_value (expr.left)
          if left != None :
             if left == True :
                value = True
             else :
                value = self.get_expr_value (expr.right)

       expr.item_value = value

   # expression type

   intInx = 1
   unsignedIntInx = 2
   longInx = 3
   unsignedLongInx = 4
   floatInx = 5
   doubleInx = 6
   unknownInx = 7

   def init_types (self) :
       self.intType = SimpleType ()
       self.intType.type_int = True

       self.unsignedIntType = SimpleType ()
       self.unsignedIntType.type_unsigned = True
       self.unsignedIntType.type_int = True

       self.longType = SimpleType ()
       self.longType.type_long = True

       self.unsignedLongType = SimpleType ()
       self.unsignedLongType.type_unsigned = True
       self.unsignedLongType.type_long = True

       self.floatType = SimpleType ()
       self.floatType.type_float = True

       self.doubleType = SimpleType ()
       self.doubleType.type_double = True

       self.boolType = SimpleType ()
       self.boolType.type_bool = True

       self.charType = SimpleType ()
       self.charType.type_char = True

       # self.wcharType = SimpleType ()
       # self.wcharType.type_wchar = True

       # self.voidType = SimpleType ()
       # self.voidType.type_void = True

       self.stringType = NamedType ()
       self.stringType.type_name = "string" # !?

   def type_number (self, expr) :
       inx = self.unknownInx
       type = expr.item_type
       if type != None:
          if isinstance (type, SimpleType) : # !?
             if type.type_double :
                inx = self.doubleInx
             elif type.type_float :
                inx = self.floatInx
             elif type.type_long :
                if type.type_unsigned :
                   inx = self.unsignedLongInx
                else :
                   inx = self.longInx
             elif type.type_int or type.type_short or type.type_wchar or type.type_char or type.type_bool :
                if type.type_unsigned :
                   inx = self.unsignedIntInx
                else :
                   inx = self.intInx
       return inx

   # -----------------------------------------------------------------------

   def on_declaration_list (self, decl_list) :
       if self.top_decl_list == None :
          self.top_decl_list = decl_list

   # -----------------------------------------------------------------------

   def custom_namespace (self, ns_decl) :
       pass

   def custom_simple_item (self, simple_decl, simple_item) :
       pass

   def custom_simple_declaration (self, simple_decl) :
       pass

   def custom_simple_statement (self, stat) :
       pass

   def custom_block_statement (self, stat) :
       pass

   def custom_base_name (self, qual_name) :
       pass

   def custom_relation (self, expr) :
       pass

   def custom_binary (self, expr, inx) :
       pass

   def custom_assign (self, expr) :
       pass

   def custom_call (self, expr) :
       pass

   def custom_field (self, expr) :
       pass

   def custom_type_specifiers (self, type_spec, type) :
       pass

   def custom_statement (self, target, stat) :
       pass

# --------------------------------------------------------------------------

class CmmQtCompiler (CmmCompiler) :

   def __init__ (self) :
       super (CmmQtCompiler, self).__init__ ()

       self.foreign_modules = { }
       self.foreign_types = { }

   # -----------------------------------------------------------------------

   # special scopes

   def registerScope (self, top, name) :
       if name in top.registered_scopes :
          result = top.registered_scopes [name]
       else :
          result = Scope ()
          result.hidden_scope = True
          self.register (top, name, result)
       return result

   def enter_unknown (self, top, name, qual_name) :
       scope = self.registerScope (top, "(unknown)")
       if name in scope.item_dict :
          unknown = scope.item_dict [name]
       else :
          unknown = Unknown ()
          unknown.item_name = name
          unknown.link_code (qual_name)
          self.enterIntoScope (scope, unknown)
          self.copy_location (unknown, qual_name)
          unknown.item_ink = findColor ("unknown")
       qual_name.item_decl = unknown

   def enter_foreign (self, top, name, qual_name) :
       scope = self.registerScope (top, "(foreign)")
       # scope = top
       if name in scope.item_dict :
          result = scope.item_dict [name]
       else :
          result = Unknown ()
          result.item_name = name
          result.link_code (qual_name)
          self.enterIntoScope (scope, result)
          result.item_place = top # after enterIntoScope
          self.copy_location (result, qual_name)
          result.item_ink = findColor ("foreign")
       qual_name.item_decl = result

   # -----------------------------------------------------------------------

   def find_foreign_object (self, name) :
       result = None
       for module in self.foreign_modules :
           if result == None :
              result = getattr (module, name, None)
              # print ("FOUND", name, result)
       # if name.startswith ("QTable") :
       #    print ("FOUND", name, result)
       return result

   def find_foreign_variable (self, var) :
       type = var.item_type

       if isinstance (type, PointerType) :
          type = type.type_from
       if isinstance (type, NamedType) :
          name = type.type_name
          var.foreign_obj = self.find_foreign_object (name) # variable with Qt type

   # -----------------------------------------------------------------------

   # custom identifiers

   def custom_base_name (self, qual_name) :
       if qual_name.item_decl == None and qual_name.kind == qual_name.simpleName :
          name = qual_name.id

          "foreign identifiers (Qt field names)"
          inx = len (self.display) - 1
          while qual_name.item_decl == None and inx >= 0 :
             scope = self.display [inx]
             if scope.foreign_obj != None :
                if hasattr (scope.foreign_obj, name) :
                   self.enter_foreign (scope, name, qual_name)
                   # print ("QT item", name)
             inx = inx - 1

          stop = False
          foreign = self.find_foreign_object (name) # variable with Qt type
          if foreign != None :
             # print ("FOREIGN", foreign.__name__)
             self.enter_foreign (self.global_scope, name, qual_name)
             if inspect.isclass (foreign) :
                qual_name.type_flag = True
             stop = True

          if not stop :
             "unknown identifiers"
             inx = len (self.display) - 1
             while qual_name.item_decl == None and inx >= 0 :
                scope = self.display [inx]
                if scope.default_scope :
                   self.enter_unknown (scope, name, qual_name)
                   # print ("UNKNOWN item", name)
                inx = inx - 1

             if qual_name.item_decl == None :
                self.enter_unknown (self.global_scope, name, qual_name)

   def custom_open_class (self, cls) :
       base_list = cls.item_code.base_list
       if base_list != None :
          for item in base_list.items :
              if cls.foreign_obj == None :
                 name = item.from_cls.id
                 cls.foreign_obj = self.find_foreign_object (name) # class with one/first Qt super class

   # -----------------------------------------------------------------------

   # Qt assign

   def custom_assign (self, expr) :
       var = expr.left.item_decl
       right = expr.right

       if var != None : # !?
          self.find_foreign_variable (var)

          name = var.item_name
          target_obj = var.item_place.foreign_obj

          context = var.item_context
          if context.item_name == "(foreign)" : # !?
             foreign = context.item_context.foreign_obj
             if foreign != None :
                set_name = "set" + name.capitalize ()
                if hasattr (foreign, name) and hasattr (foreign, set_name) :
                   expr.alt_assign = set_name

          if self.is_subtype (target_obj, "QTreeWidgetItem") :
             if name == "text":
                expr.alt_assign = "<text>"
             elif name == "icon" :
                expr.alt_assign = "<icon>"
             elif name == "foreground" :
                expr.alt_assign = "<foreground>"
             elif name == "background" :
                expr.alt_assign = "<background>"

          else :
             if name == "icon" :
                expr.alt_assign = "<setIcon>"
             elif name == "shortcut" :
                expr.alt_assign = "<setShortcut>"

   # -----------------------------------------------------------------------

   # Qt field initialization

   def find_type (self, name) :
       result = None
       if name in self.foreign_types :
          result = self.foreign_types [name]
       else :
          for module in self.foreign_modules :
              if result == None :
                 result = getattr (module, name, None)
          self.foreign_types [name] = result # store type or None
       return result

   def is_subtype (self, obj, name) :
       type = self.find_type (name)
       result = obj != None and issubclass (obj, type)
       return result

   def custom_simple_item (self, simple_decl, simple_item) :
       var = simple_item.item_ref

       var.default_scope = True
       self.find_foreign_variable (var)

       type = var.item_type
       type_name = ""
       if isinstance (type, PointerType) :
          type = type.type_from
       if getattr (type, "type_name", "") != "" :
          type_name = type.type_name

       local_obj = var.foreign_obj

       target_obj = None
       if var.item_place != None :
          target_obj = var.item_place.foreign_obj

       if self.is_subtype (target_obj, "QMainWindow") :
          if self.is_subtype (local_obj, "QMenuBar") :
             var.alt_create = "<menuBar>"
          elif self.is_subtype (local_obj, "QToolBar") :
             var.alt_create = "<addToolBar>"
          elif self.is_subtype (local_obj, "QStatusBar") :
             var.alt_create = "<statusBar>"
          elif self.is_subtype (local_obj, "QLayout")  :
             var.alt_setup = "<layout>"
          else :
             var.alt_setup = "<setCentralWidget>"

       if var.alt_create == "" :
          if self.is_subtype (local_obj, "QTreeWidgetItem") :
             var.alt_create = type_name
             var.alt_create_place = True
          elif self.is_subtype (local_obj, "QTableWidgetItem") :
             var.alt_create = type_name
          elif self.is_subtype (local_obj, "QWidget") :
             var.alt_create = type_name
             var.alt_create_owner = True
          elif self.is_subtype (local_obj, "QAction") :
             var.alt_create = type_name
             var.alt_create_owner = True
          elif self.is_subtype (local_obj, "QLayout") :
             var.alt_create = type_name
             var.alt_create_owner = True

       # if self.is_subtype (target_obj, "QMainWindow") :
       #    if self.is_subtype (local_obj, "QMenuBar") :
       #       pass
       #    elif self.is_subtype (local_obj, "QToolBar") :
       #       pass
       #    elif self.is_subtype (local_obj, "QStatusBar") :
       #       pass
       # elif self.is_subtype (target_obj, "QLayout") :
       if self.is_subtype (target_obj, "QLayout") :
          if self.is_subtype (local_obj, "QLayout") :
             var.alt_setup = "addLayout"
          else :
             var.alt_setup = "addWidget"

       if self.is_subtype (target_obj, "QMenuBar") and self.is_subtype (local_obj, "QMenu") :
          var.alt_setup = "addMenu"
       elif self.is_subtype (local_obj, "QAction") :
          var.alt_setup = "addAction"
       elif self.is_subtype (target_obj, "QToolBar") or self.is_subtype (target_obj, "QStatusBar"):
          var.alt_setup = "addWidget"
       elif self.is_subtype (target_obj, "QTabWidget") :
          var.alt_setup = "addTab"
          var.alt_setup_param = quoteString (var.item_name) # !?
       elif self.is_subtype (target_obj, "QTreeWidget") :
          var.alt_setup = "addTopLevelItem"

       elif self.is_subtype (target_obj, "QWidget") and self.is_subtype (local_obj, "QWidget") :
          pass
       elif target_obj != None and self.is_subtype (local_obj, "QWidget") :
          var.alt_setup = "addWidget"

       type = var.item_type
       if isinstance (type, SimpleType) :
           if type.type_bool :
              var.alt_create = "<false>"
           if type.type_char or type.type_wchar :
              var.alt_create = "<char_zero>"
           if type.type_short or type.type_int or type.type_long :
              var.alt_create = "<zero>"
           if type.type_float or type.type_double :
              var.alt_create = "<real_zero>"

       if isinstance (type, NamedType) :
          if type.type_name == "string" :
              var.alt_create = "<empty_string>"

       if var.alt_create == "" :
          var.alt_create = "<null>"

   # -----------------------------------------------------------------------

   "Qt connect"

   def custom_block_statement (self, stat) :
       expr = stat.inner_expr
       if expr.kind == expr.callExp : # !?
          if expr.left.kind == expr.simpleName : # !?
             dcl = getattr (expr.left, "item_decl", None) # !?
             if dcl != None :
                foreign = dcl.item_context.foreign_obj
                cls = self.getClass ()
                if cls != None :
                   method = Method ()
                   method.name = "method" + str (len (cls.methods)+1)
                   method.body = stat.body
                   cls.methods.append (method)
                   expr.alt_connect = method.name
                   expr.alt_connect_dcl = dcl
                   expr.alt_connect_signal = expr.left.id

   def getClass (self) :
       inx = len (self.display) - 1
       obj = None
       while inx > 0 and obj == None :
          tmp = self.display[inx]
          if isinstance (tmp, Class) :
             obj = tmp
          else :
             inx = inx - 1
       return obj

# --------------------------------------------------------------------------

class CmmCustomCompiler (CmmQtCompiler) :

   def __init__ (self) :
       super (CmmCustomCompiler, self).__init__ ()

       "options"
       self.skip_functions = False

       "type scope"
       self.type_scope = self.registerScope (self.global_scope, "(type)")

       "expr scope"
       self.expr_cnt = 0
       self.expr_scope = self.registerScope (self.global_scope, "(expr)")

       "language extensions"
       self.attribute_modules = [ ]

   # -----------------------------------------------------------------------

   def custom_field (self, expr) :
       left = expr.left
       right = expr.simp_name

       "artificial fields"
       if isinstance (left.item_decl, Class) :
          if right.item_decl == None and right.item_name == "fields" :
             "fields - list of variables declared in class"
             fields = [ ]
             for item in left.item_decl.item_list :
                 if isinstance (item, Variable) and not item.is_function :
                    fields.append (NoQuote (item.item_name))
             expr.item_value = fields

   # -----------------------------------------------------------------------

   # special scopes

   def enter_type (self, type) :
       name = str (type)
       if name in self.type_scope.item_dict :
          decl = self.type_scope.item_dict [name]
          self.copy_style (type, decl)
       else :
          type.item_name = name
          self.enterIntoScope (self.type_scope, type)
          self.selectColor (type)

   # -----------------------------------------------------------------------

   # attributes

   def custom_namespace (self, ns_decl) :
       "namespace_attributes"
       ns = ns_decl.item_ref
       for group in ns_decl.attr.items :
           for a in group.items :
               n = self.get_expr_name (a.attr_expr)
               if n == "compile_time" :
                  ns.attr_compile_time = True
                  ns.skip_code = True
               else :
                  self.error ("Unknown namespace attribute: " + n)

   def custom_class (self, cls_decl) :
       "class attributes"
       cls = cls_decl.item_ref
       for group in cls_decl.attr.items :
           for a in group.items :
               n = self.get_expr_name (a.attr_expr)
               if n == "compile_time" :
                  cls.attr_compile_time = True
                  cls.skip_code = True
               else :
                  self.error ("Unknown class attribute: " + n)

   def custom_simple_item (self, simple_decl, simple_item) :
       "invoke attribute"
       if self.no_decl_spec (simple_decl.decl_spec) :
          if not simple_decl.a_destructor :
             expr = simple_decl.type_spec
             if expr.kind == expr.simpleName : # !?
                dcl = expr.item_decl
                if dcl != None and isinstance (dcl, Variable):
                   if dcl.attr_compile_time :
                      if dcl.attr_field :
                         self.set_field (dcl.item_name)
                      else :
                         self.invoke_attribute (dcl.item_name)

                   decl = simple_item.decl # declarator
                   if decl.qual_name == None :
                      if len (decl.ptr_spec.items) == 0 :
                         if len (decl.ptr_spec.items) == 0 :
                            if len (decl.cont_spec.items) == 1 :
                               cont = decl.cont_spec.items [0]
                               if isinstance (cont, CmmFunctionSpecifier) :
                                  values = [ ]
                                  if not cont.cv_spec.cv_const :
                                     if not cont.cv_spec.cv_volatile :
                                        if cont.exception_spec == None :
                                           params = cont.parameters
                                           for param in params :
                                               if (param.decl != None or
                                                   param.dots or
                                                   param.item_value == None) :
                                                   self.error ("Invalid attribute value")
                                               values.append (param.item_value)
                                  if dcl.attr_field :
                                     self.set_field (dcl.item_name, values)
                                  else :
                                     self.invoke_attribute (dcl.item_name, values)
       "simple item attributes"
       var = simple_item.item_ref
       for g in simple_item.attr.items :
           for a in g.items :
              n = self.get_expr_name (a.attr_expr)
              if n == "compile_time" :
                 var.attr_compile_time = True
              elif n == "field" :
                 var.attr_compile_time = True
                 var.attr_field = True
              elif n == "context" :
                 var.attr_context = True
              else :
                 self.error ("Unknown attribute: " + n)
       if var.attr_compile_time :
          if not var.attr_field :
              self.check_attribute (simple_item)
          var.skip_code = True

       "Qt assign / declaration"
       super (CmmCustomCompiler, self).custom_simple_item (simple_decl, simple_item)

   def custom_simple_statement (self, stat) :
       expr = stat.inner_expr
       if expr.kind == expr.simpleName : # !?
          dcl = expr.item_decl
          if dcl != None and isinstance (dcl, Variable):
             if dcl.attr_compile_time :
                if dcl.attr_field :
                   self.set_field (dcl.item_name)
                else :
                   self.invoke_attribute (dcl.item_name)
       "Qt connect"
       super (CmmCustomCompiler, self).custom_simple_statement (stat)

   def no_decl_spec (self, decl_spec) :
       return ( decl_spec == None or
                ( not decl_spec.a_inline and
                  not decl_spec.a_virtual and
                  not decl_spec.a_explicit and
                  not decl_spec.a_mutable and
                  not decl_spec.a_static and
                  not decl_spec.a_register ) )

   def get_expr_name (self, expr) :
       return self.get_name (expr)

   def getContext (self) :
       inx = len (self.display) - 1
       obj = None
       cont = True
       while inx > 0 and cont :
          obj = self.display[inx]
          if ( isinstance (obj, Namespace) or
               isinstance (obj, Enum) or
               isinstance (obj, Class) or
               isinstance (obj, Variable) ) :
             cont = False
          else :
             inx = inx - 1
       return obj

   def set_field (self, name, value = True) :
       ctx = self.getContext ()
       setattr (ctx, name, value)
       ctx.item_tooltip = "field " + name
       self.info ("SET FIELD " + getattr (ctx, "item_name", "?") + "." + name + " = " + str (value))

   def custom_call (self, expr) :
       left = expr.left
       if left.kind == left.simpleName : # !?

          "attributes"
          dcl = left.item_decl
          if dcl != None and isinstance (dcl, Variable):

             if dcl.attr_compile_time :
                expr.skip_code = True

                name = dcl.item_name
                values = [ ]
                if dcl.attr_context :
                   values.append (expr)

                inx = 0
                for param in expr.param_list.items :
                    inx = inx + 1
                    if dcl.attr_context : # !?
                       value = param
                    else :
                       if hasattr (param, "item_value") :
                          value = param.item_value
                       else :
                          value = None
                          self.error ("Unknown value of attribute parameter: " + name + " " + str (inx))
                    values.append (value)

                self.invoke_attribute (name, values)

   # -----------------------------------------------------------------------

   def find_attribute (self, name) :
       result = None
       if hasattr (self, name) :
          result = getattr (self, name)
       if result == None :
          for module in self.attribute_modules :
              if result == None :
                 result = getattr (module, name, None)
       if result == None :
          self.error ("Missing attribute implementation: " + name)
       return result

   def check_attribute (self, decl) :
       name = decl.item_ref.item_name
       self.find_attribute (name) # only check

   def invoke_attribute (self, name, arg_list = [ ]) :
       obj = self.find_attribute (name)
       if obj != None :
          if callable (obj) :
             self.info ("INVOKE " + name)
             obj (*arg_list)

   # -----------------------------------------------------------------------

   # attributes

   def ink (self, color) :
       obj = self.getContext ()
       obj.item_ink = findColor (color)
       print ("INK", str (obj), color)

   def paper (self, color) :
       obj = self.getContext ()
       obj.item_paper = findColor (color)
       print ("PAPER", color)

   def icon (self, name) :
       obj = self.getContext ()
       obj.item_icon = name
       print ("ICON", name)

   def tooltip (self, text) :
       obj = self.getContext ()
       obj.item_tooltip = text
       print ("TOOLTIP", text)

   def alpha (self) :
       self.info ("Function alpha")

   def beta (self) :
       self.info ("Function beta")

   def gamma (self, val) :
       self.info ("Function gamma (" + str (val) + ")")

   def delta (self, param1, param2) :
       self.info ("Function delta")

# --------------------------------------------------------------------------

if __name__ == "__main__" :

   # PYTHONPATH=directory_with_generated_parser python cmm_comp.py

   parser = CmmCompiler ()
   parser.openFile ("examples/example.t")
   result = parser.parse_declaration_list ()

# --------------------------------------------------------------------------

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
