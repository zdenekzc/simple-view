
# http://github.com/mindboards/ev3sources/blob/master/lms2012/lms2012/source/bytecodes.h

# --------------------------------------------------------------------------

# GRAPHICS

vmPOP3_ABS_X                  = 16
vmPOP3_ABS_Y                  = 50

vmPOP3_ABS_WARN_ICON_X        = 64
vmPOP3_ABS_WARN_ICON_X1       = 40
vmPOP3_ABS_WARN_ICON_X2       = 72
vmPOP3_ABS_WARN_ICON_X3       = 104
vmPOP3_ABS_WARN_ICON_Y        = 60
vmPOP3_ABS_WARN_SPEC_ICON_X   = 88
vmPOP3_ABS_WARN_SPEC_ICON_Y   = 60
vmPOP3_ABS_WARN_TEXT_X        = 80
vmPOP3_ABS_WARN_TEXT_Y        = 68
vmPOP3_ABS_WARN_YES_X         = 72
vmPOP3_ABS_WARN_YES_Y         = 90
vmPOP3_ABS_WARN_LINE_X        = 21
vmPOP3_ABS_WARN_LINE_Y        = 89
vmPOP3_ABS_WARN_LINE_ENDX     = 155

# --------------------------------------------------------------------------

# HARDWARE

vmOUTPUTS                     = 4                             # Number of output ports in the system
vmINPUTS                      = 4                             # Number of input  ports in the system
vmBUTTONS                     = 6                             # Number of buttons in the system
vmLEDS                        = 4                             # Number of LEDs in the system

vmLCD_WIDTH                   = 178                           # LCD horizontal pixels
vmLCD_HEIGHT                  = 128                           # LCD vertical pixels
vmTOPLINE_HEIGHT              = 10                            # Top line vertical pixels
vmLCD_STORE_LEVELS            = 3                             # Store levels

vmDEFAULT_VOLUME              = 100
vmDEFAULT_SLEEPMINUTES        = 30

# SOFTWARE

vmFG_COLOR                    = 1                             #  Forground color
vmBG_COLOR                    = 0                             #  Background color

vmCHAIN_DEPT                  = 4                             # Number of bricks in the USB daisy chain (master + slaves)

# FILEPERMISSIONS               = (S_IRUSR | S_IWUSR | S_IRGRP | S_IWGRP | S_IROTH | S_IWOTH)
# DIRPERMISSIONS                = (S_IRWXU | S_IRWXG | S_IRWXO)
# SYSPERMISSIONS                = (S_IRUSR | S_IWUSR | S_IRGRP | S_IROTH)

vmPATHSIZE                    = 84                            # Max path size excluding trailing forward slash including zero termination
vmNAMESIZE                    = 32                            # Max name size including zero termination (must be divideable by 4)
vmEXTSIZE                     = 5                             # Max extension size including dot and zero termination
vmFILENAMESIZE                = 120                           # Max filename size including path, name, extension and termination (must be divideable by 4)
vmMACSIZE                     = 18                            # Max WIFI MAC size including zero termination
vmIPSIZE                      = 16                            # Max WIFI IP size including zero termination
vmBTADRSIZE                   = 13                            # Max bluetooth address size including zero termination

vmERR_STRING_SIZE             = 32                            # Inclusive zero termination

vmEVENT_BT_PIN                = 1
vmEVENT_BT_REQ_CONF           = 2

vmMAX_VALID_TYPE              = 101                           # Highest valid device type

# FOLDERS

vmMEMORY_FOLDER               =  "/mnt/ramdisk"                # Folder for non volatile user programs/data
vmPROGRAM_FOLDER              = "../prjs/BrkProg_SAVE"        # Folder for On Brick Programming programs
vmDATALOG_FOLDER              = "../prjs/BrkDL_SAVE"          # Folder for On Brick Data log files
vmSDCARD_FOLDER               = "../prjs/SD_Card"             # Folder for SD card mount
vmUSBSTICK_FOLDER             = "../prjs/USB_Stick"           # Folder for USB stick mount

vmPRJS_DIR                    = "../prjs"                     # Project folder
vmAPPS_DIR                    = "../apps"                     # Apps folder
vmTOOLS_DIR                   = "../tools"                    # Tools folder
vmTMP_DIR                     = "../tmp"                      # Temporary folder

vmSETTINGS_DIR                = "../sys/settings"             # Folder for non volatile settings

vmDIR_DEEPT                   = 127                           # Max directory items allocated including "." and ".."

# FILES USED IN APPLICATION

vmLASTRUN_FILE_NAME           = "lastrun"                     # Last run filename
vmCALDATA_FILE_NAME           = "caldata"                     # Calibration data filename

# FILES USED IN APPS

vmSLEEP_FILE_NAME             = "Sleep"                       # File used in "Sleep" app to save status
vmVOLUME_FILE_NAME            = "Volume"                      # File used in "Volume" app to save status
vmWIFI_FILE_NAME              = "WiFi"                        # File used in "WiFi" app to save status
vmBLUETOOTH_FILE_NAME         = "Bluetooth"                   # File used in "Bluetooth" app to save status

# EXTENSIONS

vmEXT_SOUND                   = ".rsf"                        # Robot Sound File
vmEXT_GRAPHICS                = ".rgf"                        # Robot Graphics File
vmEXT_BYTECODE                = ".rbf"                        # Robot Byte code File
vmEXT_TEXT                    = ".rtf"                        # Robot Text File
vmEXT_DATALOG                 = ".rdf"                        # Robot Datalog File
vmEXT_PROGRAM                 = ".rpf"                        # Robot Program File
vmEXT_CONFIG                  = ".rcf"                        # Robot Configuration File
vmEXT_ARCHIVE                 = ".raf"                        # Robot Archive File

# NAME LENGTHs

vmBRICKNAMESIZE               = 120                           # Brick name maximal size (including zero termination)
vmBTPASSKEYSIZE               = 7                             # Bluetooth pass key size (including zero termination)
vmWIFIPASSKEYSIZE             = 33                            # WiFi pass key size (including zero termination)

# VALID CHARACTERS

vmCHARSET_NAME                = 0x01                          # Character set allowed in brick name and raw filenames
vmCHARSET_FILENAME            = 0x02                          # Character set allowed in file names
vmCHARSET_BTPASSKEY           = 0x04                          # Character set allowed in bluetooth pass key
vmCHARSET_WIFIPASSKEY         = 0x08                          # Character set allowed in WiFi pass key
vmCHARSET_WIFISSID            = 0x10                          # Character set allowed in WiFi ssid

# --------------------------------------------------------------------------

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
