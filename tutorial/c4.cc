

void step (int p)
{
     int timer;

     OUTPUT_POWER (0, 1, 20*p);
     OUTPUT_START (0, 1);
     UI_WRITE (LED, p);

     TIMER_WAIT (500, timer);
     TIMER_READY (timer);

     OUTPUT_STOP (0, 1, 0);

     TIMER_WAIT (500, timer);
     TIMER_READY (timer);
}


int a;
int b;
int timer;

void main ()
{
     int c;
     a = 1;
     b = 7;

     c = a + 1;

     /* if (a > 0 && b > 0) */
     c = a + b;

     for (a = 1; a <= 3 ; ++a)
        step (a);


     /*
     for (a = 1; a <= 3 ; a=a+1)
     {
         OUTPUT_POWER (0, 1, 20*a);
         OUTPUT_START (0, 1);
         UI_WRITE (LED, a);

         TIMER_WAIT (500, timer);
         TIMER_READY (timer);

         OUTPUT_STOP (0, 1, 0);

         TIMER_WAIT (500, timer);
         TIMER_READY (timer);
     }
     */


     OUTPUT_STOP (0, 15, 0);
}
