
class C;

enum Color { red, blue, green };

class C
{
   private:
      int x, y, z;
      char a [10];
   public:
      void move (int dx, int dy, int dz);
      C ();
      ~ C ();
};

void fce (char * s)
{
    for (int i = 1; i <= 3; i++)
       new C;
}

int main (int argc, char * * argv)
{
   fce ("Hello");
}
