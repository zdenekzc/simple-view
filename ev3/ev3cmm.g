
/* kit/grm/cmm.g */

/* --------------------------------------------------------------------- */

< expression CmmExpr >
< struct CmmExpr { enum kind; } >
< struct CmmBinaryExpr : CmmExpr {  } >
< struct CmmStat { enum stat; } >

/*
identifier
number
character_literal
string_literal
*/

/* --------------------------------------------------------------------- */

/* identifier expr */

ident_expr <CmmIdentExpr:CmmExpr, kind=identExp>:
   name:identifier
   <execute on_ident_expr> ;

/* primary expression */

primary_expr <select CmmExpr>:
    numeric_literal_expr
  | char_literal_expr
  | string_literal_expr
  | subexpr_expr
  | ident_expr
  ;

numeric_literal_expr <CmmNumValue:CmmExpr, kind=numValueExp>:
  value:number;

char_literal_expr <CmmCharValue:CmmExpr, kind=charValueExp>:
  value:character_literal;

string_literal_cont <CmmStringCont>:
  value:string_literal;

string_literal_expr <CmmStringValue:CmmExpr, kind=stringValueExp>:
  value:string_literal ;

subexpr_expr <CmmSubexprExpr:CmmExpr, kind=subexprExp>:
  '(' param:expr ')';

/* postfix expression */

postfix_start <select CmmExpr>:
    modern_cast_expr
  | type_change_expr // !?
  | primary_expr ; // !? last - important

type_change_expr <CmmTypechangeExpr:CmmExpr, kind=typechangeExp>: // !?
  (
    "signed"   <set a_signed = true>   |
    "unsigned" <set a_unsigned = true> |

    "short"    <set a_short=true> |
    "long"     <set a_long=true>  ( "long" <set a_long_long=true> )? |

    "bool"     <set a_bool = true>     |
    "char"     <set a_char = true>     |
    "int"      <set a_int = true>      |
    "float"    <set a_float = true>    |
    "double"   <set a_double = true>   |
    "void"     <set a_void = true>
  )
  '(' list:expr_list ')' ;

postfix_expr <choose CmmExpr>:
  postfix_start
  (
    index_expr |
    call_expr |
    field_expr |
    ptr_field_expr |
    post_inc_expr |
    post_dec_expr
  )* ;

index_expr <CmmIndexExpr:CmmExpr, kind=indexExp>:
  <store left:CmmExpr>
  '[' right:expr ']' ;

call_expr <CmmCallExpr:CmmExpr, kind=callExp>:
  <store param:CmmExpr>
  '(' list:expr_list ')' ;

field_expr <CmmFieldExpr:CmmExpr, kind=fieldExp>:
  <store param:CmmExpr>
  <no_space> '.' <no_space>
  name:identifier
  <execute on_field_expr> ;

ptr_field_expr <CmmPtrFieldExpr:CmmExpr, kind=ptrFieldExp>:
  <store param:CmmExpr>
  <no_space> "->" <no_space>
  name:identifier
  <execute on_field_expr> ;

post_inc_expr <CmmPostIncExpr:CmmExpr, kind=postIncExp>:
  <store param:CmmExpr>
  "++" ;

post_dec_expr <CmmPostDecExpr:CmmExpr, kind=postDecExp>:
  <store param:CmmExpr>
  "--" ;

expr_list <CmmExprList>:
  (
     <add> assignment_expr
     ( ',' <add> assignment_expr )*
  )? ;

/* unary expression */

unary_expr <select CmmExpr>:
    inc_expr
  | dec_expr
  | deref_expr
  | addr_expr
  | plus_expr
  | minus_expr
  | bit_not_expr
  | log_not_expr
  | sizeof_expr
  | allocation_expr
  | deallocation_expr
  | postfix_expr ; // !? last - important

inc_expr <CmmUnaryExpr:CmmExpr, kind=incExp>:
  "++" param:cast_expr;

dec_expr <CmmUnaryExpr:CmmExpr, kind=decExp>:
  "--" param:cast_expr;

deref_expr <CmmUnaryExpr:CmmExpr, kind=derefExp>:
  '*' param:cast_expr;

addr_expr <CmmUnaryExpr:CmmExpr, kind=addrExp>:
  '&' param:cast_expr;

plus_expr <CmmUnaryExpr:CmmExpr, kind=plusExp>:
  '+' param:cast_expr;

minus_expr <CmmUnaryExpr:CmmExpr, kind=minusExp>:
  '-' param:cast_expr;

bit_not_expr <CmmUnaryExpr:CmmExpr, kind=bitNotExp>:
  '~' param:cast_expr;

log_not_expr <CmmUnaryExpr:CmmExpr, kind=logNotExp>:
  '!' param:cast_expr;

sizeof_expr <CmmSizeofExp:CmmExpr, kind=sizeofExp>:
  "sizeof"
  (
     ( '(' type_id ')' ) =>
       '(' type:type_id ')'
  |
     value:unary_expr
  );

/* new */

allocation_expr <CmmNewExpr:CmmExpr, kind=newExp>:
  "new"
  type_spec:type_specifiers
  ptr:ptr_specifier_list
  ( <add> allocation_array_limit )* ;

allocation_array_limit <CmmNewArrayLimit>:
  '[' value:expr ']'  ;

/* delete */

deallocation_expr <CmmDeleteExpr:CmmExpr, kind=deleteExp>:
  "delete"
  ( '[' ']' <set a_array = true> )?
  param:cast_expr ;

/* cast expression */

cast_expr <select CmmExpr>:
  cast_formula
  |
  unary_expr ;

cast_formula <CmmCastFormula: CmmExpr>:
   "type_cast" '(' type:type_id ')' param:cast_expr ;

/* arithmetic and logical expressions */

multiplicative_expr <choose CmmExpr>:
  cast_expr
  (
    <new CmmMulExpr:CmmBinaryExpr>
    <store left:CmmExpr>
    ( '*' <set kind=mulExp> |
      '/' <set kind=divExp> |
      '%' <set kind=modExp> )
    right:pm_expr
    <execute on_binary_expr>
  )* ;

additive_expr <choose CmmExpr>:
  multiplicative_expr
  (
    <new CmmAddExpr:CmmBinaryExpr>
    <store left:CmmExpr>
    ( '+' <set kind=addExp> |
      '-' <set kind=subExp> )
    right:multiplicative_expr
    <execute on_binary_expr>
  )* ;

shift_expr <choose CmmExpr>:
  additive_expr
  (
    <new CmmShiftExpr:CmmBinaryExpr>
    <store left:CmmExpr>
    ( "<<" <set kind=shlExp> |
      ">>" <set kind=shrExp> )
    right:additive_expr
  )* ;

relational_expr <choose CmmExpr>:
  shift_expr
  (
    <new CmmRelExpr:CmmBinaryExpr>
    <store left:CmmExpr>
    ( '<'  <set kind=ltExp> |
      '>'  <set kind=gtExp> |
      "<=" <set kind=leExp> |
      ">=" <set kind=geExp> )
    right:shift_expr
  )* ;

equality_expr <choose CmmExpr>:
  relational_expr
  (
    <new CmmEqExpr:CmmBinaryExpr>
    <store left:CmmExpr>
    ( "==" <set kind=eqExp> |
      "!=" <set kind=neExp> )
    right:relational_expr
  )* ;

and_expr <choose CmmExpr>:
  equality_expr
  (
    <new CmmAndExpr:CmmBinaryExpr>
    <store left:CmmExpr>
    '&' <set kind=bitAndExp>
    right:equality_expr
  )* ;

exclusive_or_expr <choose CmmExpr>:
  and_expr
  (
    <new CmmXorExpr:CmmBinaryExpr>
    <store left:CmmExpr>
    '^' <set kind=bitXorExp>
    right:and_expr
  )* ;

inclusive_or_expr <choose CmmExpr>:
  exclusive_or_expr
  (
    <new CmmOrExpr:CmmBinaryExpr>
    <store left:CmmExpr>
    ( '|' <set kind=bitOrExp> )
    right:exclusive_or_expr
  )* ;

logical_and_expr <choose CmmExpr>:
  inclusive_or_expr
  (
    <new CmmAndAndExpr:CmmBinaryExpr>
    <store left:CmmExpr>
    "&&" <set kind=logAndExp>
    right:inclusive_or_expr
  )* ;

logical_or_expr <choose CmmExpr>:
  logical_and_expr
  (
    <new CmmOrOrExpr:CmmBinaryExpr>
    <store left:CmmExpr>
    "||" <set kind=logOrExp>
    right:logical_and_expr
  )* ;

/* conditional and assignment expression */

assignment_expr <choose CmmExpr>:
  logical_or_expr // !?
  (
    <new CmmAssignExpr:CmmBinaryExpr>
    <store left:CmmExpr>
    ( '='   <set kind=assignExp>    |
      "+="  <set kind=addAssignExp> |
      "-="  <set kind=subAssignExp> |
      "*="  <set kind=mulAssignExp> |
      "/="  <set kind=divAssignExp> |
      "%="  <set kind=modAssignExp> |
      "<<=" <set kind=shlAssignExp> |
      ">>=" <set kind=shrAssignExp> |
      "&="  <set kind=andAssignExp> |
      "^="  <set kind=xorAssignExp> |
      "|="  <set kind=orAssignExp>  |
      '?'   <set kind=condExp> middle:expr ':' )
    right:assignment_expr
  )? ;

conditional_expr <return CmmExpr>:
  assignment_expr ;

/* expression */

expr <choose CmmExpr>:
  assignment_expr
  (
    <new CmmCommaExpr:CmmBinaryExpr>
    <store left:CmmExpr>
    ( ',' <set kind=commaExp> )
    right:assignment_expr
  )* ;

/* constant expression */

const_expr <return CmmExpr>:
  conditional_expr ;

/* --------------------------------------------------------------------- */

/* statement */

stat <select CmmStat>:

     ( identifier ':' ) => labeled_stat |
     ( block_declaration_head ) => declaration_stat |
     expression_stat |
     empty_stat |

     compound_stat |
     case_stat |
     default_stat |
     if_stat |
     switch_stat |
     while_stat |
     do_stat |
     for_stat |
     break_stat |
     continue_stat |
     return_stat |
     goto_stat ;

/* nested_stat - statements with different output indentation */

nested_stat <return CmmStat>:
   <new_line>
   <indent>
   stat
   <unindent> ;

/* list of statements */

stat_list <CmmStatSect>:
   ( <new_line> <add> stat )* ;

/* conditions */

condition <CmmCondition>:
     ( condition_declaration ')' ) =>
        cond_decl:condition_declaration
  |
     cond_expr:expr
  ;

for_condition <CmmCondition>:
     ( condition_declaration ';' ) =>
        cond_decl:condition_declaration
  |
     cond_expr:expr
  ;

/* statements */

declaration_stat <CmmDeclStat:CmmStat, stat=declarationStat>:
  inner_decl:block_declaration ;

labeled_stat <CmmLabeledStat:CmmStat, stat=labeledStat>:
  lab:identifier ':'
  <new_line>
  body:stat ;

case_stat <CmmCaseStat:CmmStat, stat=caseStat>:
  "case" case_expr:expr ':'
  <new_line>
  body:stat;

default_stat <CmmDefaultStat:CmmStat, stat=defaultStat>:
  "default" ':'
  <new_line>
  body:stat;

expression_stat <CmmExprStat:CmmStat, stat=exprStat>:
  inner_expr:expr ';';

empty_stat <CmmEmptyStat:CmmStat, stat=emptyStat>:
  ';' ;

compound_stat <CmmCompoundStat:CmmStat, stat=compoundStat>:
  '{'
  <indent>
  body:stat_list
  <unindent>
  <new_line>
  '}' ;

if_stat <CmmIfStat:CmmStat, stat=ifStat>:
  "if" '(' cond:condition ')' then_stat:nested_stat
  (
    <silent>
    <new_line>
    "else"
     else_stat:nested_stat
  )? ;

switch_stat <CmmSwitchStat:CmmStat, stat=switchStat>:
  "switch" '(' cond:condition ')' body:nested_stat ;

while_stat <CmmWhileStat:CmmStat, stat=whileStat>:
  "while" '(' cond:condition ')' body:nested_stat ;

do_stat <CmmDoStat:CmmStat, stat=doStat>:
  "do" body:nested_stat "while" '(' cond_expr:expr ')' ';' ;

for_stat <CmmForStat:CmmStat, stat=forStat>:
  "for"
  '('
  ( from_expr:for_condition )?
  ';'
  (to_expr:expr)?
  ';'
  (cond_expr:expr)?
  ')'
  body:nested_stat ;

break_stat <CmmBreakStat:CmmStat, stat=breakStat>:
  "break" ';' ;

continue_stat <CmmContinueStat:CmmStat, stat=continueStat>:
  "continue" ';' ;

return_stat <CmmReturnStat:CmmStat, stat=returnStat>:
  "return" (return_expr:expr)? ';' ;

goto_stat <CmmGotoStat:CmmStat, stat=gotoStat>:
  "goto" goto_lab:identifier ';' ;

/* ---------------------------------------------------------------------- */

/* declaration */

declaration_list <CmmDeclSect>:
  ( <add> declaration <new_line> )* ;

declaration <select CmmDecl>:

  simple_declaration
  | empty_declaration
  | struct_declaration
  | enum_declaration
  | typedef_declaration
  ;

/* block declaration - used only in declaration_stat */

block_declaration <select CmmDecl>:

    simple_declaration
  | typedef_declaration
  ;

/* block declaration head - only for predicate */

block_declaration_head:
    simple_head
  | "typedef"
  ;

/* typedef declaration */

typedef_declaration <CmmTypedefDecl:CmmDecl>:
  "typedef"
  type_spec:type_specifiers
  inner_decl:declarator
  ';' ;

/* empty declaration */

empty_declaration <CmmEmptyDecl:CmmDecl>:
  ';' ;

/* ---------------------------------------------------------------------- */

/* declaration specifiers */

/* type specifiers */

type_specifiers <CmmTypeSpec>:
  (
    "const" <set a_const = true>
  |
    "volatile" <set a_volatile = true>
  )?
  (
    "signed" <set a_signed = true>
  |
    "unsigned" <set a_unsigned = true>
  )?
  (
     basic_name:identifier |

     "short"    <set a_short=true> |
     "long"     <set a_long=true>  |

     "bool"     <set a_bool = true>     |
     "char"     <set a_char = true>     |
     "int"      <set a_int = true>      |
     "float"    <set a_float = true>    |
     "double"   <set a_double = true>   |
     "void"     <set a_void = true>
  )
  <execute on_type_specifiers> ;

/* ---------------------------------------------------------------------- */

/* pointer specifiers */

ptr_specifier_list <CmmPtrSpecifierSect>:
  ( <add> ptr_specifier )* ;

ptr_specifier <CmmPtrSpecifier>:
    '*' <set pointer=true>
    <modify> ptr_cv_specifier_list
  |
    '&' <set reference=true>
    <modify> ptr_cv_specifier_list
  ;

ptr_cv_specifier_list <modify CmmPtrSpecifier>:
  (
    "const" <set cv_const = true>
  |
    "volatile" <set cv_volatile = true>
  )* ;

/* function and array specifiers */

cont_specifier_list <CmmContSpecifierSect>:
  ( <add> cont_specifier )* ;

cont_specifier <select CmmContSpecifier>:
    function_specifier
  |
    array_specifier ;

function_specifier <CmmFunctionSpecifier:CmmContSpecifier>:
  '('
  parameters:parameter_declaration_list
  ')' ;

array_specifier <CmmArraySpecifier:CmmContSpecifier>:
  '['
  (lim:expr)?
  ']' ;

/* parameter declarations */

parameter_declaration_list <CmmParamSect>:
  (
     <add> parameter_declaration
     ( ',' <add> parameter_declaration )*
  )? ;

parameter_declaration <CmmParamItem>:
  type_spec:type_specifiers
  decl:declarator ;
  ( '=' init:assignment_expr )? ;

/* ---------------------------------------------------------------------- */

/* simple declaration */

simple_declaration <CmmSimpleDecl:CmmDecl>:
  type_spec:type_specifiers
  <add> simple_item <execute on_simple_item>
  (
     <execute open_function>
     func_body:compound_stat
     <execute close_function>
  |
     (
        ','
        <add> simple_item
        <execute on_simple_item>
     )*
     ';'
  );

simple_item <CmmSimpleItem>:
  decl:declarator
  ( init:initializer )?
  ;

/* simple declaration head - only for predicate */

simple_head:
  type_specifiers
  declarator
  ( '=' | ',' | ';' )
  ;

/* condition declaration */

condition_declaration <CmmSimpleDecl>:
  type_spec:type_specifiers
  <add> simple_item
  ( ',' <add> simple_item )*
  // no semicolon
  ;

/* ---------------------------------------------------------------------- */

/* declarator */

declarator <CmmDeclarator>:
  ptr:ptr_specifier_list
  (
     name:identifier
     <execute on_declarator>
  |
     ( nested_declarator ) => // necessary
        '(' inner:declarator ')'
  )
  cont:cont_specifier_list
  ;

abstract_declarator <CmmDeclarator>:
  ptr:ptr_specifier_list
  (
     ( nested_declarator ) =>
        '(' inner:abstract_declarator ')'
  )?
  cont:cont_specifier_list
  ;

nested_declarator <CmmNestedDeclarator>:
  ( '(' <set something=true> )@
  ( '*' <set a_ptr = true> |
    '&' <set a_ref = true> );

/* ---------------------------------------------------------------------- */

/* type id */

type_id <CmmTypeId>: /* abstract_type_id */
  type_spec:type_specifiers
  decl:abstract_declarator ;

/* ---------------------------------------------------------------------- */

/* enum */

enum_declaration <CmmEnumDecl:CmmDecl>:
   <execute open_enum>
   "enum"
   name:identifier
   <execute on_enum>
   <new_line>
   '{'
      <indent>
      <add> enumerator
      ( ',' <add> enumerator )*
      <unindent>
   '}'
   ';'
   <execute close_enum> ;

enumerator <CmmEnumItem>:
  <new_line>
  name:identifier
  <execute on_enum_item>
  ( '=' init:const_expr )? ;

/* ---------------------------------------------------------------------- */

/* struct */

struct_declaration <CmmClassDecl:CmmDecl>:
  <execute open_struct>
  "struct"
  name:identifier
  <execute on_struct>
  (
    '{'
        <new_line>
        <indent>
        members:member_list
        <unindent>
    '}'
  )?
  // ( ';' <set with_semicolon=true> )?
  ';'
  <execute close_class> ;

/* members */

member_item <select CmmDecl>:
  simple_declaration

member_list <CmmDeclSect>:
  ( <add> member_item <new_line> )* ;

