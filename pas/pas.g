
/*
number
real_numbe
identifier
string_literal
character_literal
*/

label_ident <TLabelIdent> :
   id: identifier |
   num: number;

qualified_name <TQualName> :
   id:identifier
   ( <add> cont_name )* ;

cont_name <TContName> :
   <no_space> '.' <no_space> id:identifier ;

ifc_type <return TType> :
   simple_alias_type ;

param_type <select TType> :
   simple_alias_type |
   simple_string_type |
   simple_file_type ;

result_type <select TType> :
   simple_alias_type |
   simple_string_type ;

simple_alias_type <new TAliasType> :
   alias_name:qualified_name ;

simple_string_type <new TStringType> :
   "string" ;

simple_file_type <new TFileType> :
   "file" ;

/* ---------------------------------------------------------------------- */

index_expr_item <new TInxItem> :
   ref:expr ;

index_expr_list <new TInxList> :
   <add> index_expr_item ( ',' <add> index_expr_item )* ;

/* arguments */

arg_item <TArgItem> :
   value:expr
   ( ':' width:expr ( ':' digits:expr )? )? ;

arg_list <TArgSect> :
   <add> arg_item ( ',' <add> arg_item )* ;

/* set constructor */

elem_sect <TElemSect> :
   <add> elem_item ( ',' <add> elem_item )* ;

elem_item <TElemItem> :
   low:expr
   (
      ".."
      high:expr
   )? ;

/* structure constructor */

struct_item <TStructSect> :
   ( name:identifier ':' )?
   value:expr ;

struct_sect <TStructSect> :
   <add> struct_item
   (
     ',' <add> struct_item ( ',' <add> struct_item )*
   |
     ';' <add> struct_item ( ';' <add> struct_item )*
   )? ;

/* factor */

ident_expr <TIdentExpr:TExpr> :
   name:identifier
   <execute on_ident_expr> ;

int_value_expr <TIntValueExpr:TExpr> :
   value:number ;

float_value_expr <TFltValueExpr:TExpr> :
   value:real_number ;

string_value_expr <TStrValueExpr:TExpr> :
   value:string_literal ;

char_value_expr <TStrValueExpr:TExpr> :
   value:character_literal ; /* #digits */

nil_expr <TNilExpr:TExpr> :
   "nil" ;

sub_expr <TStructExpr:TExpr> :
   '(' value:expr ( ',' <add> expr )* ')' ;

not_expr <TNotExpr:TExpr> :
   "not" param:factor ;

plus_expr <TPlusExpr:TExpr> :
   '+' param:factor ;

minus_expr <TMinusExpr:TExpr> :
   '-' param:factor ;

adr_expr <TAdrExpr:TExpr> :
   '@' param:factor ;

set_expr <TSetExpr:TExpr> :
   '[' list:elem_sect ']' ;

super_expr <TSuperExpr:TExpr> :
   "inherited" name:identifier ;

string_type_expr <TStringExpr:TExpr> :
   "string" "(" param:expr ")" ;

variable <select TExpr> :
   ident_expr |
   sub_expr |
   super_expr ;

reference <choose TExpr> :
   variable
   (
      index_expr |
      call_expr |
      deref_expr |
      field_expr
   )* ;

index_expr <TIndexExpr:TExpr> :
   <store left:TExpr>
   '['
   list:index_expr_list
   ']'
   ;

call_expr <TCallExpr:TExpr> :
   <store func:TExpr>
   '('
   list:arg_list
   ')'
   ;

deref_expr <TDerefExpr:TExpr> :
   <store param:TExpr>
   '^'
   ;

field_expr <TFieldExpr:TExpr> :
   <store param:TExpr>
   <no_space>
   '.'
   <no_space>
   name:identifier
   <execute on_field_expr>
   ;

/* factor */

factor <select TExpr> :
   int_value_expr |
   float_value_expr |
   string_value_expr  |
   char_value_expr  |
   not_expr |
   plus_expr |
   minus_expr |
   adr_expr |
   nil_expr |
   set_expr |
   [ "string" '(' ] => string_type_expr |
   reference  ;

/* term */

term <choose TExpr> :
  factor
  (
     <new TTermExpr:TExpr>
     <store left:TExpr>
     (  '*'   <set fce=MulExp>  |
        '/'   <set fce=RDivExp> |
        "div" <set fce=DivExp>  |
        "mod" <set fce=ModExp>  |
        "shl" <set fce=ShlExp>  |
        "shr" <set fce=ShrExp>  |
        "and" <set fce=AndExp>  |
        "as"  <set fce=AsExp >  )
     right:factor
  )* ;

/* simple expression */

simple_expr <choose TExpr> :
  term
  (
     <new TSimpleExpr:TExpr>
     <store left:TExpr>
     (  '+'   <set fce=AddExp> |
        '-'   <set fce=SubExp> |
        "or"  <set fce=OrExp>  |
        "xor" <set fce=XorExp> )
     right:term
  )* ;

/* expression */

expr <choose TExpr> :
  simple_expr
  (
     <new TCompleteExpr:TExpr>
     <store left:TExpr>
     (  '='  <set fce=EqExp> |
        "<>" <set fce=NeExp> |
        '<'  <set fce=LtExp> |
        '>'  <set fce=GtExp> |
        "<=" <set fce=LeExp> |
        ">=" <set fce=GeExp> |
        "in" <set fce=InExp> |
        "is" <set fce=IsExp> )
     right:simple_expr
  )? ;

/* ---------------------------------------------------------------------- */

/* goto */

goto_stat <TGotoStat:TStat> :
  "goto" goto_lab:label_ident ;

/* begin end */

begin_stat <TBlockStat:TStat> :
  "begin"
  body_seq:stat_list
  "end" ;

stat_list <TStatSeq> :
   <new_line>
   <indent>
   <add> stat
   ( ';' <new_line> <add> stat )*
   <unindent>
   <new_line> ;

inner_stat <return TStat> :
   <new_line>
   <indent>
   stat
   <unindent> ;

/* if */

if_stat <TIfStat:TStat> :
  "if"
  cond_expr:expr
  "then"
  then_stat:inner_stat
  (
     <silent>
     "else"
     else_stat:inner_stat
  )? ;

/* case */

case_stat <TCaseStat:TStat> :
  "case"
  case_expr:expr
  "of"
  case_list:case_sect
  (
    "else"
    else_seq:stat_list
  )?
  "end" ;

case_sect <TCaseSect> :
  <add> case_item ( ';' <new_line> <add> case_item )*;

case_item <TCaseItem> :
   sel_list:elem_sect
   ':'
   sel_stat:inner_stat ;

/* while */

while_stat <TWhileStat:TStat> :
  "while" cond_expr:expr "do" body_stat:inner_stat;

/* repeat */

repeat_stat <TRepeatStat:TStat> :
  "repeat"
  body_seq:stat_list
  "until" until_expr:expr ;

/* for */

for_stat <TForStat:TStat> :
  "for"
  var_expr:variable
  ":="
  from_expr:expr
  ( "to" <set incr=true> | "downto" <set incr=false> )
  to_expr:expr
  "do"
  body_stat:inner_stat ;

/* with */

with_stat <TWithStat:TStat> :
  "with" with_list:with_sect "do" body_stat:inner_stat ;

with_sect <TWithSect> :
  <add> with_item ( ',' <add> with_item )* ;

with_item <TWithItem> :
  expr:variable ;

/* raise */

raise_stat <TRaiseStat:TStat> :
  "raise" ( raise_expr:expr )? ;

/* try */

try_stat <TTryStat:TStat> :
  "try"
  body_seq:stat_list
  (
    finally_branch:finally_part
  |
    except_branch:except_part
  )
  "end" ;

finally_part <TFinallyPart> :
  "finally"
  finally_seq:stat_list ;

except_part <TExceptPart> :
  "except"
  (
     on_list:on_sect
     ( "else" else_seq:stat_list )?
  |
     else_seq:stat_list
  );

on_sect <TOnSect> :
  <add>  on_item
  ( ';' <add> on_item )*
  ( ';' <set semicolon=true> )? ;

on_item <TOnItem> :
  "on"
  ( on_ident:identifier ':' )?
  on_type:type
  "do"
  body_stat:inner_stat ;

/* empty statement */

empty_stat <TEmptyStat:TStat> : ;

/* simple statement */

simple_stat <choose TStat> :
  expr
  (
     assign_stat
  |
     call_stat
  ) ;

assign_stat <TAssignStat:TStat> :
  <store left_expr:TExpr>
  ":="
  right_expr:expr
  ;

call_stat <TCallStat:TStat> :
  <store call_expr:TExpr>
  ;

/* labeled statement */

labeled_stat <TLabeledTStat:TStat> :
  lab:label_ident
  ':'
  body:stat ;

/* statement */

stat <select TStat> :
  // [ label_ident ':' ] => labeled_stat |
  goto_stat |
  begin_stat |
  if_stat |
  case_stat |
  while_stat |
  repeat_stat |
  for_stat |
  with_stat |
  raise_stat |
  try_stat |
  simple_stat |
  empty_stat;

/* ---------------------------------------------------------------------- */

param_ident <TParamIdent> :
  name:identifier
  <execute on_param>
  ;

param_item <TParamItem> :
  ( "var"   <set mode=VarParam>   |
    "const" <set mode=ConstParam> |
    "out"   <set mode=OutParam>   |
            <set mode=ValueParam> )

  <add> param_ident ( ',' <add> param_ident )*
  ( ':' typ:param_type ( '=' ini:expr )? )?
  <execute add_param>
  ;

formal_param_list <TParamSect> :
   (
      '('
          <add> param_item
          ( ';' <add> param_item )*
      ')'
   )? ;

property_param_list <TParamSect> :
   '['
      <add> param_item
      ( ';' <add> param_item )*
   ']';

/* ---------------------------------------------------------------------- */

class_type <TClassType:TType> :
   <execute open_class>
   "class"
   (
     '('
     parent:ifc_type
     ( ',' ifc_list:interface_sect )?
     ')'
   )?
   <indent>
   components:components_sect
   <unindent>
   "end"
   <execute close_class>  ;

interface_type <TInterfaceType:TType> :
   <execute open_interface>
  "interface"
   ( '(' ifc_list:interface_sect ')' )?
   <indent>
   components:components_sect // !?
   <unindent>
   "end"
   <execute close_interface> ;

interface_sect <TInterfaceSect> :
   <add> interface_item ( ',' <add> interface_item )* ;

interface_item <TIntefaceItem>:
   ifc:ifc_type ;

components_sect <TComponetsSect> :
   <add> components_first_item
   ( <add> components_item )* ;

components_item <TComponentsItem> :
   ( "private"   <set acs=PrivateAccess> |
     "protected" <set acs=ProtectedAccess> |
     "public"    <set acs=PublicAccess> |
     "published" <set acs=PublishedAccess> |
     "automated" <set acs=AutomatedAccess> )
   members:member_sect ;

components_first_item <TComponentsItem> :
   <set acs=PublicAccess>
   members:member_sect ;

member_sect <TDeclGroup> :
   ( <new_line> <add> member_decl )* ;

member_decl <select TDeclSect> :
   field_decl |
   method_decl |
   property_decl ;

/* field */

field_ident <TFieldItem> :
   name:identifier
   <execute on_field> ;

field_decl <TFieldDecl:TDeclSect> :
   <add> field_ident
   ( ',' <add> field_ident )*
   ':'
   typ:type
   ';'
   <execute add_field>
   ;

/* method */

method_decl <TProcDecl> :
   <execute open_proc>
   <modify> proc_head
   (
     "virtual" <set a_virtual=true> ';' |
     "dynamic" <set a_dynamic=true> ';' |
     // "message" a_message:expr ';' |
     "override" <set a_override=true> ';' |
     "abstract" <set a_abstract=true> ';'
   )*
   <execute close_proc> ;

/* property */

property_decl <TPropertyDecl:TDeclSect> :
  "property"
  name:identifier
  ( param_list:property_param_list )?
  ( ':' typ:result_type )?

  // ( "index" index:expr )?
  ( "read" a_read:expr )?
  ( "write" a_write:expr )?
  ( "stored" <set a_stored=true> )?
  ( "default" <set a_default=true> )?
  ( "nodefault" <set a_nodefault=true> )?
  ( "implements" a_implements:interface_sect )?

  ( ';' "default" <set a_def_array=true> )?
  ';' ;

/* ---------------------------------------------------------------------- */

/* enum */

enum_type <TEnumType:TType> :
   <execute simple_type>
   '(' elements:enum_sect ')' ;

enum_sect <TEnumSect> :
   <add> enum_item ( ',' <add> enum_item )* ;

enum_item <TEnumItem> :
   name:identifier ;

/* string */

string_type <TStringType:TType> :
   <execute simple_type>
   "string"
   ( '[' lim:expr ']' )? ;

/* array */

array_type <TArrayType:TType> :
   <execute simple_type>
  "array"
  ( '[' index_list:index_type_sect ']' )?
  "of"
  elem:type;

index_type_sect <TIndexTypeSect> :
   <add> index_type_item ( ',' <add> index_type_item )* ;

index_type_item <TIndexTypeItem> :
   index:type ;

/* record */

record_type <TRecordType:TType> :
   <execute simple_type>
  ( "packed" <set a_packed=true> )? 
  "record"
  fields:field_sect
  "end"
  ;

field_sect <TFieldDeclGroup> :
   ( <add> field_decl )* ;

/* pointer */

pointer_type <TPointerType:TType> :
   <execute simple_type>
   '^' elem:type;

/* set */

set_type <TSetType:TType> :
   <execute simple_type>
   "set" "of" elem:type;

/* file */

file_type <TFileType:TType> :
   <execute simple_type>
   "file" ( "of" elem:type )? ;

/* class of type */

class_of_type <TClassOfType:TType> :
   <execute simple_type>
  "class" "of" elem:type ;

/* procedure */

proc_type <TProcType:TType> :
   <execute simple_type>
   (
     "procedure" <set style = ProcedureStyle> |
     "function"  <set style = FunctionStyle>
   )

   param_list:formal_param_list
   ( ':' answer:result_type )?
   ( "of" "object" <set of_object=true> )?

   (
     "register" <set call_conv=RegisterCall> |
     "pascal"   <set call_conv=PascalCall> |
     "cdecl"    <set call_conv=CdeclCall> |
     "stdcall"  <set call_conv=StdcallCall> |
     "safecall" <set call_conv=SafecallCall>
   )? ;

/* other type */

range_type <TSubrangeType:TType> :
   <execute simple_type>
   low:simple_expr
   ".."
   high:simple_expr
   ;

alias_type <TAliasType:TType> :
   <execute simple_type>
   alias_name:qualified_name
   ;

/* type */

type <select TType> :
   string_type |
   array_type |
   set_type |
   file_type |
   record_type |
   class_type |
   class_of_type |
   interface_type |
   proc_type |
   pointer_type |
   [ range_type ] => range_type |
   [ enum_type ] => enum_type |
   alias_type ;

   /* !? packed */

/* ---------------------------------------------------------------------- */

/* labels */

label_decl <TLabelDecl> :
   name:label_ident ;

label_sect <TLabelSect:TDeclSect> :
   "label" <add> label_decl ( ',' <add> label_decl )* ';' ;

/* constants */

const_decl <TConstDecl> :
   name:identifier
   <execute on_const>
   ( ':' typ:type )? '=' val:expr ';'
   <execute add_const>
   ;

const_sect <TConstSect:TDeclSect> :
   "const" <add> const_decl ( <add> const_decl )* ;

/* types */

type_decl <TTypeDecl> :
   name:identifier
   <execute on_type>
   '=' typ:type ';'
   <execute add_type>
   ;

type_sect <TTypeSect:TDeclSect> :
   "type" <add> type_decl ( <add> type_decl )* ;

/* variables */

var_item <TVarItem> :
   name:identifier
   <execute on_var>
   ;

var_decl <TVarDecl> :
   <add> var_item ( ',' <add> var_item )*
   ':' typ:type
   ( '=' ini:expr )?
   ';'
   <execute add_var>
   ;

var_sect <TVarSect:TDeclSect> :
   "var"
   <indent>
   <new_line> <add> var_decl
   ( <new_line> <add> var_decl )*
   <unindent> ;

/* subroutine */

proc_head <modify TProcDecl:TDeclSect> :
   ( "class" <set a_static=true> )?

   ( "procedure"   <set style=ProcedureStyle>   |
     "function"    <set style=FunctionStyle>    |
     "constructor" <set style=ConstructorStyle> |
     "destructor"  <set style=DestructorStyle>  )

   proc_name:qualified_name
   // name:identifier
   <execute on_proc>
   param_list:formal_param_list
   ( ':' answer:result_type ) ?

   /*
   (
     "reintroduce" <set a_reintroduce=true> |
     "overload" <set a_overload=true>
   )?
   */

   /*
   (
     ( ';' <set semicolon2=true> )?
     ( "register" <set call_conv=RegisterCall> |
       "pascal"   <set call_conv=PascalCall>   |
       "cdecl"    <set call_conv=CdeclCall>    |
       "stdcall"  <set call_conv=StdcallCall>  |
       "safecall" <set call_conv=SafecallCall> )
     <set call_spec=true>
   )?
   */

   ';' ;

proc_decl <TProcDecl> :
   <execute open_proc>
   <modify> proc_head
   (
      "forward" <set a_forward=true>
   |
      <modify> proc_external <set external_spec=true>
   |
     ( "inline" ';' <set a_inline=true> )?
     local:decl_part
     <new_line>
     <execute on_begin_proc>
     "begin"
     body:stat_list
     <execute on_end_proc>
     "end"
     <execute on_tail_proc>
   )
   ';'
   <execute close_proc>
   <empty_line> ;

proc_external <modify TProcDecl> :
   "external" <set a_external=true>
   (
      a_lib:expr
      /* !?
      (
         "name"
         a_name:expr
      |
         "index"
         a_index:expr
      )?
      */
   )?
   ';' <empty_line> ;

proc_intf_decl <TProcDecl> :
   <execute open_proc>
   <modify> proc_head
   ( "inline" ';' <set a_inline=true> )?
   ( <modify> proc_external <set external_spec=true> )?
   <execute close_proc> ;

/* declarations */

intf_decl <select TDeclSect> :
   const_sect |
   type_sect |
   var_sect |
   proc_intf_decl ;

intf_decl_part <TDeclGroup> :
   ( <new_line> <add> intf_decl )* ;

decl <select TDeclSect> :
   label_sect |
   const_sect |
   type_sect |
   var_sect |
   proc_decl ;

decl_part <TDeclGroup> :
   ( <new_line> <add> decl )* ;

/* import */

import_item <new TImportItem> :
  name:identifier <execute on_import>
  ( "in" path:string_literal )? ;

import_sect <new TImportSect> :
  (
     <empty_line>
     "uses"
     <add> import_item
     ( ',' <add> import_item )*
     ';'
     <empty_line>
  )? ;

/* unit */

unit_decl <new TUnitModule:TModule> :
   <execute open_module>
   "unit" name:identifier <execute on_module> ';'
   <empty_line>
   "interface"
   <empty_line>
      intf_imports:import_sect
      intf_decl:intf_decl_part
   <empty_line>
   "implementation"
   <empty_line>
      impl_imports:import_sect
      impl_decl:decl_part
   (
     ( "initialization" init:stat_list )?
     ( "finalization" finish:stat_list )?
     <set no_begin=true>
   |
     "begin"
     init:stat_list
   )?
   "end" <no_space> '.'
   <execute close_module>
   ;

/* program */

program_decl <new TProgramModule:TModule> :
   <execute open_module>
   "program" name:identifier <execute on_module> ';'
   <empty_line>
   impl_imports:import_sect
   impl_decl:decl_part
   <new_line>
   "begin"
   init:stat_list
   "end" <no_space>  '.'
   <execute close_module>
   ;

/* library */

library_decl <new TLibraryModule:TModule> :
   <execute open_module>
   "library" name:identifier <execute on_module> ';'
   <empty_line>
   impl_imports:import_sect
   impl_decl:decl_part
   <new_line>
   "begin"
   init:stat_list
   "end" <no_space> '.'
   <execute close_module>
   ;

/* module */

module_decl <select TModule> <start> :
   unit_decl |
   program_decl |
   library_decl ;
