#! /usr/bin/env python

from __future__ import print_function

import sys, re, subprocess

if sys.version_info >= (3,) :
   def conv (s) :
       return str (s, "utf-8")
else :
   def conv (s) :
       return str (s)

def gcc_options (gcc = "gcc", complete = False, selected_variables = False) :

    cmd = "echo 'int main () { }' | " + gcc + " -v -x c++ -dD -E - 2>&1"

    variables = [ "__GNUC__",
                  "__GNUG__",
                  "__GNUC_MINOR__",
                  "__GNUC_PATCHLEVEL__",
                  "_GNU_SOURCE",
                  "__VERSION__" ]

    result = [ ]
    if complete :
       result.append ("-nostdinc")

    f = subprocess.Popen (cmd, shell=True, stdout=subprocess.PIPE).stdout
    incl = False

    for s in f :
      s = s.strip ()
      s = conv (s)
      if re.match ("End of search list.", s) :
         incl = False
      if incl and s != "" :
         # s = os.path.normpath (s)
         # result.append ("-I " + s)
         result.append ("-I")
         result.append (s)
         # two items    "-I", "directory",
         # one item     "-Idirectory"
         # NOT one item "-I directory"
      # if re.match ("#include \"...\" search starts here:", s) :
      #    incl = True
      if re.match ("#include <...> search starts here:", s) :
         incl = True

      m = re.match ("#define (\\w+) (.*)", s)
      if m :
         name = m.group (1)
         value = m.group (2)

         # if name == "__VERSION__" :
         #    value = value.replace (" ", "_")

         if name in variables or not selected_variables:
            if complete :
               result.append ("-U " + name)
            result.append ("-D " + name + "=" + value)

    f.close ()
    return result

def pkg_options (pkg, libs = False) :
    cmd = "pkg-config " + pkg + " --cflags"
    if libs :
       cmd = cmd + " --libs"
    f = subprocess.Popen (cmd, shell=True, stdout=subprocess.PIPE).stdout
    result = [ ]
    for s in f :
       s = s.strip ()
       s = conv (s)
       for t in s.split () :
          result.append (t)
    return result

if __name__ == "__main__" :
   gcc = "gcc"

   if len (sys.argv) == 2 :
      gcc = sys.argv [1]

   result = gcc_options (gcc, complete = True, selected_variables = True)

   for s in result :
       print (s)

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
