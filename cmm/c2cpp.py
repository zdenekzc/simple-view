
# c2cpp.py

from __future__ import print_function

from util import use_new_qt
from input import quoteString
from code import *
from cmm_parser import *
from cmm_product import Product

# --------------------------------------------------------------------------

class ToCpp (Product) :

   def __init__ (self) :
       super (ToCpp, self).__init__ ()
       self.class_stack = [ ]
       self.init_stack = [ False ]

   def send_program (self, decl_list) :
       self.send_declaration_list (decl_list)

   def comment (self, txt) :
       self.style_new_line ()
       self.send ("//")
       self.send (txt)
       self.style_new_line ()

   def put_dot (self) :
       self.style_no_space ()
       self.send (".")
       self.style_no_space ()

   def put_arrow (self) :
       self.style_no_space ()
       self.send ("->")
       self.style_no_space ()

   def put_colons (self) :
       self.style_no_space ()
       self.send ("::")
       self.style_no_space ()

   # -----------------------------------------------------------------------

   def custom_prefix (self, obj) :
       pass

   def custom_simple_declaration (self, simple_decl) :
       return False

   def custom_constructor_body (self, cls, stat) :
       self.send ("{")
       self.style_new_line ()
       self.send ("}")
       self.style_new_line ()

   # -----------------------------------------------------------------------

   def get_expr_value (self, expr) :
       return getattr (expr, "item_value", None)

   def send_expr (self, expr) :
       done = False

       # if expr.kind == expr.contName :
       #    self.send (expr.id)

       if expr.kind == expr.simpleName :
          if getattr (expr, "item_decl", None) != None :
             self.custom_prefix (expr.item_decl)

       if isinstance (expr, CmmName) :
          if hasattr (expr, "item_decl") :
             expr.item_value = self.get_expr_value (expr.item_decl)
             " copy loop parameter "

       value = self.get_expr_value (expr)
       if value != None :
          if value == True :
             self.send ("true")
          elif value == False :
             self.send ("false")
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
             self.send ("false")
             done = True

       if expr.kind == expr.logOrExp :
          left = self.get_expr_value (expr.left)
          if left == False :
             self.send_expr (expr.right)
             done = True
          elif left == True :
             self.send ("true")
             done = True

       if expr.kind == expr.callExp:
          # if self.get_expr_name (expr.left) == "write" : # !?
          #    self.write_function (expr)
          if getattr (expr, "skip_code", False) :
             done = True

       if not done :
          super (ToCpp, self). send_expr (expr)

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
          super (ToCpp, self). send_if_stat (stat)

   def send_for_stat (self, stat) :
       done = False

       target = None
       if stat.from_expr != None :
          expr = stat.from_expr
          # print ("EXPR", expr)
          if getattr (expr, "item_decl", None) != None :
             target = expr.item_decl
             # print ("TARGET", target.item_name, target)

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
          super (ToCpp, self). send_for_stat (stat)

   # -----------------------------------------------------------------------

   def code_block (self, decl) :
       self.send ("{")
       self.putEol ()
       self.incIndent ()

       for item in decl.item_list :
           self.send_declaration (item)

       self.decIndent ()
       self.send ("}")
       self.putEol ()

   def code_namespace (self, decll) :
       self.send ("enum")
       self.send (decl.item_name)
       self.putEol ()
       self.code_block (decl)
       self.send ("// end of " + decl.item_name )
       self.putEol ()

   def code_class (self, decl) :
       self.send ("class")
       self.send (decl.item_name)
       if len (decl.base_classes) != 0 :
          self.send (":")
          first = True
          for item in decl.base_classes :
             if not first :
                self.send (",")
             first = False
             self.send (item.item_name) # !?
       self.code_block (decl)
       self.send (";")
       self.send (" // end of " + decl.item_name )
       self.putEol ()

   def code_enum (self, decl) :
       self.send ("enum")
       self.send (decl.item_name)
       self.code_block (decl)
       self.send (";")
       self.putEol ()

   def code_typedef (self, decl) :
       self.send ("typedef")
       self.send (decl.item_name)
       self.send (";")
       self.putEol ()

   def code_variable (self, decl) :
       if decl.item_type != None :
          self.send (str (decl.item_type))
       self.send (decl.item_name)

   def code_function (self, decl) :
          if decl.result_type != None :
             self.send (str (decl.result_type))
          self.send (decl.item_name)
          self.send ("(")
          any = False
          for param in decl.parameters.item_list :
              if any :
                 self.put (", ")
              any = True
              if param.item_type != None :
                 self.send (str (param.item_type))
              self.send (param.item_name)
          self.send (")")

   def send_flexible_stat (self, stat) :
       if stat.mode == stat.simpleDecl :
          # done = self.custom_simple_expr (stat.type_spec)
          # if not done :
             self.send_simple_declaration (stat)
       elif stat.mode == stat.simpleStat :
          done = self.custom_simple_expr (stat.inner_expr)
          if not done :
             self.send_expr (stat.inner_expr)
             self.send (";")
       elif stat.mode == stat.blockStat :
          done = self.custom_simple_expr (stat.inner_expr)
          if not done :
             self.send_expr (stat.inner_expr)
             self.send (";")
             # self.send_compound_stat (stat.body)
             for item in stat.body.items :
                self.send_stat (item)

   def send_declaration (self, decl) :
       if isinstance (decl, Item) :
          if isinstance (decl, Namespace) :
             self.code_namespace (decl)
          elif isinstance (decl, Class) :
             self.code_class (decl)
          elif isinstance (decl, Enum) :
             self.code_enum (decl)
          elif isinstance (decl, Typedef) :
             self.code_enum (decl)
          elif isinstance (decl, Variable) :
             if decl.is_function :
                self.code_function (decl)
             else :
                self.code_variable (decl)
       else :
          super (ToCpp, self). send_stat (decl)

   # -----------------------------------------------------------------------

   def send_simple_declaration (self, stat) :
       only_init = self.init_stack [-1]

       if len (stat.items) == 0 :
          if not getattr (stat, "skip_code", False) :
              self.send_expr (stat.inner_expr)

       for item in stat.items :
           obj = item.item_ref
           if not obj.skip_code :
              # if getattr (obj, "method", "") != "" :
                 # self.send ("/* method: " + obj.method + " */")
                 # self.style_new_line ()
              # if getattr (obj, "special", "") != "" :
                 # self.send ("/* special: " + obj.special + " */")
                 # self.style_new_line ()
              if only_init :
                 done = self.custom_simple_expr (stat.type_spec)
                 if not done :
                    if item.init != None :
                       self.send_expr (stat.inner_expr)
                       self.send_initializer (item.init)
              else :
                 self.openSection (obj)
                 if stat.decl_spec != None :
                    self.send_decl_specifiers (stat.decl_spec)
                 if stat.a_destructor :
                    self.send ("~")
                 # self.send_type_specifiers (stat.type_spec)
                 self.send_expr (stat.type_spec)

                 # !?
                 dcl = item.decl
                 if dcl.kind == dcl.basicDeclarator :
                    self.send_ptr_specifier_list (dcl.ptr_spec)
                    name = dcl.qual_name
                    if name.kind == name.simpleName :
                       self.send (dcl.qual_name.id)
                    self.send_cont_specifier_list (dcl.cont_spec)
                 # self.send_declarator (item.decl)
                 if item.init != None :
                    self.send_initializer (item.init)

                 if stat.body != None :
                    if obj.is_function : # !?
                       if stat.ctor_init != None :
                          self.send (":")
                          self.style_new_line ()
                          self.send_ctor_initializer (stat.ctor_init)
                       self.style_new_line ()
                       if obj.is_constructor :
                          self.custom_constructor_body (obj.item_context, stat.body);
                       else :
                          self.send_compound_stat (stat.body)
                    else :
                        self.send (";")
                        self.style_new_line ()
                        for item in stat.body.items :
                           if item.mode == item.simpleDecl :
                              self.send_simple_declaration (item)

                 else :
                    self.send (";")
                    self.style_new_line ()
                 self.closeSection ()

   # -----------------------------------------------------------------------

   def default_constructor (self, cls) :
       self.style_empty_line ()
       # self.send (cls.item_name) # !?
       # self.put_colons ()
       self.send (cls.item_name)
       self.send ("(")
       self.send (")")
       self.style_new_line ()
       self.custom_constructor_body (cls, None)

   """
   def custom_member_declaration_body (self, target, body) :
       for decl in body.items :
           if decl.mode == decl.simpleDecl :
              for item in decl.items :
                 obj = item.item_ref
                 if obj != None and obj.item_context == target :
                    self.send_simple_item (item)
                    self.style_new_line ()

   def custom_member_declaration (self, target, decl) :
       if decl.mode == decl.simpleDecl :
          for item in decl.items :
              obj = item.item_ref
              if not obj.is_function :
                 if decl.body != None :
                    self.custom_member_declaration_body (target, decl.body)
       if decl.mode == decl.blockStat :
           self.custom_member_declaration_body (target, decl.body)
   """

   def send_class_declaration (self, decl) :
       cls = decl.item_ref
       if not cls.skip_code :
          self.class_stack.append (cls)
          self.openSection (cls)

          if decl.style == decl.ClassStyle :
             self.send ("class")
          elif decl.style == decl.StructStyle :
             self.send ("struct")
          elif decl.style == decl.UnionStyle :
             self.send ("union")
          self.send_expr (decl.simp_name)
          # self.send_attr_list (decl.attr)

          if decl.members != None :
             if decl.base_list != None :
                self.send (":")
                self.send_base_specifier_list (decl.base_list)
             self.style_new_line ()
             self.send ("{")
             self.style_indent ()
             self.send_member_list (decl.members)
             # for item in decl.members.items :
             #     self.send_member_item (item)
             #     self.style_new_line ()
             #     self.custom_member_declaration (cls, item)
             # for item in cls.item_list :
             #     self.send_declaration (item)
             #     self.style_new_line ()
                 # self.custom_member_declaration (cls, item)

             "default constructor"
             any = False
             for item in cls.item_list :
                 if getattr (item, "is_constructor", False) :
                    any = True
             if not any :
                self.default_constructor (cls)

             "additional (generated) methods"
             for method in cls.methods :
                 self.send ("void")
                 self.send (method.name)
                 self.send ("(")
                 self.send (")")
                 self.style_new_line ()
                 # self.send ("{")
                 # self.style_new_line ()
                 # self.style_indent ()
                 self.send_compound_stat (method.body)
                 # self.style_unindent ()
                 # self.send ("}")
                 #self.style_new_line ()
                 self.style_empty_line ()

             "end of class declaration"
             self.style_unindent ()
             self.send ("}")

          self.send (";")
          self.style_empty_line ()
          self.closeSection ()
          self.class_stack.pop ()

# --------------------------------------------------------------------------

class ToQtCpp (ToCpp) :

   def __init__ (self) :
       super (ToQtCpp, self).__init__ ()

   def custom_prefix (self, obj) :
       ctx = obj.item_context
       names = [ ]
       while ctx != None and not isinstance (ctx, Class) :
          if getattr (ctx, "is_function", False) : # !?
             ctx = None
          else:
             if not ctx.hidden_scope :
                names.insert (0, ctx.item_name)
             ctx = ctx.item_context
       for name in names :
           self.send (name)
           self.put_arrow () # !?

   # -----------------------------------------------------------------------

   def custom_left (self, expr) :
       self.custom_prefix (expr.left.item_decl)
       # self.style_no_space ()
       # self.send (".")
       # self.style_no_space ()

   def custom_assign (self, expr) :
       done = False
       special = expr.alt_assign
       if special != "" :
          if special.startswith ("<") :
             if special == "<setIcon>" :
                self.custom_left (expr)
                self.send ("setIcon")
                self.send ("(")
                self.send ("QIcon")
                self.put_colons ()
                self.send ("fromTheme")
                self.send ("(")
                self.send_expr (expr.right)
                self.send (")")
                self.send (")")
                self.send (";")
                self.style_new_line ()
                done = True
             elif special == "<setShortcut>" :
                self.custom_left (expr)
                self.send ("setShortcut")
                self.send ("(")
                self.send ("QKeySequence")
                self.send ("(")
                self.send_expr (expr.right)
                self.send (")")
                self.send (")")
                self.send (";")
                self.style_new_line ()
                done = True
             else :
                if special == "<text>" :
                   self.custom_left (expr)
                   self.send ("setText")
                elif special == "<icon>" :
                   self.custom_left (expr)
                   self.send ("setIcon")
                elif special == "<foreground>" :
                   self.custom_left (expr)
                   self.send ("setForeground")
                elif special == "<background>" :
                   self.custom_left (expr)
                   self.send ("setBackground")
                else :
                   self.custom_left (expr)
                   self.send (special) # !?
                self.send ("(")
                self.send ("0")
                self.send (",")
                if special == "<icon>" or special == "<setIcon>" :
                   self.send ("QIcon")
                   self.put_colons ()
                   self.send ("fromTheme")
                   self.send ("(")
                   self.send_expr (expr.right)
                   self.send (")")
                elif special == "<foreground>" or special == "<background>" :
                   self.send ("QColor")
                   self.send ("(")
                   self.send_expr (expr.right)
                   self.send (")")
                else :
                   self.send_expr (expr.right)
                self.send (")")
                self.send (";")
                self.style_new_line ()
                done = True
          else :
             self.custom_left (expr)
             self.send (special)
             self.send ("(")
             self.send_expr (expr.right)
             self.send (")")
             self.send (";")
             self.style_new_line ()
             done = True
       return done

   # -----------------------------------------------------------------------

   def custom_simple_expr (self, expr) :
       done = False

       if expr.kind == expr.assignExp :
          done = self.custom_assign (expr)

       special = expr.alt_connect
       if special != "" :
          self.send ("QObject")
          self.put_colons ()
          self.send ("connect")
          self.send ("(")
          # self.custom_prefix (expr.alt_connect_dcl)
          self.put_place (expr.alt_connect_dcl)
          self.send (",")
          self.send (quoteString (expr.alt_connect_signal))
          self.send (",")
          self.send ("this")
          self.send (",")
          self.send ("&")
          self.style_no_space ()
          # self.send (cls.item_name) # !?
          # self.put_colons ()
          self.send (special)
          self.send (")")
          self.send (";")
          self.style_new_line ()
          done = True

       return done

   # -----------------------------------------------------------------------

   """
   def find_type (self, name) :
       result = None
       if name in self.foreign_types :
          result = self.foreign_types [name]
       else :
          for module in self.foreign_modules :
              if name in module.__dict__ :
                 result = module.__dict__ [name]
                 self.foreign_types [name] = result
                 # print ("FOUND", name, result)
       return result

   def is_subtype (self, obj, name) :
       type = self.find_type (name)
       result = obj != None and type != None and issubclass (obj, type)
       # print ("CHECK", obj, type, result)
       return result
   """

   def put_place (self, var) :
       if isinstance (var.item_place, Class) :
          self.send ("this")
       else :
          self.send (var.item_place.item_name)

   # -----------------------------------------------------------------------

   def custom_variable_initialization (self, var) :
       self.send ("=")

       done = False
       special = var.alt_create
       if special != "" :
          done = True
          if special.startswith ("<") :
              if special == "<menuBar>" :
                 self.send ("menuBar ();")
              elif special == "<addToolBar>" :
                 self.send ("addToolBar (\"\");")
              elif special == "<statusBar>" :
                 self.send ("statusBar ();")
              elif special == "<addMenu>" :
                 self.send ("addMenu (\"\");")
              elif special == "<addAction>" :
                 self.put_place (var)
                 self.put_arrow ()
                 self.send ("addAction (\"\");")

          elif special == "<false>" :
             self.send ("false")
          elif special == "<char_zero>" :
             self.send ("0")
          elif special == "<zero>" :
            self.send ("0")
          elif special == "<real_zero>" :
            self.send ("0.0")
          elif special == "<empty_string>" :
            self.send ("\"\"")
          elif special == "<null>" :
             self.send ("NULL") # !?

          else :
             self.send ("new")
             self.send (special)
             self.send ("(")
             if var.alt_create_owner :
                self.send ("this")
             if var.alt_create_place :
                self.put_place (var)
             self.send (")")
             self.send (";")

   # -----------------------------------------------------------------------

   def custom_variable_placement (self, var) :
       special = var.alt_setup
       if special != "" :
          if special == "<layout>" :
             self.send ("QWidget * temp = new QWidget ();")
             self.style_new_line ()
             self.send ("temp.setLayout (")
             self.send (var.item_name)
             self.send (");")
             self.style_new_line ()
             self.send ("self.setCentralWidget (temp);")
             self.style_new_line ()
          elif special == "<setCentralWidget>" :
             self.send ("self.setCentralWidget (")
             self.custom_prefix (var)
             self.send (var.item_name)
             self.send (");")
             self.style_new_line ()
          else :
             func_name = var.alt_setup
             func_param = var.alt_setup_param
             self.put_place (var)
             self.put_arrow ()
             self.send (func_name)
             self.send ("(")
             self.send (var.item_name)
             if func_param != "" :
                self.send (",")
                self.send (func_param)
             self.send (")")
             self.send (";")
             self.style_new_line ()

   # -----------------------------------------------------------------------

   def custom_begin_of_constructor (self, cls) :
       for var in cls.item_list :
          if isinstance (var, Variable) and not var.is_function :
             if var.item_body != None :
                self.comment (var.item_name)
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

             self.init_stack.append (True)
             if var.item_body != None :
                for item in var.item_body.items :
                    self.send_stat (item)
                    self.style_new_line ()
             self.init_stack.pop ()

   def custom_constructor_body (self, cls, stat) :
       self.send ("{")
       self.style_new_line ()
       self.style_indent ()

       self.custom_begin_of_constructor (cls)
       if stat != None :
          for item in stat.items :
             self.send_stat (item)

       self.style_unindent ()
       self.send ("}")
       self.style_new_line ()
       self.style_empty_line ()

   # -----------------------------------------------------------------------

   def send_program (self, decl_list) :
       self.putLn ("#include <QApplication>")
       if use_new_qt :
          self.putLn ("#include <QtWidgets>")
       else :
          self.putLn ("#include <QtGui>")
       super (ToQtCpp, self).send_program (decl_list)
       if use_new_qt :
          self.putLn ("// compile: -P Qt5Widgets")
       else :
          self.putLn ("// compile: -P QtGui")
       self.putLn ("// compile: -lstdc++ -fPIC")
       self.putLn ("// kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all")

# --------------------------------------------------------------------------

class ToCustomCpp (ToQtCpp) :

   def __init__ (self) :
       super (ToCustomCpp, self).__init__ ()

   def send_text_stat (self, stat) :
       self.put (stat.text)

   def send_eol_stat (self, stat) :
       self.putEol ()

   def send_indent_stat (self, stat) :
       self.incIndent ()

   def send_unindent_stat (self, stat) :
       self.decIndent ()

   def send_empty_line_stat (self, stat) :
       self.style_empty_line ()

   def send_cpp_only_stat (self, stat) :
       self.send_stat (stat.inner_stat)

   def send_python_only_stat (self, stat) :
       pass


# --------------------------------------------------------------------------

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
