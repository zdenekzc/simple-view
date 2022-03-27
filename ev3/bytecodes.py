
# https://github.com/mindboards/ev3sources/blob/master/lms2012/lms2012/source/bytecodes.h

opERROR                     = 0x00
opNOP                       = 0x01
opPROGRAM_STOP              = 0x02
opPROGRAM_START             = 0x03
opOBJECT_STOP               = 0x04
opOBJECT_START              = 0x05
opOBJECT_TRIG               = 0x06
opOBJECT_WAIT               = 0x07
opRETURN                    = 0x08
opCALL                      = 0x09
opOBJECT_END                = 0x0A
opSLEEP                     = 0x0B
opPROGRAM_INFO              = 0x0C
opLABEL                     = 0x0D
opPROBE                     = 0x0E
opDO                        = 0x0F

opADD8                      = 0x10
opADD16                     = 0x11
opADD32                     = 0x12
opADDF                      = 0x13

opSUB8                      = 0x14
opSUB16                     = 0x15
opSUB32                     = 0x16
opSUBF                      = 0x17

opMUL8                      = 0x18
opMUL16                     = 0x19
opMUL32                     = 0x1A
opMULF                      = 0x1B

opDIV8                      = 0x1C
opDIV16                     = 0x1D
opDIV32                     = 0x1E
opDIVF                      = 0x1F

opOR8                       = 0x20
opOR16                      = 0x21
opOR32                      = 0x22

opAND8                      = 0x24
opAND16                     = 0x25
opAND32                     = 0x26

opXOR8                      = 0x28
opXOR16                     = 0x29
opXOR32                     = 0x2A

opRL8                       = 0x2C
opRL16                      = 0x2D
opRL32                      = 0x2E

opINIT_BYTES                = 0x2F

opMOVE8_8                   = 0x30
opMOVE8_16                  = 0x31
opMOVE8_32                  = 0x32
opMOVE8_F                   = 0x33

opMOVE16_8                  = 0x34
opMOVE16_16                 = 0x35
opMOVE16_32                 = 0x36
opMOVE16_F                  = 0x37

opMOVE32_8                  = 0x38
opMOVE32_16                 = 0x39
opMOVE32_32                 = 0x3A
opMOVE32_F                  = 0x3B

opMOVEF_8                   = 0x3C
opMOVEF_16                  = 0x3D
opMOVEF_32                  = 0x3E
opMOVEF_F                   = 0x3F

opJR                        = 0x40
opJR_FALSE                  = 0x41
opJR_TRUE                   = 0x42
opJR_NAN                    = 0x43

opCP_LT8                    = 0x44
opCP_LT16                   = 0x45
opCP_LT32                   = 0x46
opCP_LTF                    = 0x47

opCP_GT8                    = 0x48
opCP_GT16                   = 0x49
opCP_GT32                   = 0x4A
opCP_GTF                    = 0x4B

opCP_EQ8                    = 0x4C
opCP_EQ16                   = 0x4D
opCP_EQ32                   = 0x4E
opCP_EQF                    = 0x4F

opCP_NEQ8                   = 0x50
opCP_NEQ16                  = 0x51
opCP_NEQ32                  = 0x52
opCP_NEQF                   = 0x53

opCP_LTEQ8                  = 0x54
opCP_LTEQ16                 = 0x55
opCP_LTEQ32                 = 0x56
opCP_LTEQF                  = 0x57

opCP_GTEQ8                  = 0x58
opCP_GTEQ16                 = 0x59
opCP_GTEQ32                 = 0x5A
opCP_GTEQF                  = 0x5B

opSELECT8                   = 0x5C
opSELECT16                  = 0x5D
opSELECT32                  = 0x5E
opSELECTF                   = 0x5F

opSYSTEM                    = 0x60
opPORT_CNV_OUTPUT           = 0x61
opPORT_CNV_INPUT            = 0x62
opNOTE_TO_FREQ              = 0x63

opJR_LT8                    = 0x64
opJR_LT16                   = 0x65
opJR_LT32                   = 0x66
opJR_LTF                    = 0x67

opJR_GT8                    = 0x68
opJR_GT16                   = 0x69
opJR_GT32                   = 0x6A
opJR_GTF                    = 0x6B

opJR_EQ8                    = 0x6C
opJR_EQ16                   = 0x6D
opJR_EQ32                   = 0x6E
opJR_EQF                    = 0x6F

opJR_NEQ8                   = 0x70
opJR_NEQ16                  = 0x71
opJR_NEQ32                  = 0x72
opJR_NEQF                   = 0x73

opJR_LTEQ8                  = 0x74
opJR_LTEQ16                 = 0x75
opJR_LTEQ32                 = 0x76
opJR_LTEQF                  = 0x77

opJR_GTEQ8                  = 0x78
opJR_GTEQ16                 = 0x79
opJR_GTEQ32                 = 0x7A
opJR_GTEQF                  = 0x7B

opINFO                      = 0x7C
opSTRINGS                   = 0x7D
opMEMORY_WRITE              = 0x7E
opMEMORY_READ               = 0x7F

opUI_FLUSH                  = 0x80
opUI_READ                   = 0x81
opUI_WRITE                  = 0x82
opUI_BUTTON                 = 0x83
opUI_DRAW                   = 0x84


opTIMER_WAIT                = 0x85
opTIMER_READY               = 0x86
opTIMER_READ                = 0x87



opBP0                       = 0x88
opBP1                       = 0x89
opBP2                       = 0x8A
opBP3                       = 0x8B
opBP_SET                    = 0x8C
opMATH                      = 0x8D
opRANDOM                    = 0x8E

opTIMER_READ_US             = 0x8F

opKEEP_ALIVE                = 0x90

opCOM_READ                  = 0x91
opCOM_WRITE                 = 0x92

opSOUND                     = 0x94
opSOUND_TEST                = 0x95
opSOUND_READY               = 0x96

opINPUT_SAMPLE              = 0x97

opINPUT_DEVICE_LIST         = 0x98
opINPUT_DEVICE              = 0x99
opINPUT_READ                = 0x9A
opINPUT_TEST                = 0x9B
opINPUT_READY               = 0x9C
opINPUT_READSI              = 0x9D
opINPUT_READEXT             = 0x9E
opINPUT_WRITE               = 0x9F

opOUTPUT_GET_TYPE           = 0xA0
opOUTPUT_SET_TYPE           = 0xA1
opOUTPUT_RESET              = 0xA2
opOUTPUT_STOP               = 0xA3
opOUTPUT_POWER              = 0xA4
opOUTPUT_SPEED              = 0xA5
opOUTPUT_START              = 0xA6
opOUTPUT_POLARITY           = 0xA7
opOUTPUT_READ               = 0xA8
opOUTPUT_TEST               = 0xA9
opOUTPUT_READY              = 0xAA
opOUTPUT_POSITION           = 0xAB
opOUTPUT_STEP_POWER         = 0xAC
opOUTPUT_TIME_POWER         = 0xAD
opOUTPUT_STEP_SPEED         = 0xAE
opOUTPUT_TIME_SPEED         = 0xAF

opOUTPUT_STEP_SYNC          = 0xB0
opOUTPUT_TIME_SYNC          = 0xB1
opOUTPUT_CLR_COUNT          = 0xB2
opOUTPUT_GET_COUNT          = 0xB3

opOUTPUT_PRG_STOP           = 0xB4

opFILE                      = 0xC0
opARRAY                     = 0xC1
opARRAY_WRITE               = 0xC2
opARRAY_READ                = 0xC3
opARRAY_APPEND              = 0xC4
opMEMORY_USAGE              = 0xC5
opFILENAME                  = 0xC6

opREAD8                     = 0xC8
opREAD16                    = 0xC9
opREAD32                    = 0xCA
opREADF                     = 0xCB

opWRITE8                    = 0xCC
opWRITE16                   = 0xCD
opWRITE32                   = 0xCE
opWRITEF                    = 0xCF

opCOM_READY                 = 0xD0
opCOM_READDATA              = 0xD1
opCOM_WRITEDATA             = 0xD2
opCOM_GET                   = 0xD3
opCOM_SET                   = 0xD4
opCOM_TEST                  = 0xD5
opCOM_REMOVE                = 0xD6
opCOM_WRITEFILE             = 0xD7

opMAILBOX_OPEN              = 0xD8
opMAILBOX_WRITE             = 0xD9
opMAILBOX_READ              = 0xDA
opMAILBOX_TEST              = 0xDB
opMAILBOX_READY             = 0xDC
opMAILBOX_CLOSE             = 0xDD

opTST                       = 0xFF

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
