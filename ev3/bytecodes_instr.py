
from bytecodes import *
from bytecodes2 import *
from bytecodes_par import *

# https://github.com/mindboards/ev3sources/blob/master/lms2012/lms2012/source/bytecodes.c

# --------------------------------------------------------------------------

SUBP          = 0x01                # Next nibble is sub parameter table no
PARNO         = 0x02                # Defines no of following parameters
PARLAB        = 0x03                # Defines label no
PARVALUES     = 0x04                # Last parameter defines number of values to follow

# --------------------------------------------------------------------------

PAR           =     0x08              # Plain  parameter as below:
PAR8          =     (PAR + DATA_8)    # DATA8  parameter
PAR16         =     (PAR + DATA_16)   # DATA16 parameter
PAR32         =     (PAR + DATA_32)   # DATA32 parameter
PARF          =     (PAR + DATA_F)    # DATAF  parameter
PARS          =     (PAR + DATA_S)    # DATAS  parameter
PARV          =     (PAR + DATA_V)    # Parameter type variable

# --------------------------------------------------------------------------

ParTypeNames = {
   DATA_8  : "DATA8",
   DATA_16 : "DATA16",
   DATA_32 : "DATA32",
   DATA_F  : "DATAF",
   DATA_S  : "STRING",
   DATA_V  : "UNKNOWN",
}

# --------------------------------------------------------------------------

ParMin = { DATA_8: DATA8_MIN, DATA_16: DATA16_MIN, DATA_32: DATA32_MIN }
ParMax = { DATA_8: DATA8_MAX, DATA_16: DATA16_MAX, DATA_32: DATA32_MAX }

# --------------------------------------------------------------------------

UI_READ_SUBP    = 0
UI_WRITE_SUBP   = 1
UI_DRAW_SUBP    = 2
UI_BUTTON_SUBP  = 3
FILE_SUBP       = 4
PROGRAM_SUBP    = 5
VM_SUBP         = 6
STRING_SUBP     = 7
COM_READ_SUBP   = 8
COM_WRITE_SUBP  = 9
SOUND_SUBP      = 10
INPUT_SUBP      = 11
ARRAY_SUBP      = 12
MATH_SUBP       = 13
COM_GET_SUBP    = 14
COM_SET_SUBP    = 15
FILENAME_SUBP   = 16

FILENAME_SUBP = ARRAY_SUBP
TST_SUBP      = VM_SUBP

# --------------------------------------------------------------------------

class OC (object) :
    def __init__ (self, cmd, cmd_txt, * params) :
       self.cmd = cmd
       self.cmd_txt = cmd_txt
       self.params = params

class SC (object) :
    def __init__ (self, cmd_key, sub_code, sub_code_txt, * params) :
       self.cmd_key = cmd_key
       self.sub_code = sub_code
       self.sub_code_txt = sub_code_txt
       self.sub_params = params

# --------------------------------------------------------------------------

#  OpCode and Parameters
OpCodes = [
  #     OpCode                                           Parameters                                      Unused
  #     VM
  OC(   opERROR,                "ERROR",               0,                                              0,0,0,0,0,0,0         ),
  OC(   opNOP,                  "NOP",                 0,                                              0,0,0,0,0,0,0         ),
  OC(   opPROGRAM_STOP,         "PROGRAM_STOP",        PAR16,                                          0,0,0,0,0,0,0         ),
  OC(   opPROGRAM_START,        "PROGRAM_START",       PAR16,PAR32,PAR32,PAR8,                         0,0,0,0               ),
  OC(   opOBJECT_STOP,          "OBJECT_STOP",         PAR16,                                          0,0,0,0,0,0,0         ),
  OC(   opOBJECT_START,         "OBJECT_START",        PAR16,                                          0,0,0,0,0,0,0         ),
  OC(   opOBJECT_TRIG,          "OBJECT_TRIG",         PAR16,                                          0,0,0,0,0,0,0         ),
  OC(   opOBJECT_WAIT,          "OBJECT_WAIT",         PAR16,                                          0,0,0,0,0,0,0         ),
  OC(   opRETURN,               "RETURN",              0,                                              0,0,0,0,0,0,0         ),
  OC(   opCALL,                 "CALL",                PAR16,PARNO,                                    0,0,0,0,0,0           ),
  OC(   opOBJECT_END,           "OBJECT_END",          0,                                              0,0,0,0,0,0,0         ),
  OC(   opSLEEP,                "SLEEP",               0,                                              0,0,0,0,0,0,0         ),
  OC(   opPROGRAM_INFO,         "PROGRAM_INFO",        PAR8, SUBP, PROGRAM_SUBP,                       0,0,0,0,0             ),
  OC(   opLABEL,                "LABEL",               PARLAB,                                         0,0,0,0,0,0,0         ),
  OC(   opPROBE,                "PROBE",               PAR16,PAR16,PAR32,PAR32,                        0,0,0,0               ),
  OC(   opDO,                   "DO",                  PAR16,PAR32,PAR32,                              0,0,0,0,0             ),
  #     Math
  OC(   opADD8,                 "ADD8",                PAR8,PAR8,PAR8,                                 0,0,0,0,0             ),
  OC(   opADD16,                "ADD16",               PAR16,PAR16,PAR16,                              0,0,0,0,0             ),
  OC(   opADD32,                "ADD32",               PAR32,PAR32,PAR32,                              0,0,0,0,0             ),
  OC(   opADDF,                 "ADDF",                PARF,PARF,PARF,                                 0,0,0,0,0             ),
  OC(   opSUB8,                 "SUB8",                PAR8,PAR8,PAR8,                                 0,0,0,0,0             ),
  OC(   opSUB16,                "SUB16",               PAR16,PAR16,PAR16,                              0,0,0,0,0             ),
  OC(   opSUB32,                "SUB32",               PAR32,PAR32,PAR32,                              0,0,0,0,0             ),
  OC(   opSUBF,                 "SUBF",                PARF,PARF,PARF,                                 0,0,0,0,0             ),
  OC(   opMUL8,                 "MUL8",                PAR8,PAR8,PAR8,                                 0,0,0,0,0             ),
  OC(   opMUL16,                "MUL16",               PAR16,PAR16,PAR16,                              0,0,0,0,0             ),
  OC(   opMUL32,                "MUL32",               PAR32,PAR32,PAR32,                              0,0,0,0,0             ),
  OC(   opMULF,                 "MULF",                PARF,PARF,PARF,                                 0,0,0,0,0             ),
  OC(   opDIV8,                 "DIV8",                PAR8,PAR8,PAR8,                                 0,0,0,0,0             ),
  OC(   opDIV16,                "DIV16",               PAR16,PAR16,PAR16,                              0,0,0,0,0             ),
  OC(   opDIV32,                "DIV32",               PAR32,PAR32,PAR32,                              0,0,0,0,0             ),
  OC(   opDIVF,                 "DIVF",                PARF,PARF,PARF,                                 0,0,0,0,0             ),
  #     Logic
  OC(   opOR8,                  "OR8",                 PAR8,PAR8,PAR8,                                 0,0,0,0,0             ),
  OC(   opOR16,                 "OR16",                PAR16,PAR16,PAR16,                              0,0,0,0,0             ),
  OC(   opOR32,                 "OR32",                PAR32,PAR32,PAR32,                              0,0,0,0,0             ),
  OC(   opAND8,                 "AND8",                PAR8,PAR8,PAR8,                                 0,0,0,0,0             ),
  OC(   opAND16,                "AND16",               PAR16,PAR16,PAR16,                              0,0,0,0,0             ),
  OC(   opAND32,                "AND32",               PAR32,PAR32,PAR32,                              0,0,0,0,0             ),
  OC(   opXOR8,                 "XOR8",                PAR8,PAR8,PAR8,                                 0,0,0,0,0             ),
  OC(   opXOR16,                "XOR16",               PAR16,PAR16,PAR16,                              0,0,0,0,0             ),
  OC(   opXOR32,                "XOR32",               PAR32,PAR32,PAR32,                              0,0,0,0,0             ),
  OC(   opRL8,                  "RL8",                 PAR8,PAR8,PAR8,                                 0,0,0,0,0             ),
  OC(   opRL16,                 "RL16",                PAR16,PAR16,PAR16,                              0,0,0,0,0             ),
  OC(   opRL32,                 "RL32",                PAR32,PAR32,PAR32,                              0,0,0,0,0             ),
  #     Move
  OC(   opINIT_BYTES,           "INIT_BYTES",          PAR8,PAR32,PARVALUES,PAR8,                      0,0,0,0               ),
  OC(   opMOVE8_8,              "MOVE8_8",             PAR8,PAR8,                                      0,0,0,0,0,0           ),
  OC(   opMOVE8_16,             "MOVE8_16",            PAR8,PAR16,                                     0,0,0,0,0,0           ),
  OC(   opMOVE8_32,             "MOVE8_32",            PAR8,PAR32,                                     0,0,0,0,0,0           ),
  OC(   opMOVE8_F,              "MOVE8_F",             PAR8,PARF,                                      0,0,0,0,0,0           ),
  OC(   opMOVE16_8,             "MOVE16_8",            PAR16,PAR8,                                     0,0,0,0,0,0           ),
  OC(   opMOVE16_16,            "MOVE16_16",           PAR16,PAR16,                                    0,0,0,0,0,0           ),
  OC(   opMOVE16_32,            "MOVE16_32",           PAR16,PAR32,                                    0,0,0,0,0,0           ),
  OC(   opMOVE16_F,             "MOVE16_F",            PAR16,PARF,                                     0,0,0,0,0,0           ),
  OC(   opMOVE32_8,             "MOVE32_8",            PAR32,PAR8,                                     0,0,0,0,0,0           ),
  OC(   opMOVE32_16,            "MOVE32_16",           PAR32,PAR16,                                    0,0,0,0,0,0           ),
  OC(   opMOVE32_32,            "MOVE32_32",           PAR32,PAR32,                                    0,0,0,0,0,0           ),
  OC(   opMOVE32_F,             "MOVE32_F",            PAR32,PARF,                                     0,0,0,0,0,0           ),
  OC(   opMOVEF_8,              "MOVEF_8",             PARF,PAR8,                                      0,0,0,0,0,0           ),
  OC(   opMOVEF_16,             "MOVEF_16",            PARF,PAR16,                                     0,0,0,0,0,0           ),
  OC(   opMOVEF_32,             "MOVEF_32",            PARF,PAR32,                                     0,0,0,0,0,0           ),
  OC(   opMOVEF_F,              "MOVEF_F",             PARF,PARF,                                      0,0,0,0,0,0           ),
  #     Branch
  OC(   opJR,                   "JR",                  PAR32,                                          0,0,0,0,0,0,0         ),
  OC(   opJR_FALSE,             "JR_FALSE",            PAR8,PAR32,                                     0,0,0,0,0,0           ),
  OC(   opJR_TRUE,              "JR_TRUE",             PAR8,PAR32,                                     0,0,0,0,0,0           ),
  OC(   opJR_NAN,               "JR_NAN",              PARF,PAR32,                                     0,0,0,0,0,0           ),
  #     Compare
  OC(   opCP_LT8,               "CP_LT8",              PAR8,PAR8,PAR8,                                 0,0,0,0,0             ),
  OC(   opCP_LT16,              "CP_LT16",             PAR16,PAR16,PAR8,                               0,0,0,0,0             ),
  OC(   opCP_LT32,              "CP_LT32",             PAR32,PAR32,PAR8,                               0,0,0,0,0             ),
  OC(   opCP_LTF,               "CP_LTF",              PARF,PARF,PAR8,                                 0,0,0,0,0             ),
  OC(   opCP_GT8,               "CP_GT8",              PAR8,PAR8,PAR8,                                 0,0,0,0,0             ),
  OC(   opCP_GT16,              "CP_GT16",             PAR16,PAR16,PAR8,                               0,0,0,0,0             ),
  OC(   opCP_GT32,              "CP_GT32",             PAR32,PAR32,PAR8,                               0,0,0,0,0             ),
  OC(   opCP_GTF,               "CP_GTF",              PARF,PARF,PAR8,                                 0,0,0,0,0             ),
  OC(   opCP_EQ8,               "CP_EQ8",              PAR8,PAR8,PAR8,                                 0,0,0,0,0             ),
  OC(   opCP_EQ16,              "CP_EQ16",             PAR16,PAR16,PAR8,                               0,0,0,0,0             ),
  OC(   opCP_EQ32,              "CP_EQ32",             PAR32,PAR32,PAR8,                               0,0,0,0,0             ),
  OC(   opCP_EQF,               "CP_EQF",              PARF,PARF,PAR8,                                 0,0,0,0,0             ),
  OC(   opCP_NEQ8,              "CP_NEQ8",             PAR8,PAR8,PAR8,                                 0,0,0,0,0             ),
  OC(   opCP_NEQ16,             "CP_NEQ16",            PAR16,PAR16,PAR8,                               0,0,0,0,0             ),
  OC(   opCP_NEQ32,             "CP_NEQ32",            PAR32,PAR32,PAR8,                               0,0,0,0,0             ),
  OC(   opCP_NEQF,              "CP_NEQF",             PARF,PARF,PAR8,                                 0,0,0,0,0             ),
  OC(   opCP_LTEQ8,             "CP_LTEQ8",            PAR8,PAR8,PAR8,                                 0,0,0,0,0             ),
  OC(   opCP_LTEQ16,            "CP_LTEQ16",           PAR16,PAR16,PAR8,                               0,0,0,0,0             ),
  OC(   opCP_LTEQ32,            "CP_LTEQ32",           PAR32,PAR32,PAR8,                               0,0,0,0,0             ),
  OC(   opCP_LTEQF,             "CP_LTEQF",            PARF,PARF,PAR8,                                 0,0,0,0,0             ),
  OC(   opCP_GTEQ8,             "CP_GTEQ8",            PAR8,PAR8,PAR8,                                 0,0,0,0,0             ),
  OC(   opCP_GTEQ16,            "CP_GTEQ16",           PAR16,PAR16,PAR8,                               0,0,0,0,0             ),
  OC(   opCP_GTEQ32,            "CP_GTEQ32",           PAR32,PAR32,PAR8,                               0,0,0,0,0             ),
  OC(   opCP_GTEQF,             "CP_GTEQF",            PARF,PARF,PAR8,                                 0,0,0,0,0             ),
  #     Select
  OC(   opSELECT8,              "SELECT8",             PAR8,PAR8,PAR8,PAR8,                            0,0,0,0               ),
  OC(   opSELECT16,             "SELECT16",            PAR8,PAR16,PAR16,PAR16,                         0,0,0,0               ),
  OC(   opSELECT32,             "SELECT32",            PAR8,PAR32,PAR32,PAR32,                         0,0,0,0               ),
  OC(   opSELECTF,              "SELECTF",             PAR8,PARF,PARF,PARF,                            0,0,0,0               ),

  OC(   opSYSTEM,               "SYSTEM",              PAR8,PAR32,                                     0,0,0,0,0,0           ),
  OC(   opPORT_CNV_OUTPUT,      "PORT_CNV_OUTPUT",     PAR32,PAR8,PAR8,PAR8,                           0,0,0,0               ),
  OC(   opPORT_CNV_INPUT,       "PORT_CNV_INPUT",      PAR32,PAR8,PAR8,                                0,0,0,0,0             ),
  OC(   opNOTE_TO_FREQ,         "NOTE_TO_FREQ",        PAR8,PAR16,                                     0,0,0,0,0,0           ),

  #     Branch
  OC(   opJR_LT8,               "JR_LT8",              PAR8,PAR8,PAR32,                                0,0,0,0,0             ),
  OC(   opJR_LT16,              "JR_LT16",             PAR16,PAR16,PAR32,                              0,0,0,0,0             ),
  OC(   opJR_LT32,              "JR_LT32",             PAR32,PAR32,PAR32,                              0,0,0,0,0             ),
  OC(   opJR_LTF,               "JR_LTF",              PARF,PARF,PAR32,                                0,0,0,0,0             ),
  OC(   opJR_GT8,               "JR_GT8",              PAR8,PAR8,PAR32,                                0,0,0,0,0             ),
  OC(   opJR_GT16,              "JR_GT16",             PAR16,PAR16,PAR32,                              0,0,0,0,0             ),
  OC(   opJR_GT32,              "JR_GT32",             PAR32,PAR32,PAR32,                              0,0,0,0,0             ),
  OC(   opJR_GTF,               "JR_GTF",              PARF,PARF,PAR32,                                0,0,0,0,0             ),
  OC(   opJR_EQ8,               "JR_EQ8",              PAR8,PAR8,PAR32,                                0,0,0,0,0             ),
  OC(   opJR_EQ16,              "JR_EQ16",             PAR16,PAR16,PAR32,                              0,0,0,0,0             ),
  OC(   opJR_EQ32,              "JR_EQ32",             PAR32,PAR32,PAR32,                              0,0,0,0,0             ),
  OC(   opJR_EQF,               "JR_EQF",              PARF,PARF,PAR32,                                0,0,0,0,0             ),
  OC(   opJR_NEQ8,              "JR_NEQ8",             PAR8,PAR8,PAR32,                                0,0,0,0,0             ),
  OC(   opJR_NEQ16,             "JR_NEQ16",            PAR16,PAR16,PAR32,                              0,0,0,0,0             ),
  OC(   opJR_NEQ32,             "JR_NEQ32",            PAR32,PAR32,PAR32,                              0,0,0,0,0             ),
  OC(   opJR_NEQF,              "JR_NEQF",             PARF,PARF,PAR32,                                0,0,0,0,0             ),
  OC(   opJR_LTEQ8,             "JR_LTEQ8",            PAR8,PAR8,PAR32,                                0,0,0,0,0             ),
  OC(   opJR_LTEQ16,            "JR_LTEQ16",           PAR16,PAR16,PAR32,                              0,0,0,0,0             ),
  OC(   opJR_LTEQ32,            "JR_LTEQ32",           PAR32,PAR32,PAR32,                              0,0,0,0,0             ),
  OC(   opJR_LTEQF,             "JR_LTEQF",            PARF,PARF,PAR32,                                0,0,0,0,0             ),
  OC(   opJR_GTEQ8,             "JR_GTEQ8",            PAR8,PAR8,PAR32,                                0,0,0,0,0             ),
  OC(   opJR_GTEQ16,            "JR_GTEQ16",           PAR16,PAR16,PAR32,                              0,0,0,0,0             ),
  OC(   opJR_GTEQ32,            "JR_GTEQ32",           PAR32,PAR32,PAR32,                              0,0,0,0,0             ),
  OC(   opJR_GTEQF,             "JR_GTEQF",            PARF,PARF,PAR32,                                0,0,0,0,0             ),
  #     VM
  OC(   opINFO,                 "INFO",                PAR8,SUBP,VM_SUBP,                              0,0,0,0,0             ),
  OC(   opSTRINGS,              "STRINGS",             PAR8,SUBP,STRING_SUBP,                          0,0,0,0,0             ),
  OC(   opMEMORY_WRITE,         "MEMORY_WRITE",        PAR16,PAR16,PAR32,PAR32,PAR8,                   0,0,0                 ),
  OC(   opMEMORY_READ,          "MEMORY_READ",         PAR16,PAR16,PAR32,PAR32,PAR8,                   0,0,0                 ),
  #     UI
  OC(   opUI_FLUSH,             "UI_FLUSH",            0,                                              0,0,0,0,0,0,0         ),
  OC(   opUI_READ,              "UI_READ",             PAR8,SUBP,UI_READ_SUBP,                         0,0,0,0,0             ),
  OC(   opUI_WRITE,             "UI_WRITE",            PAR8,SUBP,UI_WRITE_SUBP,                        0,0,0,0,0             ),
  OC(   opUI_BUTTON,            "UI_BUTTON",           PAR8,SUBP,UI_BUTTON_SUBP,                       0,0,0,0,0             ),
  OC(   opUI_DRAW,              "UI_DRAW",             PAR8,SUBP,UI_DRAW_SUBP,                         0,0,0,0,0             ),
  #     Timer
  OC(   opTIMER_WAIT,           "TIMER_WAIT",          PAR32,PAR32,                                    0,0,0,0,0,0           ),
  OC(   opTIMER_READY,          "TIMER_READY",         PAR32,                                          0,0,0,0,0,0,0         ),
  OC(   opTIMER_READ,           "TIMER_READ",          PAR32,                                          0,0,0,0,0,0,0         ),
  #     VM
  OC(   opBP0,                  "BP0",                 0,                                              0,0,0,0,0,0,0         ),
  OC(   opBP1,                  "BP1",                 0,                                              0,0,0,0,0,0,0         ),
  OC(   opBP2,                  "BP2",                 0,                                              0,0,0,0,0,0,0         ),
  OC(   opBP3,                  "BP3",                 0,                                              0,0,0,0,0,0,0         ),
  OC(   opBP_SET,               "BP_SET",              PAR16,PAR8,PAR32,                               0,0,0,0,0             ),
  OC(   opMATH,                 "MATH",                PAR8,SUBP,MATH_SUBP,                            0,0,0,0,0             ),
  OC(   opRANDOM,               "RANDOM",              PAR16,PAR16,PAR16,                              0,0,0,0,0             ),
  OC(   opTIMER_READ_US,        "TIMER_READ_US",       PAR32,                                          0,0,0,0,0,0,0         ),
  OC(   opKEEP_ALIVE,           "KEEP_ALIVE",          PAR8,                                           0,0,0,0,0,0,0         ),
  #     Com
  OC(   opCOM_READ,             "COM_READ",            PAR8,SUBP,COM_READ_SUBP,                        0,0,0,0,0             ),
  OC(   opCOM_WRITE,            "COM_WRITE",           PAR8,SUBP,COM_WRITE_SUBP,                       0,0,0,0,0             ),
  #     Sound
  OC(   opSOUND,                "SOUND",               PAR8,SUBP,SOUND_SUBP,                           0,0,0,0,0             ),
  OC(   opSOUND_TEST,           "SOUND_TEST",          PAR8,                                           0,0,0,0,0,0,0         ),
  OC(   opSOUND_READY,          "SOUND_READY",         0,                                              0,0,0,0,0,0,0         ),
  #     Input
  OC(   opINPUT_SAMPLE,         "INPUT_SAMPLE",        PAR32,PAR16,PAR16,PAR8,PAR8,PAR8,PAR8,PARF                            ),
  OC(   opINPUT_DEVICE_LIST,    "INPUT_DEVICE_LIST",   PAR8,PAR8,PAR8,                                 0,0,0,0,0             ),
  OC(   opINPUT_DEVICE,         "INPUT_DEVICE",        PAR8,SUBP,INPUT_SUBP,                           0,0,0,0,0             ),
  OC(   opINPUT_READ,           "INPUT_READ",          PAR8,PAR8,PAR8,PAR8,PAR8,                       0,0,0                 ),
  OC(   opINPUT_READSI,         "INPUT_READSI",        PAR8,PAR8,PAR8,PAR8,PARF,                       0,0,0                 ),
  OC(   opINPUT_TEST,           "INPUT_TEST",          PAR8,                                           0,0,0,0,0,0,0         ),
  OC(   opINPUT_TEST,           "INPUT_TEST",          PAR8,PAR8,PAR8,                                 0,0,0,0,0             ),
  OC(   opINPUT_READY,          "INPUT_READY",         PAR8,PAR8,                                      0,0,0,0,0,0           ),
  OC(   opINPUT_READEXT,        "INPUT_READEXT",       PAR8,PAR8,PAR8,PAR8,PAR8,PARNO,                 0,0                   ),
  OC(   opINPUT_WRITE,          "INPUT_WRITE",         PAR8,PAR8,PAR8,PAR8,                            0,0,0,0               ),
  #     Output
  OC(   opOUTPUT_SET_TYPE,      "OUTPUT_SET_TYPE",     PAR8,PAR8,PAR8,                                 0,0,0,0,0             ),
  OC(   opOUTPUT_RESET,         "OUTPUT_RESET",        PAR8,PAR8,                                      0,0,0,0,0,0           ),
  OC(   opOUTPUT_STOP,          "OUTPUT_STOP",         PAR8,PAR8,PAR8,                                 0,0,0,0,0             ),
  OC(   opOUTPUT_SPEED,         "OUTPUT_SPEED",        PAR8,PAR8,PAR8,                                 0,0,0,0,0             ),
  OC(   opOUTPUT_POWER,         "OUTPUT_POWER",        PAR8,PAR8,PAR8,                                 0,0,0,0,0             ),
  OC(   opOUTPUT_START,         "OUTPUT_START",        PAR8,PAR8,                                      0,0,0,0,0,0           ),
  OC(   opOUTPUT_POLARITY,      "OUTPUT_POLARITY",     PAR8,PAR8,PAR8,                                 0,0,0,0,0             ),
  OC(   opOUTPUT_READ,          "OUTPUT_READ",         PAR8,PAR8,PAR8,PAR32,                           0,0,0,0               ),
  OC(   opOUTPUT_READY,         "OUTPUT_READY",        PAR8,PAR8,                                      0,0,0,0,0,0           ),
  OC(   opOUTPUT_TEST,          "OUTPUT_TEST",         PAR8,PAR8,PAR8,                                 0,0,0,0,0             ),
  OC(   opOUTPUT_STEP_POWER,    "OUTPUT_STEP_POWER",   PAR8,PAR8,PAR8,PAR32,PAR32,PAR32,PAR8,          0                     ),
  OC(   opOUTPUT_TIME_POWER,    "OUTPUT_TIME_POWER",   PAR8,PAR8,PAR8,PAR32,PAR32,PAR32,PAR8,          0                     ),
  OC(   opOUTPUT_STEP_SPEED,    "OUTPUT_STEP_SPEED",   PAR8,PAR8,PAR8,PAR32,PAR32,PAR32,PAR8,          0                     ),
  OC(   opOUTPUT_TIME_SPEED,    "OUTPUT_TIME_SPEED",   PAR8,PAR8,PAR8,PAR32,PAR32,PAR32,PAR8,          0                     ),
  OC(   opOUTPUT_STEP_SYNC,     "OUTPUT_STEP_SYNC",    PAR8,PAR8,PAR8,PAR16,PAR32,PAR8,                0,0                   ),
  OC(   opOUTPUT_TIME_SYNC,     "OUTPUT_TIME_SYNC",    PAR8,PAR8,PAR8,PAR16,PAR32,PAR8,                0,0                   ),
  OC(   opOUTPUT_CLR_COUNT,     "OUTPUT_CLR_COUNT",    PAR8,PAR8,                                      0,0,0,0,0,0           ),
  OC(   opOUTPUT_GET_COUNT,     "OUTPUT_GET_COUNT",    PAR8,PAR8,PAR32,                                0,0,0,0,0             ),
  OC(   opOUTPUT_PRG_STOP,      "OUTPUT_PRG_STOP",     0,                                              0,0,0,0,0,0,0         ),
  #     Memory
  OC(   opFILE,                 "FILE",                PAR8,SUBP,FILE_SUBP,                            0,0,0,0,0             ),
  OC(   opARRAY,                "ARRAY",               PAR8,SUBP,ARRAY_SUBP,                           0,0,0,0,0             ),
  OC(   opARRAY_WRITE,          "ARRAY_WRITE",         PAR16,PAR32,PARV,                               0,0,0,0,0             ),
  OC(   opARRAY_READ,           "ARRAY_READ",          PAR16,PAR32,PARV,                               0,0,0,0,0             ),
  OC(   opARRAY_APPEND,         "ARRAY_APPEND",        PAR16,PARV,                                     0,0,0,0,0,0           ),
  OC(   opMEMORY_USAGE,         "MEMORY_USAGE",        PAR32,PAR32,                                    0,0,0,0,0,0           ),
  OC(   opFILENAME,             "FILENAME",            PAR8,SUBP,FILENAME_SUBP,                        0,0,0,0,0             ),
  #     Move
  OC(   opREAD8,                "READ8",               PAR8,PAR8,PAR8,                                 0,0,0,0,0             ),
  OC(   opREAD16,               "READ16",              PAR16,PAR8,PAR16,                               0,0,0,0,0             ),
  OC(   opREAD32,               "READ32",              PAR32,PAR8,PAR32,                               0,0,0,0,0             ),
  OC(   opREADF,                "READF",               PARF,PAR8,PARF,                                 0,0,0,0,0             ),
  OC(   opWRITE8,               "WRITE8",              PAR8,PAR8,PAR8,                                 0,0,0,0,0             ),
  OC(   opWRITE16,              "WRITE16",             PAR16,PAR8,PAR16,                               0,0,0,0,0             ),
  OC(   opWRITE32,              "WRITE32",             PAR32,PAR8,PAR32,                               0,0,0,0,0             ),
  OC(   opWRITEF,               "WRITEF",              PARF,PAR8,PARF,                                 0,0,0,0,0             ),
  #     Com
  OC(   opCOM_READY,            "COM_READY",           PAR8,PAR8,                                      0,0,0,0,0,0           ),
  OC(   opCOM_READDATA,         "COM_READDATA",        PAR8,PAR8,PAR16,PAR8,                           0,0,0,0               ),
  OC(   opCOM_WRITEDATA,        "COM_WRITEDATA",       PAR8,PAR8,PAR16,PAR8,                           0,0,0,0               ),
  OC(   opCOM_GET,              "COM_GET",             PAR8,SUBP,COM_GET_SUBP,                         0,0,0,0,0             ),
  OC(   opCOM_SET,              "COM_SET",             PAR8,SUBP,COM_SET_SUBP,                         0,0,0,0,0             ),
  OC(   opCOM_TEST,             "COM_TEST",            PAR8,PAR8,PAR8,                                 0,0,0,0,0             ),
  OC(   opCOM_REMOVE,           "COM_REMOVE",          PAR8,PAR8,                                      0,0,0,0,0,0           ),
  OC(   opCOM_WRITEFILE,        "COM_WRITEFILE",       PAR8,PAR8,PAR8,PAR8,                            0,0,0,0               ),

  OC(   opMAILBOX_OPEN,         "MAILBOX_OPEN",        PAR8,PAR8,PAR8,PAR8,PAR8,                       0,0,0                 ),
  OC(   opMAILBOX_WRITE,        "MAILBOX_WRITE",       PAR8,PAR8,PAR8,PAR8,PARNO,                      0,0,0                 ),
  OC(   opMAILBOX_READ,         "MAILBOX_READ",        PAR8,PAR8,PARNO,                                0,0,0,0,0             ),
  OC(   opMAILBOX_TEST,         "MAILBOX_TEST",        PAR8,PAR8,                                      0,0,0,0,0,0           ),
  OC(   opMAILBOX_READY,        "MAILBOX_READY",       PAR8,                                           0,0,0,0,0,0,0         ),
  OC(   opMAILBOX_CLOSE,        "MAILBOX_CLOSE",       PAR8,                                           0,0,0,0,0,0,0         ),
  #     Test
  OC(   opTST,                  "TST",                 PAR8,SUBP,TST_SUBP,                             0,0,0,0,0             ),
]

# ------------s--------------------------------------------------------------

SubCodes = [
  #     ParameterFormat         SubCode                                          Parameters                                      Unused

  #     VM
  SC(   PROGRAM_SUBP,           OBJ_STOP,               "OBJ_STOP",              PAR16,PAR16,                                    0,0,0,0,0,0           ),
  SC(   PROGRAM_SUBP,           OBJ_START,              "OBJ_START",             PAR16,PAR16,                                    0,0,0,0,0,0           ),
  SC(   PROGRAM_SUBP,           GET_STATUS,             "GET_STATUS",            PAR16,PAR8,                                     0,0,0,0,0,0           ),
  SC(   PROGRAM_SUBP,           GET_SPEED,              "GET_SPEED",             PAR16,PAR32,                                    0,0,0,0,0,0           ),
  SC(   PROGRAM_SUBP,           GET_PRGRESULT,          "GET_PRGRESULT",         PAR16,PAR8,                                     0,0,0,0,0,0           ),
  SC(   PROGRAM_SUBP,           SET_INSTR,              "SET_INSTR",             PAR16,                                          0,0,0,0,0,0,0         ),
  #     Memory
  SC(   FILE_SUBP,              OPEN_APPEND,            "OPEN_APPEND",           PAR8,PAR16,                                     0,0,0,0,0,0           ),
  SC(   FILE_SUBP,              OPEN_READ,              "OPEN_READ",             PAR8,PAR16,PAR32,                               0,0,0,0,0             ),
  SC(   FILE_SUBP,              OPEN_WRITE,             "OPEN_WRITE",            PAR8,PAR16,                                     0,0,0,0,0,0           ),
  SC(   FILE_SUBP,              READ_VALUE,             "READ_VALUE",            PAR16,PAR8,PARF,                                0,0,0,0,0             ),
  SC(   FILE_SUBP,              WRITE_VALUE,            "WRITE_VALUE",           PAR16,PAR8,PARF,PAR8,PAR8,                      0,0,0                 ),
  SC(   FILE_SUBP,              READ_TEXT,              "READ_TEXT",             PAR16,PAR8,PAR16,PAR8,                          0,0,0,0               ),
  SC(   FILE_SUBP,              WRITE_TEXT,             "WRITE_TEXT",            PAR16,PAR8,PAR8,                                0,0,0,0,0             ),
  SC(   FILE_SUBP,              CLOSE,                  "CLOSE",                 PAR16,                                          0,0,0,0,0,0,0         ),
  SC(   FILE_SUBP,              LOAD_IMAGE,             "LOAD_IMAGE",            PAR16,PAR8,PAR32,PAR32,                         0,0,0,0               ),
  SC(   FILE_SUBP,              GET_HANDLE,             "GET_HANDLE",            PAR8,PAR16,PAR8,                                0,0,0,0,0             ),
  SC(   FILE_SUBP,              MAKE_FOLDER,            "MAKE_FOLDER",           PAR8,PAR8,                                      0,0,0,0,0,0           ),
  SC(   FILE_SUBP,              GET_LOG_NAME,           "GET_LOG_NAME",          PAR8,PAR8,                                      0,0,0,0,0,0           ),
  SC(   FILE_SUBP,              GET_POOL,               "GET_POOL",              PAR32,PAR16,PAR32,                              0,0,0,0,0             ),
  SC(   FILE_SUBP,              GET_FOLDERS,            "GET_FOLDERS",           PAR8,PAR8,                                      0,0,0,0,0,0           ),
  SC(   FILE_SUBP,              GET_SUBFOLDER_NAME,     "GET_SUBFOLDER_NAME",    PAR8,PAR8,PAR8,PAR8,                            0,0,0,0               ),
  SC(   FILE_SUBP,              WRITE_LOG,              "WRITE_LOG",             PAR16,PAR32,PAR8,PARF,                          0,0,0,0               ),
  SC(   FILE_SUBP,              CLOSE_LOG,              "CLOSE_LOG",             PAR16,PAR8,                                     0,0,0,0,0,0           ),
  SC(   FILE_SUBP,              SET_LOG_SYNC_TIME,      "SET_LOG_SYNC_TIME",     PAR32,PAR32,                                    0,0,0,0,0,0           ),
  SC(   FILE_SUBP,              DEL_SUBFOLDER,          "DEL_SUBFOLDER",         PAR8,PAR8,                                      0,0,0,0,0,0           ),
  SC(   FILE_SUBP,              GET_LOG_SYNC_TIME,      "GET_LOG_SYNC_TIME",     PAR32,PAR32,                                    0,0,0,0,0,0           ),
  SC(   FILE_SUBP,              GET_IMAGE,              "GET_IMAGE",             PAR8,PAR16,PAR8,PAR32,                          0,0,0,0               ),
  SC(   FILE_SUBP,              GET_ITEM,               "GET_ITEM",              PAR8,PAR8,PAR8,                                 0,0,0,0,0             ),
  SC(   FILE_SUBP,              GET_CACHE_FILES,        "GET_CACHE_FILES",       PAR8,                                           0,0,0,0,0,0,0         ),
  SC(   FILE_SUBP,              GET_CACHE_FILE,         "GET_CACHE_FILE",        PAR8,PAR8,PAR8,                                 0,0,0,0,0             ),
  SC(   FILE_SUBP,              PUT_CACHE_FILE,         "PUT_CACHE_FILE",        PAR8,                                           0,0,0,0,0,0,0         ),
  SC(   FILE_SUBP,              DEL_CACHE_FILE,         "DEL_CACHE_FILE",        PAR8,                                           0,0,0,0,0,0,0         ),
  SC(   FILE_SUBP,              OPEN_LOG,               "OPEN_LOG",              PAR8,PAR32,PAR32,PAR32,PAR32,PAR32,PAR8,PAR16                         ),
  SC(   FILE_SUBP,              READ_BYTES,             "READ_BYTES",            PAR16,PAR16,PAR8,                               0,0,0,0,0             ),
  SC(   FILE_SUBP,              WRITE_BYTES,            "WRITE_BYTES",           PAR16,PAR16,PAR8,                               0,0,0,0,0             ),
  SC(   FILE_SUBP,              REMOVE,                 "REMOVE",                PAR8,                                           0,0,0,0,0,0,0         ),
  SC(   FILE_SUBP,              MOVE,                   "MOVE",                  PAR8,PAR8,                                      0,0,0,0,0,0           ),

  SC(   ARRAY_SUBP,             CREATE8,                "CREATE8",               PAR32,PAR16,                                    0,0,0,0,0,0           ),
  SC(   ARRAY_SUBP,             CREATE16,               "CREATE16",              PAR32,PAR16,                                    0,0,0,0,0,0           ),
  SC(   ARRAY_SUBP,             CREATE32,               "CREATE32",              PAR32,PAR16,                                    0,0,0,0,0,0           ),
  SC(   ARRAY_SUBP,             CREATEF,                "CREATEF",               PAR32,PAR16,                                    0,0,0,0,0,0           ),
  SC(   ARRAY_SUBP,             RESIZE,                 "RESIZE",                PAR16,PAR32,                                    0,0,0,0,0,0           ),
  SC(   ARRAY_SUBP,             DELETE,                 "DELETE",                PAR16,                                          0,0,0,0,0,0,0         ),
  SC(   ARRAY_SUBP,             FILL,                   "FILL",                  PAR16,PARV,                                     0,0,0,0,0,0           ),
  SC(   ARRAY_SUBP,             COPY,                   "COPY",                  PAR16,PAR16,                                    0,0,0,0,0,0           ),
  SC(   ARRAY_SUBP,             INIT8,                  "INIT8",                 PAR16,PAR32,PAR32,PARVALUES,PAR8,               0,0,0                 ),
  SC(   ARRAY_SUBP,             INIT16,                 "INIT16",                PAR16,PAR32,PAR32,PARVALUES,PAR16,              0,0,0                 ),
  SC(   ARRAY_SUBP,             INIT32,                 "INIT32",                PAR16,PAR32,PAR32,PARVALUES,PAR32,              0,0,0                 ),
  SC(   ARRAY_SUBP,             INITF,                  "INITF",                 PAR16,PAR32,PAR32,PARVALUES,PARF,               0,0,0                 ),
  SC(   ARRAY_SUBP,             SIZE,                   "SIZE",                  PAR16,PAR32,                                    0,0,0,0,0,0           ),
  SC(   ARRAY_SUBP,             READ_CONTENT,           "READ_CONTENT",          PAR16,PAR16,PAR32,PAR32,PAR8,                   0,0,0                 ),
  SC(   ARRAY_SUBP,             WRITE_CONTENT,          "WRITE_CONTENT",         PAR16,PAR16,PAR32,PAR32,PAR8,                   0,0,0                 ),
  SC(   ARRAY_SUBP,             READ_SIZE,              "READ_SIZE",             PAR16,PAR16,PAR32,                              0,0,0,0,0             ),

  SC(   FILENAME_SUBP,          EXIST,                  "EXIST",                 PAR8,PAR8,                                      0,0,0,0,0,0           ),
  SC(   FILENAME_SUBP,          TOTALSIZE,              "TOTALSIZE",             PAR8,PAR32,PAR32,                               0,0,0,0,0             ),
  SC(   FILENAME_SUBP,          SPLIT,                  "SPLIT",                 PAR8,PAR8,PAR8,PAR8,PAR8,                       0,0,0                 ),
  SC(   FILENAME_SUBP,          MERGE,                  "MERGE",                 PAR8,PAR8,PAR8,PAR8,PAR8,                       0,0,0                 ),
  SC(   FILENAME_SUBP,          CHECK,                  "CHECK",                 PAR8,PAR8,                                      0,0,0,0,0,0           ),
  SC(   FILENAME_SUBP,          PACK,                   "PACK",                  PAR8,                                           0,0,0,0,0,0,0         ),
  SC(   FILENAME_SUBP,          UNPACK,                 "UNPACK",                PAR8,                                           0,0,0,0,0,0,0         ),
  SC(   FILENAME_SUBP,          GET_FOLDERNAME,         "GET_FOLDERNAME",        PAR8,PAR8,                                      0,0,0,0,0,0           ),

  #     VM
  SC(   VM_SUBP,                SET_ERROR,              "SET_ERROR",             PAR8,                                           0,0,0,0,0,0,0         ),
  SC(   VM_SUBP,                GET_ERROR,              "GET_ERROR",             PAR8,                                           0,0,0,0,0,0,0         ),
  SC(   VM_SUBP,                ERRORTEXT,              "ERRORTEXT",             PAR8,PAR8,PAR8,                                 0,0,0,0,0             ),

  SC(   VM_SUBP,                GET_VOLUME,             "GET_VOLUME",            PAR8,                                           0,0,0,0,0,0,0         ),
  SC(   VM_SUBP,                SET_VOLUME,             "SET_VOLUME",            PAR8,                                           0,0,0,0,0,0,0         ),
  SC(   VM_SUBP,                GET_MINUTES,            "GET_MINUTES",           PAR8,                                           0,0,0,0,0,0,0         ),
  SC(   VM_SUBP,                SET_MINUTES,            "SET_MINUTES",           PAR8,                                           0,0,0,0,0,0,0         ),

  SC(   TST_SUBP,               TST_OPEN,               "TST_OPEN",              0,                                              0,0,0,0,0,0,0         ),
  SC(   TST_SUBP,               TST_CLOSE,              "TST_CLOSE",             0,                                              0,0,0,0,0,0,0         ),
  SC(   TST_SUBP,               TST_READ_PINS,          "TST_READ_PINS",         PAR8,PAR8,PAR8,                                 0,0,0,0,0             ),
  SC(   TST_SUBP,               TST_WRITE_PINS,         "TST_WRITE_PINS",        PAR8,PAR8,PAR8,                                 0,0,0,0,0             ),
  SC(   TST_SUBP,               TST_READ_ADC,           "TST_READ_ADC",          PAR8,PAR16,                                     0,0,0,0,0,0           ),
  SC(   TST_SUBP,               TST_WRITE_UART,         "TST_WRITE_UART",        PAR8,PAR8,PAR8,                                 0,0,0,0,0             ),
  SC(   TST_SUBP,               TST_READ_UART,          "TST_READ_UART",         PAR8,PAR8,PAR8,                                 0,0,0,0,0             ),
  SC(   TST_SUBP,               TST_ENABLE_UART,        "TST_ENABLE_UART",       PAR32,                                          0,0,0,0,0,0,0         ),
  SC(   TST_SUBP,               TST_DISABLE_UART,       "TST_DISABLE_UART",      0,                                              0,0,0,0,0,0,0         ),
  SC(   TST_SUBP,               TST_ACCU_SWITCH,        "TST_ACCU_SWITCH",       PAR8,                                           0,0,0,0,0,0,0         ),
  SC(   TST_SUBP,               TST_BOOT_MODE2,         "TST_BOOT_MODE2",        0,                                              0,0,0,0,0,0,0         ),
  SC(   TST_SUBP,               TST_POLL_MODE2,         "TST_POLL_MODE2",        PAR8,                                           0,0,0,0,0,0,0         ),
  SC(   TST_SUBP,               TST_CLOSE_MODE2,        "TST_CLOSE_MODE2",       0,                                              0,0,0,0,0,0,0         ),
  SC(   TST_SUBP,               TST_RAM_CHECK,          "TST_RAM_CHECK",         PAR8,                                           0,0,0,0,0,0,0         ),

  SC(   STRING_SUBP,            GET_SIZE,               "GET_SIZE",              PAR8,PAR16,                                     0,0,0,0,0,0           ),
  SC(   STRING_SUBP,            ADD,                    "ADD",                   PAR8,PAR8,PAR8,                                 0,0,0,0,0             ),
  SC(   STRING_SUBP,            COMPARE,                "COMPARE",               PAR8,PAR8,PAR8,                                 0,0,0,0,0             ),
  SC(   STRING_SUBP,            DUPLICATE,              "DUPLICATE",             PAR8,PAR8,                                      0,0,0,0,0,0           ),
  SC(   STRING_SUBP,            VALUE_TO_STRING,        "VALUE_TO_STRING",       PARF,PAR8,PAR8,PAR8,                            0,0,0,0               ),
  SC(   STRING_SUBP,            STRING_TO_VALUE,        "STRING_TO_VALUE",       PAR8,PARF,                                      0,0,0,0,0,0           ),
  SC(   STRING_SUBP,            STRIP,                  "STRIP",                 PAR8,PAR8,                                      0,0,0,0,0,0           ),
  SC(   STRING_SUBP,            NUMBER_TO_STRING,       "NUMBER_TO_STRING",      PAR16,PAR8,PAR8,                                0,0,0,0,0             ),
  SC(   STRING_SUBP,            SUB,                    "SUB",                   PAR8,PAR8,PAR8,                                 0,0,0,0,0             ),
  SC(   STRING_SUBP,            VALUE_FORMATTED,        "VALUE_FORMATTED",       PARF,PAR8,PAR8,PAR8,                            0,0,0,0               ),
  SC(   STRING_SUBP,            NUMBER_FORMATTED,       "NUMBER_FORMATTED",      PAR32,PAR8,PAR8,PAR8,                           0,0,0,0               ),

  #     UI
  SC(   UI_READ_SUBP,           GET_VBATT,              "GET_VBATT",             PARF,                                           0,0,0,0,0,0,0         ),
  SC(   UI_READ_SUBP,           GET_IBATT,              "GET_IBATT",             PARF,                                           0,0,0,0,0,0,0         ),
  SC(   UI_READ_SUBP,           GET_OS_VERS,            "GET_OS_VERS",           PAR8,PAR8,                                      0,0,0,0,0,0           ),
  SC(   UI_READ_SUBP,           GET_EVENT,              "GET_EVENT",             PAR8,                                           0,0,0,0,0,0,0         ),
  SC(   UI_READ_SUBP,           GET_TBATT,              "GET_TBATT",             PARF,                                           0,0,0,0,0,0,0         ),
  SC(   UI_READ_SUBP,           GET_IINT,               "GET_IINT",              PARF,                                           0,0,0,0,0,0,0         ),
  SC(   UI_READ_SUBP,           GET_IMOTOR,             "GET_IMOTOR",            PARF,                                           0,0,0,0,0,0,0         ),
  SC(   UI_READ_SUBP,           GET_STRING,             "GET_STRING",            PAR8,PAR8,                                      0,0,0,0,0,0           ),
  SC(   UI_READ_SUBP,           KEY,                    "KEY",                   PAR8,                                           0,0,0,0,0,0,0         ),
  SC(   UI_READ_SUBP,           GET_SHUTDOWN,           "GET_SHUTDOWN",          PAR8,                                           0,0,0,0,0,0,0         ),
  SC(   UI_READ_SUBP,           GET_WARNING,            "GET_WARNING",           PAR8,                                           0,0,0,0,0,0,0         ),
  SC(   UI_READ_SUBP,           GET_LBATT,              "GET_LBATT",             PAR8,                                           0,0,0,0,0,0,0         ),
  SC(   UI_READ_SUBP,           GET_ADDRESS,            "GET_ADDRESS",           PAR32,                                          0,0,0,0,0,0,0         ),
  SC(   UI_READ_SUBP,           GET_CODE,               "GET_CODE",              PAR32,PAR32,PAR32,PAR8,                         0,0,0,0               ),
  SC(   UI_READ_SUBP,           TEXTBOX_READ,           "TEXTBOX_READ",          PAR8,PAR32,PAR8,PAR8,PAR16,PAR8,                0,0                   ),
  SC(   UI_READ_SUBP,           GET_HW_VERS,            "GET_HW_VERS",           PAR8,PAR8,                                      0,0,0,0,0,0           ),
  SC(   UI_READ_SUBP,           GET_FW_VERS,            "GET_FW_VERS",           PAR8,PAR8,                                      0,0,0,0,0,0           ),
  SC(   UI_READ_SUBP,           GET_FW_BUILD,           "GET_FW_BUILD",          PAR8,PAR8,                                      0,0,0,0,0,0           ),
  SC(   UI_READ_SUBP,           GET_OS_BUILD,           "GET_OS_BUILD",          PAR8,PAR8,                                      0,0,0,0,0,0           ),
  SC(   UI_READ_SUBP,           GET_VERSION,            "GET_VERSION",           PAR8,PAR8,                                      0,0,0,0,0,0           ),
  SC(   UI_READ_SUBP,           GET_IP,                 "GET_IP",                PAR8,PAR8,                                      0,0,0,0,0,0           ),
  SC(   UI_READ_SUBP,           GET_SDCARD,             "GET_SDCARD",            PAR8,PAR32,PAR32,                               0,0,0,0,0             ),
  SC(   UI_READ_SUBP,           GET_USBSTICK,           "GET_USBSTICK",          PAR8,PAR32,PAR32,                               0,0,0,0,0             ),

  SC(   UI_WRITE_SUBP,          WRITE_FLUSH,            "WRITE_FLUSH",           0,                                              0,0,0,0,0,0,0         ),
  SC(   UI_WRITE_SUBP,          FLOATVALUE,             "FLOATVALUE",            PARF,PAR8,PAR8,                                 0,0,0,0,0             ),
  SC(   UI_WRITE_SUBP,          STAMP,                  "STAMP",                 PAR8,                                           0,0,0,0,0,0,0         ),
  SC(   UI_WRITE_SUBP,          PUT_STRING,             "PUT_STRING",            PAR8,                                           0,0,0,0,0,0,0         ),
  SC(   UI_WRITE_SUBP,          CODE,                   "CODE",                  PAR8,PAR32,                                     0,0,0,0,0,0           ),
  SC(   UI_WRITE_SUBP,          DOWNLOAD_END,           "DOWNLOAD_END",          0,                                              0,0,0,0,0,0,0         ),
  SC(   UI_WRITE_SUBP,          SCREEN_BLOCK,           "SCREEN_BLOCK",          PAR8,                                           0,0,0,0,0,0,0         ),
  SC(   UI_WRITE_SUBP,          TEXTBOX_APPEND,         "TEXTBOX_APPEND",        PAR8,PAR32,PAR8,PAR8,                           0,0,0,0               ),
  SC(   UI_WRITE_SUBP,          SET_BUSY,               "SET_BUSY",              PAR8,                                           0,0,0,0,0,0,0         ),
  SC(   UI_WRITE_SUBP,          VALUE8,                 "VALUE8",                PAR8,                                           0,0,0,0,0,0,0         ),
  SC(   UI_WRITE_SUBP,          VALUE16,                "VALUE16",               PAR16,                                          0,0,0,0,0,0,0         ),
  SC(   UI_WRITE_SUBP,          VALUE32,                "VALUE32",               PAR32,                                          0,0,0,0,0,0,0         ),
  SC(   UI_WRITE_SUBP,          VALUEF,                 "VALUEF",                PARF,                                           0,0,0,0,0,0,0         ),
  SC(   UI_WRITE_SUBP,          INIT_RUN,               "INIT_RUN",              0,                                              0,0,0,0,0,0,0         ),
  SC(   UI_WRITE_SUBP,          UPDATE_RUN,             "UPDATE_RUN",            0,                                              0,0,0,0,0,0,0         ),
  SC(   UI_WRITE_SUBP,          LED,                    "LED",                   PAR8,                                           0,0,0,0,0,0,0         ),
  SC(   UI_WRITE_SUBP,          POWER,                  "POWER",                 PAR8,                                           0,0,0,0,0,0,0         ),
  SC(   UI_WRITE_SUBP,          TERMINAL,               "TERMINAL",              PAR8,                                           0,0,0,0,0,0,0         ),
  SC(   UI_WRITE_SUBP,          GRAPH_SAMPLE,           "GRAPH_SAMPLE",          0,                                              0,0,0,0,0,0,0         ),
  SC(   UI_WRITE_SUBP,          SET_TESTPIN,            "SET_TESTPIN",           PAR8,                                           0,0,0,0,0,0,0         ),

  SC(   UI_DRAW_SUBP,           UPDATE,                 "UPDATE",                0,                                              0,0,0,0,0,0,0         ),
  SC(   UI_DRAW_SUBP,           CLEAN,                  "CLEAN",                 0,                                              0,0,0,0,0,0,0         ),
  SC(   UI_DRAW_SUBP,           FILLRECT,               "FILLRECT",              PAR8,PAR16,PAR16,PAR16,PAR16,                   0,0,0                 ),
  SC(   UI_DRAW_SUBP,           RECT,                   "RECT",                  PAR8,PAR16,PAR16,PAR16,PAR16,                   0,0,0                 ),
  SC(   UI_DRAW_SUBP,           PIXEL,                  "PIXEL",                 PAR8,PAR16,PAR16,                               0,0,0,0,0             ),
  SC(   UI_DRAW_SUBP,           LINE,                   "LINE",                  PAR8,PAR16,PAR16,PAR16,PAR16,                   0,0,0                 ),
  SC(   UI_DRAW_SUBP,           CIRCLE,                 "CIRCLE",                PAR8,PAR16,PAR16,PAR16,                         0,0,0,0               ),
  SC(   UI_DRAW_SUBP,           TEXT,                   "TEXT",                  PAR8,PAR16,PAR16,PAR8,                          0,0,0,0               ),
  SC(   UI_DRAW_SUBP,           ICON,                   "ICON",                  PAR8,PAR16,PAR16,PAR8,PAR8,                     0,0,0                 ),
  SC(   UI_DRAW_SUBP,           PICTURE,                "PICTURE",               PAR8,PAR16,PAR16,PAR32,                         0,0,0,0               ),
  SC(   UI_DRAW_SUBP,           VALUE,                  "VALUE",                 PAR8,PAR16,PAR16,PARF,PAR8,PAR8,                0,0                   ),
  SC(   UI_DRAW_SUBP,           NOTIFICATION,           "NOTIFICATION",          PAR8,PAR16,PAR16,PAR8,PAR8,PAR8,PAR8,PAR8                             ),
  SC(   UI_DRAW_SUBP,           QUESTION,               "QUESTION",              PAR8,PAR16,PAR16,PAR8,PAR8,PAR8,PAR8,PAR8                             ),
  SC(   UI_DRAW_SUBP,           KEYBOARD,               "KEYBOARD",              PAR8,PAR16,PAR16,PAR8,PAR8,PAR8,PAR8,PAR8                             ),
  SC(   UI_DRAW_SUBP,           BROWSE,                 "BROWSE",                PAR8,PAR16,PAR16,PAR16,PAR16,PAR8,PAR8,PAR8                           ),
  SC(   UI_DRAW_SUBP,           VERTBAR,                "VERTBAR",               PAR8,PAR16,PAR16,PAR16,PAR16,PAR16,PAR16,PAR16                        ),
  SC(   UI_DRAW_SUBP,           INVERSERECT,            "INVERSERECT",           PAR16,PAR16,PAR16,PAR16,                        0,0,0,0               ),
  SC(   UI_DRAW_SUBP,           SELECT_FONT,            "SELECT_FONT",           PAR8,                                           0,0,0,0,0,0,0         ),
  SC(   UI_DRAW_SUBP,           TOPLINE,                "TOPLINE",               PAR8,                                           0,0,0,0,0,0,0         ),
  SC(   UI_DRAW_SUBP,           FILLWINDOW,             "FILLWINDOW",            PAR8,PAR16,PAR16,                               0,0,0,0,0             ),
  SC(   UI_DRAW_SUBP,           SCROLL,                 "SCROLL",                PAR16,                                          0,0,0,0,0,0,0         ),
  SC(   UI_DRAW_SUBP,           DOTLINE,                "DOTLINE",               PAR8,PAR16,PAR16,PAR16,PAR16,PAR16,PAR16,       0                     ),
  SC(   UI_DRAW_SUBP,           VIEW_VALUE,             "VIEW_VALUE",            PAR8,PAR16,PAR16,PARF,PAR8,PAR8,                0,0                   ),
  SC(   UI_DRAW_SUBP,           VIEW_UNIT,              "VIEW_UNIT",             PAR8,PAR16,PAR16,PARF,PAR8,PAR8,PAR8,PAR8                             ),
  SC(   UI_DRAW_SUBP,           FILLCIRCLE,             "FILLCIRCLE",            PAR8,PAR16,PAR16,PAR16,                         0,0,0,0               ),
  SC(   UI_DRAW_SUBP,           STORE,                  "STORE",                 PAR8,                                           0,0,0,0,0,0,0         ),
  SC(   UI_DRAW_SUBP,           RESTORE,                "RESTORE",               PAR8,                                           0,0,0,0,0,0,0         ),
  SC(   UI_DRAW_SUBP,           ICON_QUESTION,          "ICON_QUESTION",         PAR8,PAR16,PAR16,PAR8,PAR32,                    0,0,0                 ),
  SC(   UI_DRAW_SUBP,           BMPFILE,                "BMPFILE",               PAR8,PAR16,PAR16,PAR8,                          0,0,0,0               ),
  SC(   UI_DRAW_SUBP,           GRAPH_SETUP,            "GRAPH_SETUP",           PAR16,PAR16,PAR16,PAR16,PAR8,PAR16,PAR16,PAR16                        ),
  SC(   UI_DRAW_SUBP,           GRAPH_DRAW,             "GRAPH_DRAW",            PAR8,PARF,PARF,PARF,PARF,                       0,0,0                 ),
  SC(   UI_DRAW_SUBP,           POPUP,                  "POPUP",                 PAR8,                                           0,0,0,0,0,0,0         ),
  SC(   UI_DRAW_SUBP,           TEXTBOX,                "TEXTBOX",               PAR16,PAR16,PAR16,PAR16,PAR8,PAR32,PAR8,PAR8                          ),

  SC(   UI_BUTTON_SUBP,         SHORTPRESS,             "SHORTPRESS",            PAR8,PAR8,                                      0,0,0,0,0,0           ),
  SC(   UI_BUTTON_SUBP,         LONGPRESS,              "LONGPRESS",             PAR8,PAR8,                                      0,0,0,0,0,0           ),
  SC(   UI_BUTTON_SUBP,         FLUSH,                  "FLUSH",                 0,                                              0,0,0,0,0,0,0         ),
  SC(   UI_BUTTON_SUBP,         WAIT_FOR_PRESS,         "WAIT_FOR_PRESS",        0,                                              0,0,0,0,0,0,0         ),
  SC(   UI_BUTTON_SUBP,         PRESS,                  "PRESS",                 PAR8,                                           0,0,0,0,0,0,0         ),
  SC(   UI_BUTTON_SUBP,         RELEASE,                "RELEASE",               PAR8,                                           0,0,0,0,0,0,0         ),
  SC(   UI_BUTTON_SUBP,         GET_HORZ,               "GET_HORZ",              PAR16,                                          0,0,0,0,0,0,0         ),
  SC(   UI_BUTTON_SUBP,         GET_VERT,               "GET_VERT",              PAR16,                                          0,0,0,0,0,0,0         ),
  SC(   UI_BUTTON_SUBP,         PRESSED,                "PRESSED",               PAR8,PAR8,                                      0,0,0,0,0,0           ),
  SC(   UI_BUTTON_SUBP,         SET_BACK_BLOCK,         "SET_BACK_BLOCK",        PAR8,                                           0,0,0,0,0,0,0         ),
  SC(   UI_BUTTON_SUBP,         GET_BACK_BLOCK,         "GET_BACK_BLOCK",        PAR8,                                           0,0,0,0,0,0,0         ),
  SC(   UI_BUTTON_SUBP,         TESTSHORTPRESS,         "TESTSHORTPRESS",        PAR8,PAR8,                                      0,0,0,0,0,0           ),
  SC(   UI_BUTTON_SUBP,         TESTLONGPRESS,          "TESTLONGPRESS",         PAR8,PAR8,                                      0,0,0,0,0,0           ),
  SC(   UI_BUTTON_SUBP,         GET_BUMBED,             "GET_BUMBED",            PAR8,PAR8,                                      0,0,0,0,0,0           ),
  SC(   UI_BUTTON_SUBP,         GET_CLICK,              "GET_CLICK",             PAR8,                                           0,0,0,0,0,0,0         ),

  #     Com
  SC(   COM_READ_SUBP,          COMMAND,                "COMMAND",               PAR32,PAR32,PAR32,PAR8,                         0,0,0,0               ),
  SC(   COM_WRITE_SUBP,         REPLY,                  "REPLY",                 PAR32,PAR32,PAR8,                               0,0,0,0,0             ),

  #     Sound
  SC(   SOUND_SUBP,             BREAK,                  "BREAK",                 0,                                              0,0,0,0,0,0,0         ),
  SC(   SOUND_SUBP,             TONE,                   "TONE",                  PAR8,PAR16,PAR16,                               0,0,0,0,0             ),
  SC(   SOUND_SUBP,             PLAY,                   "PLAY",                  PAR8,PARS,                                      0,0,0,0,0,0           ),
  SC(   SOUND_SUBP,             REPEAT,                 "REPEAT",                PAR8,PARS,                                      0,0,0,0,0,0           ),
  SC(   SOUND_SUBP,             SERVICE,                "SERVICE",               0,                                              0,0,0,0,0,0,0         ),

  #     Input
  SC(   INPUT_SUBP,             GET_TYPEMODE,           "GET_TYPEMODE",          PAR8,PAR8,PAR8,PAR8,                            0,0,0,0               ),
  SC(   INPUT_SUBP,             GET_CONNECTION,         "GET_CONNECTION",        PAR8,PAR8,PAR8,                                 0,0,0,0,0             ),
  SC(   INPUT_SUBP,             GET_NAME,               "GET_NAME",              PAR8,PAR8,PAR8,PAR8,                            0,0,0,0               ),
  SC(   INPUT_SUBP,             GET_SYMBOL,             "GET_SYMBOL",            PAR8,PAR8,PAR8,PAR8,                            0,0,0,0               ),
  SC(   INPUT_SUBP,             GET_FORMAT,             "GET_FORMAT",            PAR8,PAR8,PAR8,PAR8,PAR8,PAR8,                  0,0                   ),
  SC(   INPUT_SUBP,             GET_RAW,                "GET_RAW",               PAR8,PAR8,PAR32,                                0,0,0,0,0             ),
  SC(   INPUT_SUBP,             GET_MODENAME,           "GET_MODENAME",          PAR8,PAR8,PAR8,PAR8,PAR8,                       0,0,0                 ),
  SC(   INPUT_SUBP,             SET_RAW,                "SET_RAW",               PAR8,PAR8,PAR8,PAR32,                           0,0,0,0               ),
  SC(   INPUT_SUBP,             GET_FIGURES,            "GET_FIGURES",           PAR8,PAR8,PAR8,PAR8,                            0,0,0,0               ),
  SC(   INPUT_SUBP,             GET_CHANGES,            "GET_CHANGES",           PAR8,PAR8,PARF,                                 0,0,0,0,0             ),
  SC(   INPUT_SUBP,             CLR_CHANGES,            "CLR_CHANGES",           PAR8,PAR8,0,                                    0,0,0,0,0             ),
  SC(   INPUT_SUBP,             READY_PCT,              "READY_PCT",             PAR8,PAR8,PAR8,PAR8,PARNO,                      0,0,0                 ),
  SC(   INPUT_SUBP,             READY_RAW,              "READY_RAW",             PAR8,PAR8,PAR8,PAR8,PARNO,                      0,0,0                 ),
  SC(   INPUT_SUBP,             READY_SI,               "READY_SI",              PAR8,PAR8,PAR8,PAR8,PARNO,                      0,0,0                 ),
  SC(   INPUT_SUBP,             GET_MINMAX,             "GET_MINMAX",            PAR8,PAR8,PARF,PARF,                            0,0,0,0               ),
  SC(   INPUT_SUBP,             CAL_MINMAX,             "CAL_MINMAX",            PAR8,PAR8,PAR32,PAR32,                          0,0,0,0               ),
  SC(   INPUT_SUBP,             CAL_DEFAULT,            "CAL_DEFAULT",           PAR8,PAR8,0,                                    0,0,0,0,0             ),
  SC(   INPUT_SUBP,             CAL_MIN,                "CAL_MIN",               PAR8,PAR8,PAR32,                                0,0,0,0,0             ),
  SC(   INPUT_SUBP,             CAL_MAX,                "CAL_MAX",               PAR8,PAR8,PAR32,                                0,0,0,0,0             ),
  SC(   INPUT_SUBP,             GET_BUMPS,              "GET_BUMPS",             PAR8,PAR8,PARF,                                 0,0,0,0,0             ),
  SC(   INPUT_SUBP,             SETUP,                  "SETUP",                 PAR8,PAR8,PAR8,PAR16,PAR8,PAR8,PAR8,PAR8                              ),
  SC(   INPUT_SUBP,             CLR_ALL,                "CLR_ALL",               PAR8,                                           0,0,0,0,0,0,0         ),
  SC(   INPUT_SUBP,             STOP_ALL,               "STOP_ALL",              PAR8,                                           0,0,0,0,0,0,0         ),

  #     Math
  SC(   MATH_SUBP,              EXP,                    "EXP",                   PARF,PARF,                                      0,0,0,0,0,0           ),
  SC(   MATH_SUBP,              MOD,                    "MOD",                   PARF,PARF,PARF,                                 0,0,0,0,0             ),
  SC(   MATH_SUBP,              FLOOR,                  "FLOOR",                 PARF,PARF,                                      0,0,0,0,0,0           ),
  SC(   MATH_SUBP,              CEIL,                   "CEIL",                  PARF,PARF,                                      0,0,0,0,0,0           ),
  SC(   MATH_SUBP,              ROUND,                  "ROUND",                 PARF,PARF,                                      0,0,0,0,0,0           ),
  SC(   MATH_SUBP,              ABS,                    "ABS",                   PARF,PARF,                                      0,0,0,0,0,0           ),
  SC(   MATH_SUBP,              NEGATE,                 "NEGATE",                PARF,PARF,                                      0,0,0,0,0,0           ),
  SC(   MATH_SUBP,              SQRT,                   "SQRT",                  PARF,PARF,                                      0,0,0,0,0,0           ),
  SC(   MATH_SUBP,              LOG,                    "LOG",                   PARF,PARF,                                      0,0,0,0,0,0           ),
  SC(   MATH_SUBP,              LN,                     "LN",                    PARF,PARF,                                      0,0,0,0,0,0           ),
  SC(   MATH_SUBP,              SIN,                    "SIN",                   PARF,PARF,                                      0,0,0,0,0,0           ),
  SC(   MATH_SUBP,              COS,                    "COS",                   PARF,PARF,                                      0,0,0,0,0,0           ),
  SC(   MATH_SUBP,              TAN,                    "TAN",                   PARF,PARF,                                      0,0,0,0,0,0           ),
  SC(   MATH_SUBP,              ASIN,                   "ASIN",                  PARF,PARF,                                      0,0,0,0,0,0           ),
  SC(   MATH_SUBP,              ACOS,                   "ACOS",                  PARF,PARF,                                      0,0,0,0,0,0           ),
  SC(   MATH_SUBP,              ATAN,                   "ATAN",                  PARF,PARF,                                      0,0,0,0,0,0           ),
  SC(   MATH_SUBP,              MOD8,                   "MOD8",                  PAR8,PAR8,PAR8,                                 0,0,0,0,0             ),
  SC(   MATH_SUBP,              MOD16,                  "MOD16",                 PAR16,PAR16,PAR16,                              0,0,0,0,0             ),
  SC(   MATH_SUBP,              MOD32,                  "MOD32",                 PAR32,PAR32,PAR32,                              0,0,0,0,0             ),
  SC(   MATH_SUBP,              POW,                    "POW",                   PARF,PARF,PARF,                                 0,0,0,0,0             ),
  SC(   MATH_SUBP,              TRUNC,                  "TRUNC",                 PARF,PAR8,PARF,                                 0,0,0,0,0             ),

  #     ComGet
  SC(   COM_GET_SUBP,           GET_ON_OFF,             "GET_ON_OFF",            PAR8,PAR8,                                      0,0,0,0,0,0           ),
  SC(   COM_GET_SUBP,           GET_VISIBLE,            "GET_VISIBLE",           PAR8,PAR8,                                      0,0,0,0,0,0           ),
  SC(   COM_GET_SUBP,           GET_RESULT,             "GET_RESULT",            PAR8,PAR8,PAR8,                                 0,0,0,0,0             ),
  SC(   COM_GET_SUBP,           GET_PIN,                "GET_PIN",               PAR8,PAR8,PAR8,PAR8,                            0,0,0,0               ),
  SC(   COM_GET_SUBP,           SEARCH_ITEMS,           "SEARCH_ITEMS",          PAR8,PAR8,                                      0,0,0,0,0,0           ),
  SC(   COM_GET_SUBP,           SEARCH_ITEM,            "SEARCH_ITEM",           PAR8,PAR8,PAR8,PAR8,PAR8,PAR8,PAR8,PAR8                               ),
  SC(   COM_GET_SUBP,           FAVOUR_ITEMS,           "FAVOUR_ITEMS",          PAR8,PAR8,                                      0,0,0,0,0,0           ),
  SC(   COM_GET_SUBP,           FAVOUR_ITEM,            "FAVOUR_ITEM",           PAR8,PAR8,PAR8,PAR8,PAR8,PAR8,PAR8,             0                     ),
  SC(   COM_GET_SUBP,           GET_ID,                 "GET_ID",                PAR8,PAR8,PAR8,                                 0,0,0,0,0             ),
  SC(   COM_GET_SUBP,           GET_BRICKNAME,          "GET_BRICKNAME",         PAR8,PAR8,                                      0,0,0,0,0,0           ),
  SC(   COM_GET_SUBP,           GET_NETWORK,            "GET_NETWORK",           PAR8,PAR8,PAR8,PAR8,PAR8,                       0,0,0                 ),
  SC(   COM_GET_SUBP,           GET_PRESENT,            "GET_PRESENT",           PAR8,PAR8,                                      0,0,0,0,0,0           ),
  SC(   COM_GET_SUBP,           GET_ENCRYPT,            "GET_ENCRYPT",           PAR8,PAR8,PAR8,                                 0,0,0,0,0             ),
  SC(   COM_GET_SUBP,           CONNEC_ITEMS,           "CONNEC_ITEMS",          PAR8,PAR8,                                      0,0,0,0,0,0           ),
  SC(   COM_GET_SUBP,           CONNEC_ITEM,            "CONNEC_ITEM",           PAR8,PAR8,PAR8,PAR8,PAR8,                       0,0,0                 ),
  SC(   COM_GET_SUBP,           GET_INCOMING,           "GET_INCOMING",          PAR8,PAR8,PAR8,PAR8,                            0,0,0,0               ),
  SC(   COM_GET_SUBP,           GET_MODE2,              "GET_MODE2",             PAR8,PAR8,                                      0,0,0,0,0,0           ),

  #     ComSet
  SC(   COM_SET_SUBP,           SET_ON_OFF,             "SET_ON_OFF",            PAR8,PAR8,                                      0,0,0,0,0,0           ),
  SC(   COM_SET_SUBP,           SET_VISIBLE,            "SET_VISIBLE",           PAR8,PAR8,                                      0,0,0,0,0,0           ),
  SC(   COM_SET_SUBP,           SET_SEARCH,             "SET_SEARCH",            PAR8,PAR8,                                      0,0,0,0,0,0           ),
  SC(   COM_SET_SUBP,           SET_PIN,                "SET_PIN",               PAR8,PAR8,PAR8,                                 0,0,0,0,0             ),
  SC(   COM_SET_SUBP,           SET_PASSKEY,            "SET_PASSKEY",           PAR8,PAR8,                                      0,0,0,0,0,0           ),
  SC(   COM_SET_SUBP,           SET_CONNECTION,         "SET_CONNECTION",        PAR8,PAR8,PAR8,                                 0,0,0,0,0             ),
  SC(   COM_SET_SUBP,           SET_BRICKNAME,          "SET_BRICKNAME",         PAR8,                                           0,0,0,0,0,0,0         ),
  SC(   COM_SET_SUBP,           SET_MOVEUP,             "SET_MOVEUP",            PAR8,PAR8,                                      0,0,0,0,0,0           ),
  SC(   COM_SET_SUBP,           SET_MOVEDOWN,           "SET_MOVEDOWN",          PAR8,PAR8,                                      0,0,0,0,0,0           ),
  SC(   COM_SET_SUBP,           SET_ENCRYPT,            "SET_ENCRYPT",           PAR8,PAR8,PAR8,                                 0,0,0,0,0             ),
  SC(   COM_SET_SUBP,           SET_SSID,               "SET_SSID",              PAR8,PAR8,                                      0,0,0,0,0,0           ),
  SC(   COM_SET_SUBP,           SET_MODE2,              "SET_MODE2",             PAR8,PAR8,                                      0,0,0,0,0,0           ),
]

# --------------------------------------------------------------------------

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
