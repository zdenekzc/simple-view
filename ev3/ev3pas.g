
/*
number <primitive> : NUM_INT ;
real_number <primitive> : NUM_REAL ;
identifier  <primitive> <identifier> : IDENT ;
string_literal <primitive> : STRING_LITERAL ;
*/

label_ident <TLabelIdent> :
   id: identifier ;

param_type <select TType> :
   simple_alias_type |
   simple_string_type |
   simple_file_type ;

result_type <select TType> :
   simple_alias_type |
   simple_string_type ;

simple_alias_type <new TAliasType> :
   name:identifier ;

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

nil_expr <TNilExpr:TExpr> :
   "nil" ;

sub_expr <TSubExpr:TExpr> :
   '(' value:expr ')' ;

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

string_type_expr <TStringExpr:TExpr> :
   "string" "(" param:expr ")" ;

variable <select TExpr> :
   ident_expr |
   sub_expr ;

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
        "and" <set fce=AndExp>  )
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
        "in" <set fce=InExp> )
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
  <add> case_item
  ( ';' <new_line> <add> case_item )* ;

case_item <TCaseItem> :
   sel_list:elem_sect
   ':'
   sel_stat:inner_stat ;

/* while */

while_stat <TWhileStat:TStat> :
  "while" cond_expr:expr "do" body_stat:inner_stat ;

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
  right_expr:expr  ;

call_stat <TCallStat:TStat> :
  <store call_expr:TExpr> ;

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
  simple_stat |
  empty_stat ;

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

  <add> param_ident
  ( ',' <add> param_ident )*
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

/* ---------------------------------------------------------------------- */

/* enum */

enum_type <TEnumType:TType> :
   <execute simple_type>
   '(' elements:enum_sect ')' ;

enum_sect <TEnumSect> :
   <add> enum_item
   ( ',' <add> enum_item )* ;

enum_item <TEnumItem> :
   name:identifier ;

/* string */

string_type <TStringType:TType> :
   <execute simple_type>
   "string" ;

/* array */

array_type <TArrayType:TType> :
   <execute simple_type>
  "array"
  '[' index_list:index_type_sect ']'
  "of"
  elem:type ;

index_type_sect <TIndexTypeSect> :
   <add> index_type_item
   ( ',' <add> index_type_item )* ;

index_type_item <TIndexTypeItem> :
   index:type ;

/* record */

record_type <TRecordType:TType> :
   <execute simple_type>
  "record"
  ( <add> field_decl )*
  "end" ;

field_ident <TFieldItem> :
   name:identifier
   <execute on_field> ;

field_decl <TFieldDecl:TDeclSect> :
   <add> field_ident
   ( ',' <add> field_ident )*
   ':'
   typ:type
   ';'
   <execute add_field>  ;

/* pointer */

pointer_type <TPointerType:TType> :
   '^' elem:type;
/* set */

set_type <TSetType:TType> :
   <execute simple_type>
   "set" "of" elem:type ;

/* file */

file_type <TFileType:TType> :
   <execute simple_type>
   "file" ( "of" elem:type )? ;

/* other type */

range_type <TSubrangeType:TType> :
   <execute simple_type>
   low:simple_expr
   ".."
   high:simple_expr ;

alias_type <TAliasType:TType> :
   <execute simple_type>
   name:identifier ;

/* type */

type <select TType> :
   string_type |
   array_type |
   set_type |
   file_type |
   record_type |
   pointer_type |
   [ range_type ] => range_type |
   [ enum_type ] => enum_type |
   alias_type ;

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
   <new_line>
   <add> var_item
   ( ',' <add> var_item )*
   ':' typ:type
   ( '=' ini:expr )?
   ';'
   <execute add_var>
   ;

var_sect <TVarSect:TDeclSect> :
   "var"
   <indent>
   <add> var_decl
   ( <add> var_decl )*
   <unindent> ;

/* subroutine */

proc_head <modify TProcDecl:TDeclSect> :
   ( "procedure"   <set style=ProcedureStyle> |
     "function"    <set style=FunctionStyle>  )
   name:identifier
   <execute on_proc>
   param_list:formal_param_list
   ( ':' answer:result_type ) ?
   ';' ;

proc_decl <TProcDecl> :
   <execute open_proc>
   <modify> proc_head
   (
      "forward" <set a_forward=true>
   |
      local:local_decl_part
      <new_line>
      <execute on_begin_proc>
      "begin"
      body:stat_list
      <execute on_end_proc>
      "end"
   )
   ';'
   <execute close_proc> ;

proc_intf_decl <TProcDecl> :
   <execute open_proc>
   <modify> proc_head
   <execute close_proc> ;

/* declarations */

intf_decl <select TDeclSect> :
   const_sect |
   type_sect |
   var_sect |
   proc_intf_decl ;

intf_decl_part <TDeclGroup> :
   ( <new_line> <add> intf_decl )* ;

local_decl <select TDeclSect> :
   label_sect |
   const_sect |
   type_sect |
   var_sect ;

local_decl_part <TDeclGroup> :
   ( <new_line> <add> local_decl )* ;

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
  name:identifier <execute on_import> ;

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
     "begin"
     init:stat_list
   )?
   "end" <no_space> '.'
   <execute close_module>
   ;

/* program */

program_decl <new TProgramModule:TModule> :
   <execute open_module>
   "program" name:identifier  <execute on_module> ';'
   <empty_line>
   impl_imports:import_sect
   impl_decl:decl_part
   <new_line>
   "begin"
   init:stat_list
   "end" <no_space>  '.'
   <execute close_module>
   ;

/* module */

module_decl <select TModule> :
   unit_decl |
   program_decl ;
