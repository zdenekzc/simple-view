
# http://github.com/mindboards/ev3sources/blob/master/lms2012/lms2012/source/bytecodes.h

# --------------------------------------------------------------------------

# programid Program ID's (Slots)

GUI_SLOT                      = 0    # Program slot reserved for executing the user interface
USER_SLOT                     = 1    # Program slot used to execute user projects, apps and tools
CMD_SLOT                      = 2    # Program slot used for direct commands coming from c_com
TERM_SLOT                     = 3    # Program slot used for direct commands coming from c_ui
DEBUG_SLOT                    = 4    # Program slot used to run the debug ui

# buttons Button

NO_BUTTON                     = 0
UP_BUTTON                     = 1
ENTER_BUTTON                  = 2
DOWN_BUTTON                   = 3
RIGHT_BUTTON                  = 4
LEFT_BUTTON                   = 5
BACK_BUTTON                   = 6
ANY_BUTTON                    = 7

# --------------------------------------------------------------------------

# browsers Browser Types Avaliable

BROWSE_FOLDERS                = 0    # Browser for folders
BROWSE_FOLDS_FILES            = 1    # Browser for folders and files
BROWSE_CACHE                  = 2    # Browser for cached / recent files
BROWSE_FILES                  = 3    # Browser for files

# fonts Font Types Avaliable

NORMAL_FONT                   = 0
SMALL_FONT                    = 1
LARGE_FONT                    = 2
TINY_FONT                     = 3

# icons Icon Types Avaliable

NORMAL_ICON                   = 0    # "24x12_Files_Folders_Settings.bmp"
SMALL_ICON                    = 1
LARGE_ICON                    = 2    # "24x22_Yes_No_OFF_FILEOps.bmp"
MENU_ICON                     = 3
ARROW_ICON                    = 4    # "8x12_miniArrows.bmp"

SICON_CHARGING                = 0
SICON_BATT_4                  = 1
SICON_BATT_3                  = 2
SICON_BATT_2                  = 3
SICON_BATT_1                  = 4
SICON_BATT_0                  = 5
SICON_WAIT1                   = 6
SICON_WAIT2                   = 7
SICON_BT_ON                   = 8
SICON_BT_VISIBLE              = 9
SICON_BT_CONNECTED            = 10
SICON_BT_CONNVISIB            = 11
SICON_WIFI_3                  = 12
SICON_WIFI_2                  = 13
SICON_WIFI_1                  = 14
SICON_WIFI_CONNECTED          = 15

SICON_USB                     = 21

ICON_NONE                     = -1
ICON_RUN                      = 0
ICON_FOLDER                   = 1
ICON_FOLDER2                  = 2
ICON_USB                      = 3
ICON_SD                       = 4
ICON_SOUND                    = 5
ICON_IMAGE                    = 6
ICON_SETTINGS                 = 7
ICON_ONOFF                    = 8
ICON_SEARCH                   = 9
ICON_WIFI                     = 10
ICON_CONNECTIONS              = 11
ICON_ADD_HIDDEN               = 12
ICON_TRASHBIN                 = 13
ICON_VISIBILITY               = 14
ICON_KEY                      = 15
ICON_CONNECT                  = 16
ICON_DISCONNECT               = 17
ICON_UP                       = 18
ICON_DOWN                     = 19
ICON_WAIT1                    = 20
ICON_WAIT2                    = 21
ICON_BLUETOOTH                = 22
ICON_INFO                     = 23
ICON_TEXT                     = 24


ICON_QUESTIONMARK             = 27
ICON_INFO_FILE                = 28
ICON_DISC                     = 29
ICON_CONNECTED                = 30
ICON_OBP                      = 31
ICON_OBD                      = 32
ICON_OPENFOLDER               = 33
ICON_BRICK1                   = 34


YES_NOTSEL                    = 0
YES_SEL                       = 1
NO_NOTSEL                     = 2
NO_SEL                        = 3
OFF                           = 4
WAIT_VERT                     = 5
WAIT_HORZ                     = 6
TO_MANUAL                     = 7
WARNSIGN                      = 8
WARN_BATT                     = 9
WARN_POWER                    = 10
WARN_TEMP                     = 11
NO_USBSTICK                   = 12
TO_EXECUTE                    = 13
TO_BRICK                      = 14
TO_SDCARD                     = 15
TO_USBSTICK                   = 16
TO_BLUETOOTH                  = 17
TO_WIFI                       = 18
TO_TRASH                      = 19
TO_COPY                       = 20
TO_FILE                       = 21
CHAR_ERROR                    = 22
COPY_ERROR                    = 23
PROGRAM_ERROR                 = 24

WARN_MEMORY                   = 27

ICON_STAR                     = 0
ICON_LOCKSTAR                 = 1
ICON_LOCK                     = 2
ICON_PC                       = 3    # Bluetooth type PC
ICON_PHONE                    = 4    # Bluetooth type PHONE
ICON_BRICK                    = 5    # Bluetooth type BRICK
ICON_UNKNOWN                  = 6    # Bluetooth type UNKNOWN
ICON_FROM_FOLDER              = 7
ICON_CHECKBOX                 = 8
ICON_CHECKED                  = 9
ICON_XED                      = 10

ICON_LEFT                     = 1
ICON_RIGHT                    = 2

# bttypes Bluetooth Device Types

BTTYPE_PC                     = 3    # Bluetooth type PC
BTTYPE_PHONE                  = 4    # Bluetooth type PHONE
BTTYPE_BRICK                  = 5    # Bluetooth type BRICK
BTTYPE_UNKNOWN                = 6    # Bluetooth type UNKNOWN

# ledpatterns LED Pattern

LED_BLACK                     = 0
LED_GREEN                     = 1
LED_RED                       = 2
LED_ORANGE                    = 3
LED_GREEN_FLASH               = 4
LED_RED_FLASH                 = 5
LED_ORANGE_FLASH              = 6
LED_GREEN_PULSE               = 7
LED_RED_PULSE                 = 8
LED_ORANGE_PULSE              = 9

LED_ALL                       = 0        # All LEDs
LED_RR                        = 1        # Right red
LED_RG                        = 2        # Right green
LED_LR                        = 3        # Left red
LED_LG                        = 4        # Left green

# filetypes File Types Avaliable

FILETYPE_UNKNOWN              = 0x00
TYPE_FOLDER                   = 0x01
TYPE_SOUND                    = 0x02
TYPE_BYTECODE                 = 0x03
TYPE_GRAPHICS                 = 0x04
TYPE_DATALOG                  = 0x05
TYPE_PROGRAM                  = 0x06
TYPE_TEXT                     = 0x07
TYPE_SDCARD                   = 0x10
TYPE_USBSTICK                 = 0x20

TYPE_RESTART_BROWSER          = -1
TYPE_REFRESH_BROWSER          = -2

# --------------------------------------------------------------------------

# delimiters

DEL_NONE      = 0                    # No delimiter at all
DEL_TAB       = 1                    # Use tab as delimiter
DEL_SPACE     = 2                    # Use space as delimiter
DEL_RETURN    = 3                    # Use return as delimiter
DEL_COLON     = 4                    # Use colon as delimiter
DEL_COMMA     = 5                    # Use comma as delimiter
DEL_LINEFEED  = 6                    # Use line feed as delimiter
DEL_CRLF      = 7                    # Use return+line feed as delimiter

# transportlayers Hardware Transport Layer

HW_USB        = 1
HW_BT         = 2
HW_WIFI       = 3

# encryptions Encryption Types

ENCRYPT_NONE  = 0
ENCRYPT_WPA2  = 1

MODE_KEEP     = -1
TYPE_KEEP     =  0

RED           =  0
GREEN         =  1
BLUE          =  2
BLANK         =  3


# Constants related to color sensor value using
# Color sensor as color detector

BLACKCOLOR   = 1
BLUECOLOR    = 2
GREENCOLOR   = 3
YELLOWCOLOR  = 4
REDCOLOR     = 5
WHITECOLOR   = 6

WARNING_TEMP      = 0x01
WARNING_CURRENT   = 0x02
WARNING_VOLTAGE   = 0x04
WARNING_MEMORY    = 0x08
WARNING_DSPSTAT   = 0x10

WARNING_BATTLOW   = 0x40
WARNING_BUSY      = 0x80

# --------------------------------------------------------------------------

# results

OK            = 0                    # No errors to report
BUSY          = 1                    # Busy - try again
FAIL          = 2                    # Something failed
STOP          = 4                    # Stopped

# Values used to describe an object's status

RUNNING = 0x0010                     # Object code is running
WAITING = 0x0020                     # Object is waiting for final trigger
STOPPED = 0x0040                     # Object is stopped or not triggered yet
HALTED  = 0x0080                     # Object is halted because a call is in progress

# Device commands used to control (UART sensors) devices

DEVCMD_RESET        = 0x11           # UART device reset
DEVCMD_FIRE         = 0x11           # UART device fire   (ultrasonic)
DEVCMD_CHANNEL      = 0x12           # UART device channel (IR seeker)

# --------------------------------------------------------------------------

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all

