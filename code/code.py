
# code.py

from __future__ import print_function

# --------------------------------------------------------------------------

class Item (object) :
   def __init__ (self) :
       self.item_name = ""
       self.item_context = None
       self.item_qual = ""

       self.item_icon = None
       self.item_ink = None
       self.item_paper = None
       self.item_tooltip = None

       self.src_file = -1
       self.src_line = -1
       self.src_column = -1
       self.src_pos = -1
       self.src_end = -1

       self.item_decl = None
       self.item_type = None
       self.foreign_obj = None

       self.item_code = None
       self.item_place = None

       self.item_label = ""
       self.item_block = [ ]

       self.attr_compile_time = False
       self.attr_field = False
       self.attr_context = False

   def __str__ (self) :
       return decl_to_text (self)

   def link_code (self, obj) :
       self.item_code = obj
       obj.item_ref = self

# --------------------------------------------------------------------------

class Declaration (Item) :
   def __init__ (self) :
       super (Declaration, self).__init__ ()

# --------------------------------------------------------------------------

class Scope (Declaration) :
   def __init__ (self) :
       super (Scope, self).__init__ ()

       self.item_dict = { }
       self.item_list = [ ]

       self.registered_scopes = { }

       self.foreign_obj = None

       self.default_scope = False
       self.hidden_scope = False # True ... do not print scope name
       self.search_only = False # True ... only for lookup, not for declarations

   def add (self, item) :
       self.item_dict [item.item_name] = item
       self.item_list.append (item)

       item.item_context = self

       if self.item_qual != "" :
          item.item_qual = self.item_qual + "." + item.item_name
       else :
          item.item_qual = item.item_name

# --------------------------------------------------------------------------

class Namespace (Scope) :
   def __init__ (self) :
       super (Namespace, self).__init__ ()
       self.item_icon = "namespace"
       self.item_expand = True

class Class (Scope) :
   def __init__ (self) :
       super (Class, self).__init__ ()
       self.item_icon = "class"
       self.base_classes = [ ]
       self.skip_code = False
       self.methods = [ ]

class Enum (Scope) :
   def __init__ (self) :
       super (Enum, self).__init__ ()
       self.item_icon = "enum"

class EnumItem (Declaration) :
   def __init__ (self) :
       super (EnumItem, self).__init__ ()
       self.item_icon = "variable"

class Variable (Scope) :
   def __init__ (self) :
       super (Variable, self).__init__ ()
       self.item_icon = "variable"

       self.is_function = False
       self.is_constructor = False
       self.is_destructor = False

       self.result_type = None

       self.item_body = None
       self.local_scope = Scope ()
       self.skip_code = False

       self.alt_create = ""
       self.alt_create_place = False
       self.alt_create_owner = False
       self.alt_setup = ""
       self.alt_setup_param = ""
       self.alt_ignore = False

def Function () :
    result = Variable ()
    result.is_function = True
    result.item_icon = "function"
    return result

class Typedef (Declaration) :
   def __init__ (self) :
       super (Typedef, self).__init__ ()
       self.item_icon = "type"
       self.item_type = None

# --------------------------------------------------------------------------

class Type (Item) :
   def __init__ (self) :
       super (Type, self).__init__ ()
       self.type_const = False
       self.type_volatile = False

   def __str__ (self) :
       return type_to_text (self)

class CompoundType (Type) :
   def __init__ (self) :
       super (CompoundType, self).__init__ ()
       self.type_from = None

# --------------------------------------------------------------------------

class SimpleType (Type) :
   def __init__ (self) :
       super (SimpleType, self).__init__ ()

       self.type_void = False
       self.type_bool = False
       self.type_char = False
       self.type_wchar = False
       self.type_short = False
       self.type_int = False
       self.type_long = False
       self.type_float = False
       self.type_double = False

       self.type_signed = False
       self.type_unsigned = False

class NamedType (Type) :
   def __init__ (self) :
       super (NamedType, self).__init__ ()
       self.type_name = ""
       self.type_decl = None
       self.type_args = None


# --------------------------------------------------------------------------

class PointerType (CompoundType) :
   def __init__ (self) :
       super (PointerType, self).__init__ ()

class ReferenceType (CompoundType) :
   def __init__ (self) :
       super (ReferenceType, self).__init__ ()

class ArrayType (CompoundType) :
   def __init__ (self) :
       super (ArrayType, self).__init__ ()

class FunctionType (CompoundType) :
   def __init__ (self) :
       super (FunctionType, self).__init__ ()

# --------------------------------------------------------------------------

class Unknown (Item) :
   def __init__ (self) :
       super (Unknown, self).__init__ ()

# --------------------------------------------------------------------------

class Method (object) :
   def __init__ (self) :
       self.name = ""
       self.body = None

# --------------------------------------------------------------------------

def type_to_text (t) :
    result = ""

    if isinstance (t, CompoundType) :
       if isinstance (t, PointerType) :
          result = "pointer to " + type_to_text (t.type_from)
       elif isinstance (t, ReferenceType) :
          result = "reference to " + type_to_text (t.type_from)
       elif isinstance (t, FunctionType) :
          result = "function returning " + type_to_text (t.type_from)
       elif isinstance (t, ArrayType) :
          result = "array of " +  + type_to_text (t.type_from)

    elif isinstance (t, NamedType) :
       result = t.type_name

    elif isinstance (t, SimpleType) :
       result = "<simple type>" # !?
       if t.type_void : result = "void"
       elif t.type_bool : result = "bool"
       elif t.type_char : result = "char"
       elif t.type_wchar : result = "wchar_t"
       elif t.type_short : result = "short"
       elif t.type_int : result = "int"
       elif t.type_long : result = "long"
       elif t.type_float : result = "float"
       elif t.type_double : result = "double"

       if t.type_signed :
          result = "signed " + result
       elif t.type_unsigned :
          result = "unsigned " + result

    if getattr (t, "type_const", False) :
       result = "const " + result
    if getattr (t, "type_volatile", False) :
       result = "volatile " + resultt

    return result

# --------------------------------------------------------------------------

def decl_to_text (decl) :
    result = ""

    ctx = decl.item_context
    while ctx != None :
       if ctx.item_name != "" :
          result = ctx.item_name + "." + result
       ctx = ctx.item_context

    if decl.item_name != "" :
       result = result + decl.item_name

    if result == "" :
       result = "???"

    return result

# --------------------------------------------------------------------------

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
