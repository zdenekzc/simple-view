
# http://github.com/mindboards/ev3sources/blob/master/lms2012/lms2012/source/bytecodes.h

# --------------------------------------------------------------------------

# formats

DATA_8        = 0x00                 # DATA8  (don't change)
DATA_16       = 0x01                 # DATA16 (don't change)
DATA_32       = 0x02                 # DATA32 (don't change)
DATA_F        = 0x03                 # DATAF  (don't change)
DATA_S        = 0x04                 # Zero terminated string
DATA_A        = 0x05                 # Array handle

DATA_V        = 0x07                 # Variable type

DATA_PCT      = 0x10                 # Percent (used in opINPUT_READEXT)
DATA_RAW      = 0x12                 # Raw     (used in opINPUT_READEXT)
DATA_SI       = 0x13                 # SI unit (used in opINPUT_READEXT)

# --------------------------------------------------------------------------

DATA8_NAN     = -128
DATA16_NAN    = -32768
DATA32_NAN    = 0x80000000
DATAF_NAN     = 0x7FC00000

DATA8_MIN     = -127
DATA8_MAX     = 127
DATA16_MIN    = -32767
DATA16_MAX    = 32767
DATA32_MIN    = -2147483647
DATA32_MAX    = 2147483647
DATAF_MIN     = -2147483647
DATAF_MAX     = 2147483647

# --------------------------------------------------------------------------

def LongToBytes (v) :
    return bytearray ([ v & 0xFF, (v >> 8) & 0xFF, (v >> 16) & 0xFF, (v >> 24) & 0xFF ])

def WordToBytes (v) :
    return bytearray ([ v & 0xFF, (v >> 8) & 0xFF ])

def ByteToBytes (v) :
    return bytearray ([ v & 0xFF ])

# --------------------------------------------------------------------------

BYTECODE_VERSION = 104

def PROGRAMHeader (VersionInfo, NumberOfObjects, GlobalBytes) :
    return ( bytearray ([ ord ('L'), ord ('E'), ord ('G'), ord ('O') ]) +
             LongToBytes (0) + # ProgramSize
             WordToBytes (BYTECODE_VERSION) +
             WordToBytes (NumberOfObjects) +
             LongToBytes (GlobalBytes) )

def VMTHREADHeader (OffsetToInstructions, LocalBytes) :
    return LongToBytes (OffsetToInstructions) + bytearray ([0, 0, 0, 0]) + LongToBytes (LocalBytes)

def SUBCALLHeader (OffsetToInstructions, LocalBytes) :
    return LongToBytes (OffsetToInstructions) + bytearray ([0, 0, 1, 0]) + LongToBytes (LocalBytes)

def BLOCKHeader (OffsetToInstructions, OwnerObjectId, TriggerCount) :
    return LongToBytes (OffsetToInstructions) + WordToBytes (OwnerObjectId) + WordToBytes (TriggerCount) + LongToBytes (0)

# --------------------------------------------------------------------------

PRIMPAR_SHORT       = 0x00
PRIMPAR_LONG        = 0x80

PRIMPAR_CONST       = 0x00
PRIMPAR_VARIABLE    = 0x40
PRIMPAR_LOCAL       = 0x00
PRIMPAR_GLOBAL      = 0x20
PRIMPAR_HANDLE      = 0x10
PRIMPAR_ADDR        = 0x08

PRIMPAR_INDEX       = 0x1F
PRIMPAR_CONST_SIGN  = 0x20
PRIMPAR_VALUE       = 0x3F

PRIMPAR_BYTES       = 0x07

PRIMPAR_STRING_OLD  = 0
PRIMPAR_1_BYTE      = 1
PRIMPAR_2_BYTES     = 2
PRIMPAR_4_BYTES     = 3
PRIMPAR_STRING      = 4

PRIMPAR_LABEL       = 0x20

# --------------------------------------------------------------------------

def byte (n) :
    return bytearray ([n])

# --------------------------------------------------------------------------

def HND (x) :
    return byte (PRIMPAR_HANDLE | x)

def ADR (x) :
    return byte (PRIMPAR_ADR | x)

def LCS (s) :
    t = byte (PRIMPAR_LONG | PRIMPAR_STRING)
    for c in s :
       t = t + byte (c)
    t = t + byte (0)
    return t

def LAB1 (v) :
    return  byte (PRIMPAR_LONG | PRIMPAR_LABEL) + ByteToBytes (v)

# --------------------------------------------------------------------------

def LC0 (v) :
    return  byte ((v & PRIMPAR_VALUE) | PRIMPAR_SHORT | PRIMPAR_CONST)

def LC1 (v) :
    return  byte (PRIMPAR_LONG | PRIMPAR_CONST | PRIMPAR_1_BYTE) + ByteToBytes (v)

def LC2 (v) :
    return  byte (PRIMPAR_LONG | PRIMPAR_CONST | PRIMPAR_2_BYTES) + WordToBytes (v)

def LC4 (v) :
    return  byte (PRIMPAR_LONG | PRIMPAR_CONST | PRIMPAR_4_BYTES) + LongToBytes (v)

def LC (v) :
    if v >= 0 and v <= PRIMPAR_VALUE :
       return LC0 (v)
    elif v >= 0 and v <= 0xFF :
       return LC1 (v)
    elif v >= 0 and v <= 0xFFFF :
       return LC2 (v)
    else :
       return LC4 (v)

# --------------------------------------------------------------------------

def LV0 (i) :
    return byte ((i & PRIMPAR_INDEX) | PRIMPAR_SHORT | PRIMPAR_VARIABLE | PRIMPAR_LOCAL)

def LV1 (v) :
    return  byte (PRIMPAR_LONG | PRIMPAR_VARIABLE | PRIMPAR_LOCAL | PRIMPAR_1_BYTE) + ByteToBytes (v)

def LV2 (v) :
    return  byte (PRIMPAR_LONG | PRIMPAR_VARIABLE | PRIMPAR_LOCAL | PRIMPAR_2_BYTES) + WordToBytes (v)

def LV4 (v) :
    return  byte (PRIMPAR_LONG | PRIMPAR_VARIABLE | PRIMPAR_LOCAL | PRIMPAR_4_BYTES) + LongToBytes (v)

def LV (v) :
    if v >= 0 and v <= PRIMPAR_INDEX :
       return LV0 (v)
    elif v >= 0 and v <= 0xFF :
       return LV1 (v)
    elif v >= 0 and v <= 0xFFFF :
       return LV2 (v)
    else :
       return LV4 (v)

# --------------------------------------------------------------------------

def GV0 (i) :
    return byte ((i & PRIMPAR_INDEX) | PRIMPAR_SHORT | PRIMPAR_VARIABLE | PRIMPAR_GLOBAL)

def GV1 (v) :
    return  byte (PRIMPAR_LONG | PRIMPAR_VARIABLE | PRIMPAR_GLOBAL | PRIMPAR_1_BYTE) + ByteToBytes (v)

def GV2 (v) :
    return  byte (PRIMPAR_LONG | PRIMPAR_VARIABLE | PRIMPAR_GLOBAL | PRIMPAR_2_BYTES) + WordToBytes (v)

def GV4 (v) :
    return  byte (PRIMPAR_LONG | PRIMPAR_VARIABLE | PRIMPAR_GLOBAL | PRIMPAR_4_BYTES) + LongToBytes (v)

def GV (v) :
    if v >= 0 and v <= PRIMPAR_INDEX :
       return GV0 (v)
    elif v >= 0 and v <= 0xFF :
       return GV1 (v)
    elif v >= 0 and v <= 0xFFFF :
       return GV2 (v)
    else :
       return GV4 (v)

# --------------------------------------------------------------------------

CALLPAR_IN          = 0x80
CALLPAR_OUT         = 0x40

CALLPAR_TYPE        = 0x07
CALLPAR_DATA8       = DATA_8
CALLPAR_DATA16      = DATA_16
CALLPAR_DATA32      = DATA_32
CALLPAR_DATAF       = DATA_F
CALLPAR_STRING      = DATA_S

IN_8                = (CALLPAR_IN  | CALLPAR_DATA8)
IN_16               = (CALLPAR_IN  | CALLPAR_DATA16)
IN_32               = (CALLPAR_IN  | CALLPAR_DATA32)
IN_F                = (CALLPAR_IN  | CALLPAR_DATAF)
IN_S                = (CALLPAR_IN  | CALLPAR_STRING)

OUT_8               = (CALLPAR_OUT | CALLPAR_DATA8)
OUT_16              = (CALLPAR_OUT | CALLPAR_DATA16)
OUT_32              = (CALLPAR_OUT | CALLPAR_DATA32)
OUT_F               = (CALLPAR_OUT | CALLPAR_DATAF)
OUT_S               = (CALLPAR_OUT | CALLPAR_STRING)

IO_8                = IN_8  | OUT_8
IO_16               = IN_16 | OUT_16
IO_32               = IN_32 | OUT_32
IO_F                = IN_F  | OUT_F
IO_S                = IN_S  | OUT_S

# --------------------------------------------------------------------------

if __name__ == '__main__':
    import pprint
    pp = pprint.PrettyPrinter (indent=4)
    pp.pprint (PROGRAMHeader (1, 2, 3))
    pp.pprint (VMTHREADHeader (1, 2))
    pp.pprint (SUBCALLHeader (1, 2))

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
