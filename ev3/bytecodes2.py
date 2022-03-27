
# https://github.com/mindboards/ev3sources/blob/master/lms2012/lms2012/source/bytecodes.h

# --------------------------------------------------------------------------

# uireadsubcode Specific command parameter

GET_VBATT     = 1
GET_IBATT     = 2
GET_OS_VERS   = 3
GET_EVENT     = 4
GET_TBATT     = 5
GET_IINT      = 6
GET_IMOTOR    = 7
GET_STRING    = 8
GET_HW_VERS   = 9
GET_FW_VERS   = 10
GET_FW_BUILD  = 11
GET_OS_BUILD  = 12
GET_ADDRESS   = 13
GET_CODE      = 14
KEY           = 15
GET_SHUTDOWN  = 16
GET_WARNING   = 17
GET_LBATT     = 18
TEXTBOX_READ  = 21
GET_VERSION   = 26
GET_IP        = 27
GET_POWER     = 29
GET_SDCARD    = 30
GET_USBSTICK  = 31


# uiwritesubcode Specific command parameter

WRITE_FLUSH   = 1
FLOATVALUE    = 2
STAMP         = 3
PUT_STRING    = 8
VALUE8        = 9
VALUE16       = 10
VALUE32       = 11
VALUEF        = 12
ADDRESS       = 13
CODE          = 14
DOWNLOAD_END  = 15
SCREEN_BLOCK  = 16
TEXTBOX_APPEND = 21
SET_BUSY      = 22
SET_TESTPIN   = 24
INIT_RUN      = 25
UPDATE_RUN    = 26
LED           = 27
POWER         = 29
GRAPH_SAMPLE  = 30
TERMINAL      = 31

# uibuttonsubcode Specific command parameter

SHORTPRESS      = 1
LONGPRESS       = 2
WAIT_FOR_PRESS  = 3
FLUSH           = 4
PRESS           = 5
RELEASE         = 6
GET_HORZ        = 7
GET_VERT        = 8
PRESSED         = 9
SET_BACK_BLOCK  = 10
GET_BACK_BLOCK  = 11
TESTSHORTPRESS  = 12
TESTLONGPRESS   = 13
GET_BUMBED      = 14
GET_CLICK       = 15

# comreadsubcode Specific command parameter

COMMAND       = 14

# comwritesubcode Specific command parameter

REPLY         = 14

# comgetsubcode Specific command parameter

GET_ON_OFF    = 1                    # Set, Get
GET_VISIBLE   = 2                    # Set, Get
GET_RESULT    = 4                    #      Get
GET_PIN       = 5                    # Set, Get
SEARCH_ITEMS  = 8                    #      Get
SEARCH_ITEM   = 9                    #      Get
FAVOUR_ITEMS  = 10                   #      Get
FAVOUR_ITEM   = 11                   #      Get
GET_ID        = 12
GET_BRICKNAME = 13
GET_NETWORK   = 14
GET_PRESENT   = 15
GET_ENCRYPT   = 16
CONNEC_ITEMS  = 17
CONNEC_ITEM   = 18
GET_INCOMING  = 19
GET_MODE2     = 20

# comsetsubcode Specific command parameter

SET_ON_OFF    = 1                    # Set, Get
SET_VISIBLE   = 2                    # Set, Get
SET_SEARCH    = 3                    # Set
SET_PIN       = 5                    # Set, Get
SET_PASSKEY   = 6                    # Set
SET_CONNECTION = 7                    # Set
SET_BRICKNAME = 8
SET_MOVEUP    = 9
SET_MOVEDOWN  = 10
SET_ENCRYPT   = 11
SET_SSID      = 12
SET_MODE2     = 13

# inputdevicesubcode Specific command parameter

GET_FORMAT      = 2
CAL_MINMAX      = 3
CAL_DEFAULT     = 4
GET_TYPEMODE    = 5
GET_SYMBOL      = 6
CAL_MIN         = 7
CAL_MAX         = 8
SETUP           = 9
CLR_ALL         = 10
GET_RAW         = 11
GET_CONNECTION  = 12
STOP_ALL        = 13
GET_NAME        = 21
GET_MODENAME    = 22
SET_RAW         = 23
GET_FIGURES     = 24
GET_CHANGES     = 25
CLR_CHANGES     = 26
READY_PCT       = 27
READY_RAW       = 28
READY_SI        = 29
GET_MINMAX      = 30
GET_BUMPS       = 31

# programinfosubcode Specific command parameter

OBJ_STOP      = 0    # VM
OBJ_START     = 4    # VM
GET_STATUS    = 22   # VM
GET_SPEED     = 23   # VM
GET_PRGRESULT = 24   # VM
SET_INSTR     = 25   # VM

# uidrawsubcode Specific command parameter

UPDATE        = 0
CLEAN         = 1
PIXEL         = 2
LINE          = 3
CIRCLE        = 4
TEXT          = 5
ICON          = 6
PICTURE       = 7
VALUE         = 8
FILLRECT      = 9
RECT          = 10
NOTIFICATION  = 11
QUESTION      = 12
KEYBOARD      = 13
BROWSE        = 14
VERTBAR       = 15
INVERSERECT   = 16
SELECT_FONT   = 17
TOPLINE       = 18
FILLWINDOW    = 19
SCROLL        = 20
DOTLINE       = 21
VIEW_VALUE    = 22
VIEW_UNIT     = 23
FILLCIRCLE    = 24
STORE         = 25
RESTORE       = 26
ICON_QUESTION = 27
BMPFILE       = 28
POPUP         = 29
GRAPH_SETUP   = 30
GRAPH_DRAW    = 31
TEXTBOX       = 32

# memoryfilesubcode Specific command parameter

OPEN_APPEND         = 0
OPEN_READ           = 1
OPEN_WRITE          = 2
READ_VALUE          = 3
WRITE_VALUE         = 4
READ_TEXT           = 5
WRITE_TEXT          = 6
CLOSE               = 7
LOAD_IMAGE          = 8
GET_HANDLE          = 9
MAKE_FOLDER         = 10
GET_POOL            = 11
SET_LOG_SYNC_TIME   = 12
GET_FOLDERS         = 13
GET_LOG_SYNC_TIME   = 14
GET_SUBFOLDER_NAME  = 15
WRITE_LOG           = 16
CLOSE_LOG           = 17
GET_IMAGE           = 18
GET_ITEM            = 19
GET_CACHE_FILES     = 20
PUT_CACHE_FILE      = 21
GET_CACHE_FILE      = 22
DEL_CACHE_FILE      = 23
DEL_SUBFOLDER       = 24
GET_LOG_NAME        = 25

OPEN_LOG            = 27
READ_BYTES          = 28
WRITE_BYTES         = 29
REMOVE              = 30
MOVE                = 31

# memoryarraysubcode Specific command parameter

DELETE              = 0
CREATE8             = 1
CREATE16            = 2
CREATE32            = 3
CREATEF             = 4
RESIZE              = 5
FILL                = 6
COPY                = 7
INIT8               = 8
INIT16              = 9
INIT32              = 10
INITF               = 11
SIZE                = 12
READ_CONTENT        = 13
WRITE_CONTENT       = 14
READ_SIZE           = 15

# memoryfilenamesubcode Specific command parameter

EXIST               = 16     # MUST BE GREATER OR EQUAL TO "ARRAY_SUBCODES"
TOTALSIZE           = 17
SPLIT               = 18
MERGE               = 19
CHECK               = 20
PACK                = 21
UNPACK              = 22
GET_FOLDERNAME      = 23

# infosubcode Specific command parameter

SET_ERROR           = 1
GET_ERROR           = 2
ERRORTEXT           = 3

GET_VOLUME          = 4
SET_VOLUME          = 5
GET_MINUTES         = 6
SET_MINUTES         = 7

# soundsubcode Specific command parameter

BREAK               = 0
TONE                = 1
PLAY                = 2
REPEAT              = 3
SERVICE             = 4

# stringsubcode Specific command parameter

GET_SIZE            = 1    # VM       get string size
ADD                 = 2    # VM       add two strings
COMPARE             = 3    # VM       compare two strings
DUPLICATE           = 5    # VM       duplicate one string to another
VALUE_TO_STRING     = 6
STRING_TO_VALUE     = 7
STRIP               = 8
NUMBER_TO_STRING    = 9
SUB                 = 10
VALUE_FORMATTED     = 11
NUMBER_FORMATTED    = 12

# mathsubcode Specific command parameter

EXP                           = 1    # e^x            r = expf(x)
MOD                           = 2    # Modulo         r = fmod(xy)
FLOOR                         = 3    # Floor          r = floor(x)
CEIL                          = 4    # Ceiling        r = ceil(x)
ROUND                         = 5    # Round          r = round(x)
ABS                           = 6    # Absolute       r = fabs(x)
NEGATE                        = 7    # Negate         r = 0.0 - x
SQRT                          = 8    # Squareroot     r = sqrt(x)
LOG                           = 9    # Log            r = log10(x)
LN                            = 10   # Ln             r = log(x)
SIN                           = 11   #
COS                           = 12   #
TAN                           = 13   #
ASIN                          = 14   #
ACOS                          = 15   #
ATAN                          = 16   #
MOD8                          = 17   # Modulo DATA8   r = x % y
MOD16                         = 18   # Modulo DATA16  r = x % y
MOD32                         = 19   # Modulo DATA32  r = x % y
POW                           = 20   # Exponent       r = powf(x,y)
TRUNC                         = 21   # Truncate       r = (float)((int)(x * pow(y))) / pow(y)

# tstsubcode Specific command parameter

TST_OPEN                      = 10   # MUST BE GREATER OR EQUAL TO "INFO_SUBCODES"
TST_CLOSE                     = 11
TST_READ_PINS                 = 12
TST_WRITE_PINS                = 13
TST_READ_ADC                  = 14
TST_WRITE_UART                = 15
TST_READ_UART                 = 16
TST_ENABLE_UART               = 17
TST_DISABLE_UART              = 18
TST_ACCU_SWITCH               = 19
TST_BOOT_MODE2                = 20
TST_POLL_MODE2                = 21
TST_CLOSE_MODE2               = 22
TST_RAM_CHECK                 = 23

# --------------------------------------------------------------------------

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
