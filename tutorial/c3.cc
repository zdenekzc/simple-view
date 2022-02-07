class Point
{
    int x;
    int y;
    long alpha;

    void add (int x0, int y0)
    {
        x = x + x0;
        y = y + y0;
    }
};

float g;

int n;
long sum;

void f ()
{
   n = 10;
   // sum = 0;
   while ( n > 0 )
   {
      if ( sum )
         sum = sum + n;
      else
         sum = sum * n;
      n = n - 1;
   }
}
