
/* statements */

while_stat < CmmWhileStat: CmmStat > :
 "while"
 '(' cond:expr ')'
 body_stat:inner_stat ;

if_stat < CmmIfStat: CmmStat >  :
  "if"
  '(' cond:expr ')'
  then_stat:inner_stat
  (
     <new_line>
     "else"
     else_stat:inner_stat
  )? ;

for_stat <CmmForStat:CmmStat>:
  "for"
  '('
  ( from_expr:expr )?
  ';'
  ( cond_expr:expr )?
  ';'
  ( step_expr:expr) ?
  ')'
  body_stat:inner_stat ;

return_stat <CmmReturnStat:CmmStat>:
  "return"
  ( return_expr:expr )?
  ';' ;

compound_stat < CmmCompoundStat: CmmStat > :
  '{'
  <indent>
  ( <new_line> <add> stat )*
  <unindent>
   '}' ;

simple_stat < CmmSimpleStat: CmmStat >:
  inner_expr:expr
  ';' ;

decl_stat < CmmDeclStat: CmmStat >:
  "dcl" inner_decl:simple_decl ;

empty_stat < CmmEmptyStat: CmmStat > :
  ';' ;

stat < select CmmStat > :
  decl_stat |
  while_stat |
  if_stat |
  for_stat |
  return_stat |
  compound_stat |
  simple_stat |
  empty_stat ;

inner_stat < return CmmStat > :
  <indent>
  stat
  <unindent> ;

/* -------------------------------------------------------------------- */

/* expressions */

< struct CmmExpr { enum kind; } >
< struct CmmPostfixExpr : CmmExpr { CmmExpr left; } >
< struct CmmBinaryExpr : CmmExpr {  } >
< group expr * CmmExpr >

variable_expr <CmmVarExpr:CmmExpr, kind=varExp> :
  name:identifier
  <execute on_variable_expr> ;

int_value_expr <CmmIntValue:CmmExpr, kind=intValueExp> :
  value:number;

real_value_expr <CmmRealValue:CmmExpr, kind=realValueExp> :
  value:real_number;

char_value_expr <CmmCharValue:CmmExpr, kind=charValueExp> :
  value:character_literal;

string_value_expr <CmmStringValue:CmmExpr, kind=stringValueExp> :
  value:string_literal;

subexpr_expr <CmmSubexprExpr:CmmExpr, kind=subexprExp> :
  '(' inner_expr:expr ')' ;

sequence_expr <CmmSequenceExpr:CmmExpr, kind=sequenceExp> :
  '[' param:expr_list ']' ;

this_expr <CmmThisExpr:CmmExpr, kind=thisExp>:
  "this";

simple_expr <select CmmExpr> :
  variable_expr |
  int_value_expr |
  real_value_expr |
  char_value_expr |
  string_value_expr |
  subexpr_expr |
  sequence_expr |
  this_expr;

/* postfix expression */

postfix_expr <choose CmmExpr>:
  simple_expr
  (
     index_expr |
     call_expr |
     compound_expr |
     field_expr |
     ptr_field_expr |
     post_inc_expr |
     post_dec_expr
  )* ;

index_expr <CmmIndexExpr:CmmPostfixExpr, kind=indexExp>:
  <store left:CmmExpr>
  '[' param:expr_list ']' ;

call_expr <CmmCallExpr:CmmPostfixExpr, kind=callExp>:
  <store left:CmmExpr>
  '(' param_list:expr_list ')' ;

compound_expr <CmmCompoundExpr:CmmPostfixExpr, kind=compoundExp>:
  <store left:CmmExpr>
  body:compound_stat ;

field_expr <CmmFieldExpr:CmmPostfixExpr, kind=fieldExp>:
  <store left:CmmExpr>
  <no_space> '.' <no_space>
  name:identifier
  <execute on_field_expr> ;

ptr_field_expr <CmmPtrFieldExpr:CmmPostfixExpr, kind=ptrFieldExp>:
  <store left:CmmExpr>
  <no_space> "->" <no_space>
  name:identifier ;

post_inc_expr <CmmPostIncExpr:CmmPostfixExpr, kind=postIncExp>:
  <store left:CmmExpr>
  "++" ;

post_dec_expr <CmmPostDecExpr:CmmPostfixExpr, kind=postDecExp>:
  <store left:CmmExpr>
  "--" ;

/* unary expression */

unary_expr <select CmmExpr>:
  inc_expr |
  dec_expr |
  deref_expr |
  addr_expr |
  plus_expr |
  minus_expr |
  bit_not_expr |
  log_not_expr |
  allocation_expr |
  deallocation_expr |
  postfix_expr ;

inc_expr <CmmIncExpr:CmmExpr, kind=incExp>:
  "++" param:unary_expr;

dec_expr <CmmDecExpr:CmmExpr, kind=decExp>:
  "--" param:unary_expr;

deref_expr <CmmDerefExpr:CmmExpr, kind=derefExp>:
  '*' param:unary_expr;

addr_expr <CmmAddrExpr:CmmExpr, kind=addrExp>:
  '&' param:unary_expr;

plus_expr <CmmPlusExpr:CmmExpr, kind=plusExp>:
  '+' param:unary_expr;

minus_expr <CmmMinusExpr:CmmExpr, kind=minusExp>:
  '-' param:unary_expr;

bit_not_expr <CmmBitNotExpr:CmmExpr, kind=bitNotExp>:
  '~' param:unary_expr;

log_not_expr <CmmLogNotExpr:CmmExpr, kind=logNotExp>:
  '!' param:unary_expr;

allocation_expr <CmmNewExpr:CmmExpr, kind=newExp>:
  "new"
  type:identifier
  (
    '(' init_list:expr_list ')'
  )? ;

deallocation_expr <CmmDeleteExpr:CmmExpr, kind=deleteExp>:
  "delete"
  param:unary_expr ;

/* binary expressions */

multiplicative_expr <choose CmmExpr>:
  unary_expr
  (
     <new CmmMulExpr:CmmBinaryExpr>
     <store left:CmmExpr>
     ( '*' <set kind=mulExp> |
       '/' <set kind=divExp> |
       '%' <set kind=modExp> )
     right:unary_expr
  )* ;

additive_expr <choose CmmExpr>:
  multiplicative_expr
  (
     <new CmmAddExpr:CmmBinaryExpr>
     <store left:CmmExpr>
     ( '+' <set kind=addExp> |
       '-' <set kind=subExp> )
     right:multiplicative_expr
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

assignment_expr <choose CmmExpr>:
  logical_or_expr
  (
     <new CmmAssignExpr:CmmBinaryExpr>
     <store left:CmmExpr>
     ( '=' <set kind=assignExp>     |
        "+="  <set kind=addAssignExp> |
        "-="  <set kind=subAssignExp> )
     right:assignment_expr
  )? ;

expr <return CmmExpr> :
  assignment_expr ;

expr_list <CmmExprList>:
  (
     <add> expr
     ( ',' <add> expr )*
  )? ;

/* -------------------------------------------------------------------- */

namespace_decl <CmmNamespace:CmmDecl> :
  "namespace"
  name:identifier
  <execute open_namespace>
  <new_line>
  '{'
     <indent>
     ( <new_line> <add> decl ) *
     <unindent>
  '}'
  <execute close_namespace> ;

/* -------------------------------------------------------------------- */

class_decl <CmmClass:CmmDecl> :
  <execute begin_class>
  "class"
  name:identifier
  <execute open_class>
  <new_line>
  '{'
     <indent>
     ( <new_line> <add> simple_decl ) *
     <unindent>
  '}'
  <execute close_class>
  <execute end_class> ;

/* -------------------------------------------------------------------- */

enum_decl <CmmEnum:CmmDecl> :
  "enum"
  name:identifier
  <execute open_enum>
  '{'
     <add> enum_item
     ( ',' <add> enum_item ) *
  '}'
  <execute close_enum> ;

enum_item <CmmEnumItem:CmmDecl> :
  name:identifier
  <execute on_enum_item> ;

/* -------------------------------------------------------------------- */

template_decl <CmmTemplate:CmmDecl> :
  <execute begin_template>
  "template"
  '<'
  (
     <add> template_param
     ( ',' <add> template_param )*
     <set parameters=true>
  )?
  '>'
  <indent>
  inner_decl:decl
  <unindent>
  <execute end_template> ;

template_param <CmmTemplateParam> :
  name:identifier ;

/* -------------------------------------------------------------------- */

simple_decl <CmmSimpleDecl:CmmDecl> :
  type:identifier
  ( '*' <set pointer=true> )?
  name:identifier
  <execute on_simple_decl>
  (
     ( '=' init_value:expr )?
     ';'
     <set variable=true>
  |
     init_stat:compound_stat
  |
     <execute open_parameters>
     param_list:parameter_list
     <execute close_parameters>
     <new_line>
     <execute open_function>
     body:compound_stat
     <execute close_function>
  ) ;

parameter_list <CmmParamList> :
  '('
     (
        <add> parameter_decl
        ( ',' <add> parameter_decl )*
     )?
  ')' ;

parameter_decl <CmmParamDecl:CmmDecl> :
  type:identifier
  name:identifier
  <execute on_param_decl> ;

empty_decl <CmmEmptyDecl:CmmDecl> :
  ';' ;

/* -------------------------------------------------------------------- */

decl <select CmmDecl> :
  namespace_decl |
  class_decl |
  enum_decl |
  template_decl |
  simple_decl |
  empty_decl;

program <CmmDeclList> :
  <execute on_start_program>
  (
    <new_line>
    <add> decl
    <empty_line>
  )* ;

