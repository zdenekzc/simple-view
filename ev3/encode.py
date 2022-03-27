
from __future__ import print_function

# import bytecodes
# import bytecodes2

from bytecodes import *
from bytecodes2 import *
from bytecodes3 import *
from bytecodes_par import *
from bytecodes_instr import *

# --------------------------------------------------------------------------

class ObjectHeader (object) :
   def __init__ (self) :
       self.localBytes = 32
       self.code = bytearray ([ ])

   def instr (self, cmd, *argv) :
       cmd_orig = cmd
       print ("cmd" , "(" + str(cmd) + ")", format (cmd, "02x"))
       for param in argv :
           s = ""
           for c in param :
              s = s + format (c, "02x") + " "
           print ("parameter", s)

       info = None
       for item in OpCodes :
           if item.cmd == cmd :
              info = item
       if info == None or info.cmd != cmd :
          print ("error")
       else :
          cnt = 0
          for p in info.params :
             if p in [PAR8, PAR16, PAR32, PARF] :
                cnt = cnt + 1
          if len (argv) == cnt :
              print ("O.K.")
          else :
              print ("bad number of parameters", cnt)

       print ()

       self.code.append (cmd)
       for param in argv :
           self.code += param

# --------------------------------------------------------------------------

class ThreadHeader (ObjectHeader) :
    def __init__ (self) :
        super (ThreadHeader, self).__init__ ()

    def header (self) :
        return VMTHREADHeader (0, self.localBytes)

class BlockHeader (ObjectHeader) :
    def __init__ (self) :
       super (BlockHeader, self).__init__ ()
       self.owner_object_id = 1
       self.trigger_count = 1

    def header (self) :
        return BLOCKHeader (0, self.owner_object_id, self.trigger_count)

class SubcallHeader (ObjectHeader) :
    def __init__ (self) :
       super (SubcallHeader, self).__init__ ()

    def header (self) :
        return SUBCALLHeader (0, self.localBytes)

    def params (self, *arg) :
        self.code.append (len (arg))
        for item in arg :
           self.code.append (item)

# --------------------------------------------------------------------------

class ProgramHeader (object) :
   def __init__ (self) :
       self.version = 0
       self.globalBytes = 32
       self.objects = [ ]

   def addThread (self, threadObject) :
       self.objects.append (threadObject)

   def addBlock (self, blockObject) :
       self.objects.append (blockObject)

   def addSubroutine (self, subrObject) :
       self.objects.append (subrObject)

   def code (self) :

       result = PROGRAMHeader (self.version, len (self.objects), self.globalBytes)

       for obj in self.objects :
          obj.header_pos = len (result) # remember header position
          result = result + obj.header ()

       for obj in self.objects :
           obj.code_pos = len (result)
           result [ obj.header_pos : obj.header_pos+4 ] = LongToBytes (obj.code_pos) # update object offest
           result = result + obj.code

       # update program size
       result [4:8] = LongToBytes (len (result)) # update program size

       # print Program
       n = 0
       for c in result :
          print (format (c, '02x'), end=" ")
          n = n + 1
          if n % 16 == 0 :
             print ()
          elif n % 4 == 0 :
             print ("|", end=" ")
       print ()

       return result

# --------------------------------------------------------------------------

def microProgram () :

    prog = ProgramHeader ()
    prog.globalBytes = 16

    thread = ThreadHeader ()
    thread.localBytes = 0

    prog.addThread (thread)

    if 0  :
       thread.instr (opMOVE32_32, LC(1), GV(0))
       thread.instr (opADD32,     LC(7), GV(0), GV(4))

    if 1 :
       # command to start motor on port A at speed 20
       thread.instr (opOUTPUT_POWER, LC (0), LC (1), LC (20))
       thread.instr (opOUTPUT_START, LC (0), LC (1))
       # thread.instr (opUI_WRITE, LC0(LED), LC0(LED_ORANGE))

       thread.instr (opTIMER_WAIT, LC(1000), GV(12))
       thread.instr (opTIMER_READY, GV(12))

       ## stop motors
       thread.instr (opOUTPUT_STOP, LC(0), LC(15), LC(0))
       # thread.instr (opUI_WRITE, LC0(LED), LC0(LED_RED))

    thread.instr (opOBJECT_END)

    return prog.code ()

# --------------------------------------------------------------------------

def miniProgram () :

    prog = ProgramHeader ()
    prog.globalBytes = 24

    thread = ThreadHeader ()
    thread.localBytes = 20

    prog.addThread (thread)

    thread.instr (opOBJECT_TRIG, LC(2))

    if 1 :
       thread.instr (opADD32,     LC(1), GV(0), GV(0))
       thread.instr (opMOVE32_32, LC(1), GV(4))
       thread.instr (opADD32,     LC(7), GV(4), GV(8))
       thread.instr (opADD32,     LC(8), GV(8), GV(12))
       thread.instr (opCALL,      LC(3), LC(3), LC(512), GV(12), GV(12))
       thread.instr (opMOVE32_32, LC(0x777), GV(4))

       # command to start motor on port A at speed 20
       thread.instr (opOUTPUT_POWER, LC (0), LC (1), LC (20))
       thread.instr (opOUTPUT_START, LC (0), LC (1))

       thread.instr (opTIMER_WAIT, LC(1000), GV(16))
       thread.instr (opTIMER_READY, GV(16))

       ## stop motors
       thread.instr (opOUTPUT_STOP, LC(0), LC(15), LC(0))

       thread.instr (opTIMER_WAIT, LC(1000), GV(16))
       thread.instr (opTIMER_READY, GV(16))

       thread.instr (opJR, LC4(-6-len(thread.code)))

    # thread.instr (opSLEEP)
    # thread.instr (opBP0)
    thread.instr (opOBJECT_END)

    if 1 :
       block = BlockHeader ()
       prog.addBlock (block)

       block.instr (opUI_WRITE, LC0(LED), LC0(LED_ORANGE))

       block.instr (opTIMER_WAIT, LC(500), GV(20))
       block.instr (opTIMER_READY, GV(20))

       block.instr (opUI_WRITE, LC0(LED), LC0(LED_RED))

       block.instr (opTIMER_WAIT, LC(500), GV(20))
       block.instr (opTIMER_READY, GV(20))

       block.instr (opJR, LC4(-6-len(block.code)))
       block.instr (opOBJECT_END)

    if 1 :
       subr = SubcallHeader ()
       subr.params (IN_32, IN_32, OUT_32)
       prog.addSubroutine (subr)

       subr.instr (opADD32, LV(0), LV(4), LV(8))
       # subr.instr (opUI_WRITE, LC0(LED), LC0(LED_ORANGE))

       subr.instr (opRETURN)
       subr.instr (opOBJECT_END)

    return prog.code ()

# --------------------------------------------------------------------------

if __name__ == '__main__':
   miniProgram ()

# --------------------------------------------------------------------------

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
