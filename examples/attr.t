
class Identifier [[compile_time]] ;
class Variable [[compile_time]] ;
class Type [[compile_time]] ;
class Class [[compile_time]] ;

void first () [[ compile_time ]] [[ field ]] ;
void second () [[ compile_time, field ]] ;
void third (double val) ; // [[ compile_time, field ]] ;
void fourth (Identifier val) ; // [[ compile_time, field ]] ;

class C
{
   first;
   int n { first; second; }
   third (3.14) ;
   void f () { fourth (name); }
   C () { }
};

void alpha () [[ compile_time ]] ;
void beta () [[ compile_time ]] ;
void gamma (double val) [[ compile_time ]] ;
void delta (Type t, Identifier id) [[ compile_time ]] ;

int yellow;

class D
{
    alpha;
    bool b { beta; }
    gamma ( 1.4 ) g;
    delta ( "int", "name" ) ;
};
