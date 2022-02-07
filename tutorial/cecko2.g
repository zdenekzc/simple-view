
while_stat < TWhileStat: TStat > :
   "while"
   "(" cond:expr ")"
   code:inner_stat ;

if_stat < TIfStat: TStat >  :
   "if"
   "(" cond:expr ")"
   then_code:inner_stat
   (
      <new_line>
      "else"
      else_code:inner_stat
   )?   ;

compound_stat < TCompoundStat: TStat > :
   "{"
    <indent>
    (
       <new_line>
       <add> stat
    )*
   <unindent>
   <new_line>
    "}" ;

simple_stat < TSimpleStat: TStat >:
   subexpr:expr
   ";" ;

empty_stat < TEmptyStat: TStat > :
   ";" ;

stat < select TStat > :
   while_stat | if_stat | compound_stat | simple_stat | empty_stat ;

inner_stat < return TStat > :
   <new_line>
   <indent>
   stat
   <unindent > ;

program < return TStat >:
   stat ;

// < expression TExpr >
< struct TExpr { enum kind; } >
< struct TBinaryExpr : TExpr {  } >

variable_expr <TVariableExpr:TExpr, kind=varExp> :
   name:identifier ;

value_expr <TValueExpr:TExpr, kind=valueExp> :
   value:number ;

subexpr_expr <TSubexprExpr:TExpr, kind=subexprExp> :
   "(" subexpr:expr ")" ;

simple_expr <select TExpr> :
   variable_expr| value_expr  | subexpr_expr ;

multiplicative_expr <choose TExpr>:
  simple_expr
  (
    <new TMulExpr:TBinaryExpr>
    <store left:TExpr>
    ( '*' <set kind=mulExp> |
      '/' <set kind=divExp> |
      '%' <set kind=modExp> )
    right:simple_expr
  )* ;

additive_expr <choose TExpr>:
  multiplicative_expr
  (
    <new TAddExpr:TBinaryExpr>
    <store left:TExpr>
    ( '+' <set kind=addExp> |
      '-' <set kind=subExp> )
    right:multiplicative_expr
  )* ;

relational_expr <choose TExpr>:
  additive_expr
  (
    <new TRelExpr:TBinaryExpr>
    <store left:TExpr>
    ( '<'  <set kind=ltExp> |
      '>'  <set kind=gtExp> |
      "<=" <set kind=leExp> |
      ">=" <set kind=geExp> )
    right:additive_expr
  )* ;

equality_expr <choose TExpr>:
  relational_expr
  (
    <new TEqExpr:TBinaryExpr>
    <store left:TExpr>
    ( "==" <set kind=eqExp> |
      "!=" <set kind=neExp> )
    right:relational_expr
  )* ;

logical_and_expr <choose TExpr>:
  equality_expr
  (
    <new TAndAndExpr:TBinaryExpr>
    <store left:TExpr>
    "&&" <set kind=logAndExp>
    right:equality_expr
  )* ;

logical_or_expr <choose TExpr>:
  logical_and_expr
  (
    <new TOrOrExpr:TBinaryExpr>
    <store left:TExpr>
    "||" <set kind=logOrExp>
    right:logical_and_expr
  )* ;

assignment_expr <choose TExpr>:
  logical_or_expr
  (
    <new TAssignExpr:TBinaryExpr>
    <store left:TExpr>
    ( '='   <set kind=assignExp>    )
    right:assignment_expr
  )? ;

expr <return TExpr> :
   assignment_expr;


