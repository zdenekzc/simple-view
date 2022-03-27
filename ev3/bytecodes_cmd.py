
# https://github.com/mindboards/ev3sources/blob/master/lms2012/c_com/source/c_com.h

# --------------------------------------------------------------------------

# System Commands
# Byte 4:     Command type

SYSTEM_COMMAND_REPLY    = 0x01    #  System command, reply required
SYSTEM_COMMAND_NO_REPLY = 0x81    #  System command, reply not required

# Byte 5:     System Command

BEGIN_DOWNLOAD          = 0x92    #  Begin file down load
CONTINUE_DOWNLOAD       = 0x93    #  Continue file down load
BEGIN_UPLOAD            = 0x94    #  Begin file upload
CONTINUE_UPLOAD         = 0x95    #  Continue file upload
BEGIN_GETFILE           = 0x96    #  Begin get bytes from a file (while writing to the file)
CONTINUE_GETFILE        = 0x97    #  Continue get byte from a file (while writing to the file)
CLOSE_FILEHANDLE        = 0x98    #  Close file handle
LIST_FILES              = 0x99    #  List files
CONTINUE_LIST_FILES     = 0x9A    #  Continue list files
CREATE_DIR              = 0x9B    #  Create directory
DELETE_FILE             = 0x9C    #  Delete
LIST_OPEN_HANDLES       = 0x9D    #  List handles
WRITEMAILBOX            = 0x9E    #  Write to mailbox
BLUETOOTHPIN            = 0x9F    #  Transfer trusted pin code to brick
ENTERFWUPDATE           = 0xA0    #  Restart the brick in Firmware update mode
SETBUNDLEID             = 0xA1    #  Set Bundle ID for mode 2
SETBUNDLESEEDID         = 0xA2    #  Set bundle seed ID for mode 2

# --------------------------------------------------------------------------

# System Command Response Bytes

# Byte 4:     Reply type

SYSTEM_REPLY            = 0x03    #  System command reply
SYSTEM_REPLY_ERROR      = 0x05    #  System command reply error

# Byte 5:     System command this is the response to
# Byte 6:     Reply status

SUCCESS                 = 0x00
UNKNOWN_HANDLE          = 0x01
HANDLE_NOT_READY        = 0x02
CORRUPT_FILE            = 0x03
NO_HANDLES_AVAILABLE    = 0x04
NO_PERMISSION           = 0x05
ILLEGAL_PATH            = 0x06
FILE_EXITS              = 0x07
END_OF_FILE             = 0x08
SIZE_ERROR              = 0x09
UNKNOWN_ERROR           = 0x0A
ILLEGAL_FILENAME        = 0x0B
ILLEGAL_CONNECTION      = 0x0C

# --------------------------------------------------------------------------

# Direct Command Bytes
# Byte 4:     Command type

DIRECT_COMMAND_REPLY = 0x00
DIRECT_COMMAND_NO_REPLY = 0x80

# Direct Command Response Bytes:
# Byte 4:     Reply type

DIRECT_REPLY = 0x02
DIRECT_REPLY_ERROR = 0x04

# --------------------------------------------------------------------------

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
