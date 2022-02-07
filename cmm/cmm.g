
/* cmm.g */

/* --------------------------------------------------------------------- */

< struct CmmExpr { enum kind; 
                   bool type_flag; 
                   bool remember_enable_declaration; 
                   ptr item_decl;
                   ptr item_type; 
                   str alt_assign;
                   str alt_connect;
                   str alt_connect_dcl;
                   str alt_connect_signal;
                  } >

< struct CmmName : CmmExpr { } >
< struct CmmBinaryExpr : CmmExpr {  } >

< struct CmmCondition { enum kind; } >
< struct CmmDeclarationCondition : CmmCondition { 
         ptr decl_spec;
         bool a_destructor;
} >

< struct CmmStat { enum mode; } >
< struct CmmDecl : CmmStat { } >

< struct CmmDeclarator { enum kind; } >
< struct CmmPtrSpecifier { enum kind; } >
< struct CmmContSpecifier { enum kind; } >

< struct CmmParam { enum kind; } >

< struct CmmTextStat : CmmStat, mode = textStat { str text; } >
< struct CmmEolStat : CmmStat, mode = eolStat >

< struct CmmIndentStat : CmmStat, mode = indentStat  >
< struct CmmUnindentStat : CmmStat, mode = unindentStat >

< struct CmmEmptyLineStat : CmmStat, mode = emptyLineStat >

< struct CmmCppOnlyStat : CmmStat, mode = cppOnlyStat { ptr inner_stat; } >
< struct CmmPythonOnlyStat : CmmStat, mode = pythonOnlyStat { ptr inner_stat; } >

< group expr * CmmExpr >
< group stat % CmmStat 
             : stat, flexible_stat, declaration, member_item 
             / nested_stat, continue_simple_declaration >
< group param * CmmParam >

< artificial stat, text_stat, CmmTextStat >
< artificial stat, eol_stat, CmmEolStat >
< artificial stat, indent_stat, CmmIndentStat >
< artificial stat, unindent_stat, CmmUnindentStat >
< artificial stat, empty_line_stat, CmmEmptyLineStat >
< artificial stat, cpp_only_stat, CmmCppOnlyStat >
< artificial stat, python_only_stat, CmmPythonOnlyStat >

< execute_on_entry_no_param 
     on_begin_flexible_expr : 
        flexible_stat,
        parameter_declaration,
        condition,
        template_arg >

< execute_on_fork_no_param 
     on_end_flexible_expr :
        flexible_stat,
        parameter_declaration,
        condition,
        template_arg >

< execute_on_choose 
     on_binary_expr :
        // postfix_expr,
        pm_expr,
        multiplicative_expr, 
        additive_expr, 
        shift_expr,
        relational_expr, 
        equality_expr,
        and_expr, 
        exclusive_or_expr, 
        inclusive_or_expr,
        logical_and_expr, 
        logical_or_expr, 
        assignment_expr,
        colon_expr,
        comma_expr >

< predicate_on_choose 
     is_binary_expression :
        // postfix_expr,
        pm_expr,
        // multiplicative_expr, 
        additive_expr, 
        shift_expr,
        relational_expr, 
        equality_expr,
        // and_expr, 
        exclusive_or_expr, 
        inclusive_or_expr,
        logical_and_expr, 
        logical_or_expr, 
        assignment_expr,
        colon_expr,
        comma_expr >

< predicate_on_choose 
     is_postfix_expression :
        postfix_expr >

< predicate_on_choose 
     is_multiplicative_expression :
        multiplicative_expr >

< predicate_on_choose 
     is_and_expression :
        and_expr >

< execute_on_end on_ident_expr : ident_expr >
< execute_on_end on_int_value : int_value >
< execute_on_end on_real_value : real_value >
< execute_on_end on_char_value : char_value >
< execute_on_end on_string_value : string_value >
< execute_on_end on_this_expr : this_expr >
< execute_on_end on_subexpr_expr : subexpr_expr >
< execute_on_end on_field_expr : field_expr >
< execute_on_end on_ptr_field_expr : ptr_field_expr >
< execute_on_end on_call_expr : call_expr >
< execute_on_end on_type_specifier : type_specifier >
< execute_on_end on_type_name : type_name >
< execute_on_end on_cv_specifier : const_specifier, volatile_specifier >
< execute_on_end on_bit_not_expr : bit_not_expr >

< execute_on_end 
     on_name_expr :
        base_variant >

< execute_on_begin_no_param 
     on_other_expr :
        int_value,
        real_value,
        char_value,
        string_value,
        this_expr,
        subexpr_expr,

        modern_cast_expr,
        typeid_expr,
        type_name,
        type_specifier,
        const_specifier,
        volatile_specifier,

        inc_expr,
        dec_expr,
        deref_expr,
        addr_expr,
        plus_expr,
        minus_expr,
        bit_not_expr,
        log_not_expr,
        sizeof_expr,
        allocation_expr,
        deallocation_expr,
        throw_expr,

        cast_formula >

/*
identifier
number
real_number
character_literal
string_literal
*/

/* --------------------------------------------------------------------- */

/* simple name */

simple_name <CmmSimpleName:CmmName, kind=simpleName>:
   id:identifier ; // only identifier

/* base name */

global_variant <select CmmName>:
   simple_name |
   special_function ;

global_name <CmmGlobalName:CmmName, kind=globalName>:
   "::"
   inner_name:global_variant ;

base_variant <select CmmName>:
   global_name |
   simple_name |
   special_function ;

template_name <CmmTemplateName:CmmName, kind=templateName>:
   <store left:CmmName>
   template_args:template_arg_list
   <execute on_template_args> ;

base_name <choose CmmName>:
   base_variant 
   <execute on_base_name>
   (
      { is_template }?
      template_name
   )? ;

/* compound name */

cont_name <CmmContName:CmmName, kind=contName>:
   id:identifier  // same as simple_name, but used in compound_name
   <execute on_cont_name> ;

destructor_name <CmmDestructorName:CmmName, kind=destructorName>:
   "~"
   inner_name:simple_name ;

cont_variant <select CmmName>:
   cont_name |
   special_function |
   destructor_name ;

compound_variant <choose CmmName>:
   cont_variant 
   (
      { is_cont_template }?
      template_name
   )? ;

compound_name <CmmCompoundName:CmmName, kind=compoundName>:
   <execute on_begin_compound_name> 
   <store left:CmmName>
   <no_space> "::" <no_space>
   right:compound_variant
   <execute on_compound_name> ;

/* qualified name */

qualified_name <choose CmmName>:
   base_name
   (
      compound_name
   )*;

/* --------------------------------------------------------------------- */

/* primary expression */

primary_expr <select CmmExpr>:
   ident_expr |
   int_value |
   real_value |
   char_value |
   string_value |
   this_expr |
   subexpr_expr  ;

ident_expr <return CmmName>:
   qualified_name ;

int_value <CmmIntValue:CmmExpr, kind=intValue>:
   value:number ;

real_value <CmmRealValue:CmmExpr, kind=realValue>:
   value:real_number ;

char_value <CmmCharValue:CmmExpr, kind=charValue>:
   value:character_literal ;

string_value <CmmStringValue:CmmExpr, kind=stringValue>:
   value:string_literal
   ( <add> string_value_cont )* ; // !?

string_value_cont <CmmStringCont>:
   value:string_literal ;

this_expr <CmmThisExpr:CmmExpr, kind=thisExp>:
   "this" ;

subexpr_expr <CmmSubexprExpr:CmmExpr, kind=subexprExp>:
   '(' param:expr ')' ;

/* postfix expression */

postfix_start <select CmmExpr>:
   primary_expr |
   modern_cast_expr |
   typeid_expr |
   type_name |
   type_specifier ;

modern_cast_expr <CmmModernCastExpr:CmmExpr, kind=modernCastExp>:
   ( "dynamic_cast"       <set cast_kind = DynamicCast> |
     "static_cast"        <set cast_kind = StaticCast>  |
     "const_cast"         <set cast_kind = ConstCast>   |
     "reinterpret_cast"   <set cast_kind = ReinterpreterCast> )
   '<' <no_space> type:type_id <no_space> '>'
   '(' param:expr ')' ;

typeid_expr <CmmTypeIdExpr:CmmExpr, kind=typeIdExp>:
   "typeid"
   '('
   value:expr
   ')' ;

postfix_expr <choose CmmExpr>:
   postfix_start
   (
      index_expr |
      call_expr |
      // compound_expr |
      field_expr |
      ptr_field_expr |
      post_inc_expr |
      post_dec_expr
   )* ;

index_expr <CmmIndexExpr:CmmExpr, kind=indexExp>:
   <store left:CmmExpr>
   '[' param:assignment_expr ']' ; // !?

call_expr <CmmCallExpr:CmmExpr, kind=callExp>:
   <store left:CmmExpr>
   '(' param_list:expr_list /* parameter_declaration_list */ ')' ;

// compound_expr <CmmCompoundExpr:CmmExpr, kind=compoundExp>:
//    <store left:CmmExpr>
//    body:compound_stat ;

field_expr <CmmFieldExpr:CmmExpr, kind=fieldExp>:
   <store left:CmmExpr>
   <no_space> '.' <no_space>
   simp_name:simple_name ;

ptr_field_expr <CmmPtrFieldExpr:CmmExpr, kind=ptrFieldExp>:
   <store left:CmmExpr>
   <no_space> "->" <no_space>
   simp_name:simple_name ;

post_inc_expr <CmmPostIncExpr:CmmExpr, kind=postIncExp>:
   <store left:CmmExpr>
   "++" ;

post_dec_expr <CmmPostDecExpr:CmmExpr, kind=postDecExp>:
   <store left:CmmExpr>
   "--" ;

expr_list <CmmExprList>:
   (
       <add> assignment_expr
       ( ',' <add> assignment_expr )*
   )? ;

/* unary expression */

unary_expr <select CmmExpr>:
   postfix_expr |
   inc_expr |
   dec_expr |
   deref_expr |
   addr_expr |
   plus_expr |
   minus_expr |
   bit_not_expr |
   log_not_expr |
   sizeof_expr |
   allocation_expr |
   deallocation_expr |
   throw_expr ;

inc_expr <CmmIncExpr:CmmExpr, kind=incExp>:
   "++" param:cast_expr ;

dec_expr <CmmDecExpr:CmmExpr, kind=decExp>:
   "--" param:cast_expr ;

deref_expr <CmmDerefExpr:CmmExpr, kind=derefExp>:
   '*' param:cast_expr ;

addr_expr <CmmAddrExpr:CmmExpr, kind=addrExp>:
   '&' param:cast_expr ;

plus_expr <CmmPlusExpr:CmmExpr, kind=plusExp>:
   '+' param:cast_expr ;

minus_expr <CmmMinusExpr:CmmExpr, kind=minusExp>:
   '-' param:cast_expr ;

bit_not_expr <CmmBitNotExpr:CmmExpr, kind=bitNotExp>:
   '~' param:cast_expr ;

log_not_expr <CmmLogNotExpr:CmmExpr, kind=logNotExp>:
   '!' param:cast_expr ;

sizeof_expr <CmmSizeofExp:CmmExpr, kind=sizeofExp>:
   "sizeof"
    value:unary_expr ;

/* new */

allocation_expr <CmmNewExpr:CmmExpr, kind=newExp>:
   "new"
   (
      type1:new_type_id
   |
      '(' type2:type_id ')'
   )
   (
      '(' init_list:expr_list ')'
   )? ;

new_type_id <CmmNewTypeId>:
   type_spec:type_specifiers
   ptr:ptr_specifier_list
   ( <add> allocation_array_limit )* ;

allocation_array_limit <CmmNewArrayLimit>:
   '[' value:expr ']'  ;

/* delete */

deallocation_expr <CmmDeleteExpr:CmmExpr, kind=deleteExp>:
   // ( "::" <set a_global = true> )?
   "delete"
   ( '[' ']' <set a_array = true> )?
   param:cast_expr ;

/* cast expression */

cast_expr <select CmmExpr>:
      cast_formula
   |
      unary_expr ;

cast_formula <CmmTypeCastExpr: CmmExpr, kind=typecastExp>:
   "type_cast" // !?
   '<' type:type_id '>'
   '(' param:cast_expr ')' ;

/* pm expression */

pm_expr <choose CmmExpr>:
   cast_expr
   (
      <new CmmPtrMemExpr:CmmExpr>
      <store left:CmmExpr>
      ( ".*"  <set kind=dotMemberExp> |
        "->*" <set kind=arrowMemberExp> )
      right:cast_expr
   )* ;

/* arithmetic and logical expressions */

multiplicative_expr <choose CmmExpr>:
   pm_expr
   (
      <new CmmMulExpr:CmmBinaryExpr>
      <store left:CmmExpr>
      ( '*' <set kind=mulExp> |
        '/' <set kind=divExp> |
        '%' <set kind=modExp> |
        { is_mul }? <set kind=customMulExp> custom_mul:identifier )
      right:pm_expr
   )* ;

additive_expr <choose CmmExpr>:
   multiplicative_expr
   (
      <new CmmAddExpr:CmmBinaryExpr>
      <store left:CmmExpr>
      ( '+' <set kind=addExp> |
        '-' <set kind=subExp> |
        { is_add }? <set kind=customAddExp> custom_add:identifier )
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
        '?'   <set kind=condExp> middle:assignment_expr ':' )
      right:logical_or_expr // !?
   )? ;

/* expression */

colon_expr <choose CmmExpr>:
   assignment_expr
   (
      <new CmmColonExpr:CmmBinaryExpr>
      <store left:CmmExpr>
      ':' <set kind=colonExp> // !?
      right:assignment_expr
   )? ;

comma_expr <choose CmmExpr>:
   colon_expr
   (
      <new CmmCommaExpr:CmmBinaryExpr>
      <store left:CmmExpr>
      ',' <set kind=commaExp>
      right:colon_expr
   )* ;

expr <return CmmExpr>:
   comma_expr ;

/* constant expression */

const_expr <return CmmExpr>:
   assignment_expr ;

/* --------------------------------------------------------------------- */

/* statement */

stat <select CmmStat>:

   flexible_stat |
   empty_stat |
   compound_stat |
   if_stat |
   while_stat |
   do_stat |
   for_stat |
   switch_stat |
   case_stat |
   default_stat |
   break_stat |
   continue_stat |
   return_stat |
   goto_stat |
   try_stat ;

nested_stat <return CmmStat>: /* statement with different output indentation */
   <indent>
   stat
   <unindent> ;

empty_stat <CmmEmptyStat:CmmStat, mode=emptyStat>:
   ';' ;

compound_stat <CmmCompoundStat:CmmStat, mode=compoundStat>:
   '{'
   <indent>
   ( <new_line> <add> stat )*
   <unindent>
   '}' ;

if_stat <CmmIfStat:CmmStat, mode=ifStat>:
   "if"
   '(' cond:expr ')'
   then_stat:nested_stat
   (
      <silent>
      <new_line>
      "else"
      else_stat:nested_stat
   )? ;

while_stat <CmmWhileStat:CmmStat, mode=whileStat>:
   "while"
   '(' cond:expr ')'
   body:nested_stat ;

do_stat <CmmDoStat:CmmStat, mode=doStat>:
   "do"
   body:nested_stat
   "while" '(' cond_expr:expr ')' ';' ;

for_stat <CmmForStat:CmmStat, mode=forStat>:
   "for"
   '('
   ( from_expr:condition )?
   (
      ':'
      iter_expr:expr
   |
      ';'
      (to_expr:expr)?
      ';'
      (cond_expr:expr)?
   )
   ')'
   body:nested_stat ;

switch_stat <CmmSwitchStat:CmmStat, mode=switchStat>:
   "switch"
   '(' cond:expr ')'
   body:nested_stat ;

case_stat <CmmCaseStat:CmmStat, mode=caseStat>:
   "case" case_expr:expr ':'
   <new_line>
   body:nested_stat ;

default_stat <CmmDefaultStat:CmmStat, mode=defaultStat>:
   "default" ':'
   <new_line>
   body:nested_stat ;

break_stat <CmmBreakStat:CmmStat, mode=breakStat>:
   "break" ';' ;

continue_stat <CmmContinueStat:CmmStat, mode=continueStat>:
   "continue" ';' ;

return_stat <CmmReturnStat:CmmStat, mode=returnStat>:
   "return" (return_expr:expr)? ';' ;

goto_stat <CmmGotoStat:CmmStat, mode=gotoStat>:
   "goto" goto_lab:identifier ';' ;

/* simple statement */

flexible_stat <choose CmmStat>:
   expr
   (
      { is_expression }?
      simple_stat
   |
      { is_expression }?
      block_stat
   |
      continue_simple_declaration
   ) ;

simple_stat <CmmSimpleStat:CmmStat, mode=simpleStat>:
   <store inner_expr:CmmExpr>
   ';'
   <execute on_simple_statement> ;

block_stat <CmmBlockStat:CmmStat, mode=blockStat>:
   <store inner_expr:CmmExpr>
   <new_line>
   body:compound_stat
   <execute on_block_statement> ;

/* ---------------------------------------------------------------------- */

/* declaration specifiers */

decl_specifiers <CmmDeclSpec>:
   (
      "inline"   <set a_inline = true>   |
      "virtual"  <set a_virtual = true>  |
      "explicit" <set a_explicit = true> |
      "mutable"  <set a_mutable = true>  |

      // "extern"   <set a_extern = true>   |
      "static"   <set a_static = true>   |
      // "auto"     <set a_auto = true>     |
      "register" <set a_register = true>
   )* ;

/* const / volatile */

const_specifier <CmmConstSpecifier:CmmExpr, kind=constSpec>:
   "const"
   param:type_specifiers ;

volatile_specifier <CmmVolatileSpecifier:CmmExpr, kind=volatileSpec>:
   "volatile"
   param:type_specifiers ;

/* type specifier */

type_specifier <CmmTypeSpec:CmmExpr, kind=typeSpec>:
   (
      "signed" <set a_signed = true>
   |
      "unsigned" <set a_unsigned = true>
   )?
   (
      "short"    <set a_short=true> |

      "long"     <set a_long=true> 
         ( 
            "long"   <set a_long_long=true> |
            "double" <set a_long_double=true>
         )? |

      "bool"     <set a_bool = true>   |
      "char"     <set a_char = true>   |
      "wchar_t"  <set a_wchar = true>  |
      "int"      <set a_int = true>    |
      "float"    <set a_float = true>  |
      "double"   <set a_double = true> |
      "void"     <set a_void = true>
   ) ;

/* typename */

type_name <CmmTypeName:CmmExpr, kind=typeName>:
   "typename"
   qual_name:qualified_name ;

/* type specifiers */

type_specifiers <select CmmExpr>:
   ident_expr | 
   type_name |
   type_specifier |
   const_specifier |
   volatile_specifier ;

/* ---------------------------------------------------------------------- */

ptr_specifier_list <CmmPtrSpecifierSect>:
   ( <add> ptr_specifier )* ;

ptr_specifier <select CmmPtrSpecifier>:
   pointer_specifier |
   reference_specifier ;

/* pointer specifiers */

pointer_specifier <CmmPointerSpecifier:CmmPtrSpecifier, kind=pointerSpec>:
   '*'
   cv_spec:cv_specifier_list ;

/* reference specifiers */

reference_specifier <CmmReferenceSpecifier:CmmPtrSpecifier, kind=referenceSpec>:
   '&'
   cv_spec:cv_specifier_list ;

cv_specifier_list <CmmCvSpecifier>:
   (
      "const" <set cv_const = true>
   |
      "volatile" <set cv_volatile = true>
   )* ;

/* ---------------------------------------------------------------------- */

cont_specifier_list <CmmContSpecifierSect>:
   ( <add> cont_specifier )* ;

cont_specifier <select CmmContSpecifier>:
   array_specifier |
   function_specifier ;

/* array specifier */

array_specifier <CmmArraySpecifier:CmmExpr, kind=arraySpec>:
   '['
   ( lim:expr )?
   ']' ;

/* function specifier */

function_specifier <CmmFunctionSpecifier:CmmExpr, kind=functionSpec>:
   '('
   parameters:parameter_declaration_list
   ')'
   ( "const" <set a_const = true> )?
   ( exception_spec:exception_specification )? ;

/* parameter declarations */

parameter_declaration_list <CmmParamSect>:
   (
      <add> parameter_declaration
      ( ',' <add> parameter_declaration )*
   )? ;

parameter_declaration <choose CmmParam>:
      assignment_expr
      (
         { is_value_parameter }?
         value_parameter 
      |
         plain_parameter
      |
         empty_parameter // !?
      ) 
   |
      dots_parameter
   ;

value_parameter <CmmValueParam:CmmParam, kind=valueParam>:
   <store inner_expr:CmmExpr> ;

plain_parameter <CmmPlainParam:CmmParam, kind=plainParam>:
   <store type_spec:CmmExpr> 
   decl:declarator
   ( init:initializer )? ;

empty_parameter <CmmEmptyParam:CmmParam, kind=emptyParam>: // !?
   <store type_spec:CmmExpr> ;
   decl:declarator ;

dots_parameter <CmmDotsParam:CmmParam, kind=dotsParam>:
   "..." ;

/* ---------------------------------------------------------------------- */

/* declarator */

declarator <choose CmmDeclarator>:
   ptr_specifier_list
   (
      basic_declarator |
      empty_declarator
   );

basic_declarator <CmmBasicDeclarator:CmmDeclarator, kind=basicDeclarator>:
   <store ptr_spec:CmmPtrSpecifierSect>
   qual_name:qualified_name 
   cont_spec:cont_specifier_list ;

empty_declarator <CmmEmptyDeclarator:CmmDeclarator, kind=emptyDeclarator>:
   <store ptr_spec:CmmPtrSpecifierSect>
   // cont_spec:cont_specifier_list  // !?
   ;

// abstract_declarator <CmmAbstractDeclarator:CmmDeclarator, kind=abstractDeclarator>:
//    <store ptr_spec:CmmPtrSpecifierSect>
//    cont_spec:cont_specifier_list ;

nested_declarator <CmmNestedDeclarator:CmmDeclarator, kind=nestedDeclarator>:
   <store ptr_spec:CmmPtrSpecifierSect>
   '(' 
   inner_declarator:declarator 
   ')' 
   cont_spec:cont_specifier_list ;

/* typedef declarator */

typedef_declarator <choose CmmDeclarator>:
   ptr_specifier_list
   (
      basic_declarator |
      nested_declarator 
   );

/* ---------------------------------------------------------------------- */

/* type id */

type_id <CmmTypeId>:
   type_spec:type_specifiers
   decl:declarator ;

/* ---------------------------------------------------------------------- */

/* initializer */

initializer <CmmInitializer>:
   '=' value:initializer_item ;

initializer_item <select CmmInitItem>:
   simple_initializer |
   initializer_list ;

simple_initializer <CmmInitSimple:CmmInitItem>:
   inner_expr:assignment_expr ;

initializer_list <CmmInitList:CmmInitItem>:
   '{'
   <indent>
   (
      <add> initializer_item
      (
         ','
         <new_line>
         <add> initializer_item
      )*
   )?
   <unindent>
   '}' ;

/* ---------------------------------------------------------------------- */

/* attributes */

attr_item <CmmAttr>:
   attr_expr:assignment_expr ;

attr_group <CmmAttrGroup>:
   "[[" 
   <add> attr_item
   (
      ','
      <add> attr_item
   )*
   "]]";

attr_list <CmmAttrSect>:
   ( <add> attr_group )* ;

/* ---------------------------------------------------------------------- */

/* simple declaration */

simple_declaration <CmmSimpleDecl:CmmStat, mode=simpleDecl>:
   ( decl_spec:decl_specifiers )? // !?
   ( '~' <set a_destructor = true> )?
   type_spec:type_specifiers
   modify_simple_declaration ;

continue_simple_declaration <CmmSimpleDecl:CmmStat>:
   <store type_spec:CmmExpr>
   modify_simple_declaration ;

modify_simple_declaration <modify CmmSimpleDecl>:
   <add> simple_item
   <execute on_simple_item>
   (
      ','
      <add> simple_item
      <execute on_simple_item>
   )*
   (
      (
        { is_constructor }? 
        ':' 
        <new_line> 
        ctor_init:ctor_initializer 
      )?
      <execute on_open_function>
      <new_line>
      body:compound_stat
      <execute on_close_function>
   |
      ';'
   ) 
   <execute on_simple_declaration> ;

simple_item <CmmSimpleItem>:
   decl:declarator 
   ( ':' width:const_expr )?
   ( init:initializer )? 
   attr:attr_list ;

/* condition  */

condition <choose CmmCondition>:
   expr
   (
      { is_expression }?
      condition_value 
   |
      condition_declaration
   ) ;

condition_declaration <CmmDeclarationCondition:CmmCondition, kind=declarationCondition>:
   <store type_spec:CmmExpr>
   (
      <add> simple_item
      <execute on_simple_item>
      (
         ','
         <add> simple_item
         <execute on_simple_item>
      )* 
   ) ;

condition_value <CmmValueCondition:CmmCondition, kind=valueCondition>:
   <store inner_expr:CmmExpr> ;

/* ---------------------------------------------------------------------- */

/* declaration */

declaration_list <CmmDeclSect> <start>:
   ( <add> declaration <new_line> )* ;

declaration <select CmmStat>:

   flexible_stat |
   empty_stat |
   compound_stat |
   if_stat |
   while_stat |
   for_stat |

   class_declaration |
   enum_declaration |

   typedef_declaration |
   friend_declaration |

   namespace_declaration |
   extern_declaration |
   using_declaration |

   template_declaration ;

/* ---------------------------------------------------------------------- */

/* namespace declaration */

namespace_declaration <CmmNamespaceDecl:CmmDecl, mode=namespaceDecl>:
   <execute on_start_namespace>
   "namespace"
   simp_name:simple_name
   attr:attr_list
   <execute on_namespace>
   <new_line>
   '{'
      <execute on_open_namespace>
      <new_line>
      <indent>
      body:declaration_list
      <unindent>
      <execute on_close_namespace>
   '}'
   <execute on_stop_namespace> ;

/* using declaration */

using_declaration <CmmUsingDecl:CmmDecl, mode=usingDecl>:
   "using"
   (
      "namespace" <set a_namespace = true>
   )?
   qual_name:qualified_name
   ';' ;

/* linkage declaration */

extern_declaration <CmmExternDecl:CmmDecl, mode=externDecl>:
   "extern"
   ( language:string_literal )?
   (
      '{' decl_list:declaration_list '}'
   |
      inner_declaration:declaration
   ) ;

/* typedef declaration */

typedef_declaration <CmmTypedefDecl:CmmDecl, mode=typedefDecl>:
   "typedef"
   type_spec:type_specifiers
   decl:typedef_declarator
   <execute on_typedef>
   ';' ;

/* friend declaration */

friend_declaration <CmmFriendDecl:CmmDecl, mode=friendDecl>:
   "friend"
   inner_declaration:declaration ;

/* ---------------------------------------------------------------------- */

/* enum */

enum_declaration <CmmEnumDecl:CmmDecl, mode=enumDecl>:
   <execute on_start_enum>
   "enum"
   simp_name:simple_name
   <execute on_enum>
   (
      <new_line>
      '{'
         <execute on_open_enum>
         <indent>
         enum_items:enum_list
         <unindent>
         <new_line>
         <execute on_close_enum>
      '}'
    )?
    ';'
    <execute on_stop_enum> ;

enum_list <CmmEnumSect>:
   (
      <add> enumerator
      ( ',' <add> enumerator )*
   )? ;

enumerator <CmmEnumItem>:
   <new_line>
   simp_name:simple_name
   <execute on_enum_item>
   ( '=' init_value:const_expr )? ;

/* ---------------------------------------------------------------------- */

/* class */

class_declaration <CmmClassDecl:CmmDecl, mode=classDecl>:
   <execute on_start_class>
   (
      "class"  <set style = ClassStyle> |
      "struct" <set style = StructStyle> |
      "union"  <set style = UnionStyle>
   )
   simp_name:simple_name
   attr:attr_list
   <execute on_class>
   (
      ( ':' base_list:base_specifier_list )?
      <new_line>
     '{'
        <execute on_open_class>
        <indent>
        members:member_list
        <unindent>
        <execute on_close_class>
     '}'
   )?
   ';'
   <execute on_stop_class> ;

/* members */

member_visibility <CmmMemberVisibility:CmmDecl, mode=visibilityDecl>:
   ( "private"   <set access = PrivateAccess> |
     "protected" <set access = ProtectedAccess> |
     "public"    <set access = PublicAccess> )
   <no_space> ':' ;

member_item <select CmmStat>:

   member_visibility |

   flexible_stat |
   empty_stat |
   compound_stat |
   if_stat |
   while_stat |
   for_stat |

   class_declaration |
   enum_declaration |

   typedef_declaration |
   friend_declaration |

   using_declaration |
   template_declaration ;

member_list <CmmDeclSect>:
   ( <add> member_item <new_line> )* ;

/* base specification */

base_specifier_list <CmmBaseSect>:
   <add> base_specifier
   ( ',' <add> base_specifier )* ;

base_specifier <CmmBaseItem>:
   ( "virtual" <set a_virtual = true> )?
   ( "private"   <set access = PrivateAccess> |
     "protected" <set access = ProtectedAccess> |
     "public"    <set access = PublicAccess> |
                 <set access = NoAccess> )
   from_cls:qualified_name ;

/* constructor initializer */

ctor_initializer <CmmCtorInitializer>:
   <indent>
   <add> member_initializer
   (
      ','
      <new_line>
      <add> member_initializer
   )*
   <unindent> ;

member_initializer <CmmMemberInitializer>:
   simp_name:simple_name // !? qualified_name
   '('
   params:expr_list
   ')' ;

/* ---------------------------------------------------------------------- */

/* special member functions */

conversion_specifiers <CmmConvSpec>: // !?
   type_spec:type_specifiers
   ptr_spec:ptr_specifier_list ;

special_function <CmmSpecialFuction:CmmName, kind=specialName>:
   "operator"
   (
      conv:conversion_specifiers // !?

   | "new"    <set spec_new=true>    // ( ('[' ']') => '[' ']' <set spec_new_array=true> )? // !?
   | "delete" <set spec_delete=true> // ( ('[' ']') => '[' ']' <set spec_delete_array=true> )?

   | "+" <set spec_add=true>
   | "-" <set spec_sub=true>
   | "*" <set spec_mul=true>
   | "/" <set spec_div=true>
   | "%" <set spec_mod=true>
   | "^" <set spec_xor=true>
   | "&" <set spec_and=true>
   | "|" <set spec_or=true>
   | "~" <set spec_not=true>

   | "!"  <set spec_log_not=true>
   | "="  <set spec_assign=true>
   | "<"  <set spec_lt=true>
   | ">"  <set spec_gt=true>
   | "+=" <set spec_add_assign=true>
   | "-=" <set spec_sub_assign=true>
   | "*=" <set spec_mul_assign=true>
   | "/=" <set spec_div_assign=true>
   | "%=" <set spec_mod_assign=true>

   | "^="  <set spec_xor_assign=true>
   | "&="  <set spec_and_assign=true>
   | "|="  <set spec_or_assign=true>
   | "<<"  <set spec_shl=true>
   | ">>"  <set spec_shr=true>
   | ">>=" <set spec_shl_assign=true>
   | "<<=" <set spec_shr_assign=true>
   | "=="  <set spec_eq=true>
   | "!="  <set spec_ne=true>

   | "<="  <set spec_le=true>
   | ">="  <set spec_ge=true>
   | "&&"  <set spec_log_and=true>
   | "||"  <set spec_log_or=true>
   | "++"  <set spec_inc=true>
   | "--"  <set spec_dec=true>
   | ","   <set spec_comma=true>
   | "->*" <set spec_member_deref=true>
   | "->"  <set spec_deref=true>

   | "(" ")" <set spec_call=true>
   | "[" "]" <set spec_index=true>
   ) ;

/* ---------------------------------------------------------------------- */

/* template declaration */

template_declaration <CmmTemplateDecl:CmmDecl, mode=templateDecl>:
   "template"
   (
      '<'
         params:template_param_list
      '>'
   )?
   inner_declaration:declaration
   <execute on_template_declaration> ;

template_param_list <CmmTemplateParamSect>:
   (
      <add> template_param
      ( ',' <add> template_param )*
   )? ;

/* template parameter */

template_param <select CmmTemplateParam>:
   template_type_param |
   template_normal_param ;

template_type_param <CmmTemplateTypeParam:CmmTemplateParam, kind=templateTypeParam>:
   (
      "template" '<' params:template_param_list '>'
   )?
   (
      "class" <set a_class = true>
   |
      "typename" <set a_typename = true>
   )
   ( simp_name:simple_name )? ;

template_normal_param <CmmTemplateNormalParam:CmmTemplateParam, kind=templateCommonParam>:
   type_spec:type_specifiers
   decl:declarator
   ( '=' init:shift_expr )? ; // !?

/* template arguments */

template_arg_list <CmmTemplateArgSect>:
   '<'
   (
      <add> template_arg
      ( ',' <add> template_arg )*
   )?
   '>' ;

template_arg <CmmTemplateArg>:
   // value:shift_expr; // !?
   value:parameter_declaration; // !?

/* ---------------------------------------------------------------------- */

/* try statement */

try_stat <CmmTryStat:CmmStat, mode=tryStat>:
   "try"
   <new_line>
   body:compound_stat
   handlers:handler_list ;

handler_list <CmmHandlerSect>:
   <add> handler
   ( <add> handler )* ;

handler <CmmHandlerItem>:
   <new_line>
   "catch"
   '('
   (
      type_spec:type_specifiers
      decl:declarator
   |
      "..." <set dots=true>
   )
   ')'
   <new_line>
   body:compound_stat ;

/* throw expression */

throw_expr <CmmThrowExpr:CmmExpr, kind=throwExp >:
   "throw" (inner_expr:assignment_expr)? ;

/* exception specification */

exception_specification <CmmExceptionSect>:
   "throw"
   '('
   (
      <add> exception_specification_item
      ( ',' <add> exception_specification_item )*
   )?
   ')' ;

exception_specification_item <CmmExceptionItem: CmmTypeDecl>:
   type:type_id ;

/* ---------------------------------------------------------------------- */

/* kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all */
