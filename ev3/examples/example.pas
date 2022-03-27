Program Example;

Procedure Step (a: integer);
Var  timer: integer;
Begin
     OUTPUT_POWER (0, 1, 20*a);
     OUTPUT_START (0, 1);
     UI_WRITE (LED, a);

     TIMER_WAIT (500, timer);
     TIMER_READY (timer);

     OUTPUT_STOP (0, 1, 0);

     TIMER_WAIT (500, timer);
     TIMER_READY (timer);
End;

Var a, b, c: integer;
    timer: integer;

Begin
     a := 1;
     b := 7;
     c := a + b;

     for a := 1 to 3 do 
        Step (a);

     { 
     for a := 1 to 3 do begin
         OUTPUT_POWER (0, 1, 20*a);
         OUTPUT_START (0, 1);
         UI_WRITE (LED, a);

         TIMER_WAIT (500, timer);
         TIMER_READY (timer);

         OUTPUT_STOP (0, 1, 0);

         TIMER_WAIT (500, timer);
         TIMER_READY (timer);
     end;
     }
     

     { 
     OUTPUT_POWER (0, 1, 20);
     OUTPUT_START (0, 1);

     // UI_WRITE (LED, 2);

     TIMER_WAIT (1000, timer);
     TIMER_READY (timer);

     // OUTPUT_STOP (0, 1, 0);
     // UI_WRITE (LED, 3);

     // TIMER_WAIT (1000, timer);
     // TIMER_READY (timer);
     }

     OUTPUT_STOP (0, 15, 0);
End.
(* *)

(* 
Type Color = ( red, blue, green, yellow );

Type Point = record
                x, y, z: integer;
               end;

Var x, y, z : integer;
    timer: integer;

Procedure First;
Var  i, j, k: integer;
Begin
     OUTPUT_POWER (0, 1, 20);
     OUTPUT_START (0, 1);
     UI_WRITE (LED, 1 {LED_ORANGE} );

     TIMER_WAIT (1000, timer);
     TIMER_READY (timer);

     OUTPUT_STOP (0, 15, 0);

     k := 0;
     j := 1;
     for i := 1 to 10 do begin
         j := j + i ;
         k := k + j;
     end;

     while (k >= j) and (j>0) or (k > 0) and (i >= 0) do
        k := k - 10 * x + y div z;
End;

Procedure Second (p: integer; q: real);
Var  i: byteint;
     k: shortint;
     n: integer;
     r: real;
     b: boolean;
     t: char;
     s: string;
     // v : color;
     // a : array [1..10] of integer;
     // b : array [1..100] of real;
Begin
     n := 1;
     while n <= 10 do
        n := n + 1;
End;

Begin
     // First (1);
     y := 1;
     z := 2;
     // Second (y+1, z);
End.
*)