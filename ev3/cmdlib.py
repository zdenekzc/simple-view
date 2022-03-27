#!/usr/bin/env python

from __future__ import print_function

import os, sys, re, time, struct

from bytecodes import *
from bytecodes2 import *
from bytecodes3 import *
from bytecodes_par import *
from bytecodes_cmd import *
from encode import miniProgram, microProgram

# --------------------------------------------------------------------------

ID_VENDOR_LEGO = 0x0694
ID_PRODUCT_EV3 = 0x0005

INTERFACE = 0

EP_IN = 0x81
EP_OUT = 0x01

TIMEOUT = 1000 # 1000 ... 1 second

# --------------------------------------------------------------------------

use_bluetooth = False
use_hidapi = False
use_pywinusb = False
use_pyusb = not use_bluetooth and not use_hidapi and not use_pywinusb

# if int (use_bluetooth) + int (use_hidapi) + int (use_pywinusb) + int (use_pyusb) != 1 :
#    sys.exit ("Select one communication library")

if int (use_bluetooth) + int (use_hidapi) + int (use_pywinusb) > 1 :
   sys.exit ("Select only one communication library")

# --------------------------------------------------------------------------

bluetooth_name = "EV3"
bluetooth_address = ""
# bluetooth_address = "00:16:53:40:54:02"

# --------------------------------------------------------------------------

if use_bluetooth :
   import bluetooth

if use_hidapi :
   # subdirectory hidapi :
   #    hidapi.dll ( http://www.signal11.us/oss/hidapi/ , hidapi-0.7.0.zip )
   #               ( or from MonoBrick Test Project, http://www.monobrick.dk/ )
   #    hidapi.py  ( https://github.com/NF6X/pyhidapi )
   #   __init__.py
   os.environ['PATH'] = os.path.join (os.getcwd(), "hidapi") + os.pathsep + os.environ['PATH']
   sys.path.insert (1, os.path.join (os.getcwd (), "hidapi"))
   import hidapi

if use_pywinusb :
   # subdirectory pywinusb :
   #    pywinusb subdirectory ( https://github.com/rene-aguirre/pywinusb , pywinusb-0.4.0.zip  )
   #       hid subdirectory
   sys.path.insert (1, os.path.join (os.getcwd (), "pywinusb"))
   from pywinusb import hid
   import threading

if use_pyusb :
   # subdirectory pyusb
   #    usb subdirectory
   #    libusb.dll  ( http://libusb.info/ , libusb-1.0.20.7z )
   #    or libusb0.dll  ( http://sourceforge.net/p/libusb-win32/wiki/Home/ , libusb-win32-bin-1.2.6.0.zip )
   os.environ['PATH'] = os.path.join (os.getcwd(), "pyusb") + os.pathsep + os.environ['PATH']
   sys.path.insert (1, os.path.join (os.getcwd (), "pyusb")) # directory with usb subdirectory
   # Fedora 21 needs pyusb from Fedora 22 or 23 (in pyusb/usb subdirectory)

   try :
      import usb
   except :
      print ("import usb failed")
      use_pyusb = False

# --------------------------------------------------------------------------

# Fedora 21: use_pyusb
# ( yum install pyusb - original pyusb from Fedora 21 is sufficient )
# ( pyusb from Fedora 22 - better - place into pyusb/usb subdirecory )

# Fedora 21: alternatively use_hidapi
# yum install hidapi-devel
# place hidapi.py into hidapi subdirectory ( https://github.com/NF6X/pyhidapi )

# python cmdlib.py (sometimes second call is succesfull)
# sudo python cmdlib.py or install /etc/udev/rules.d/99-ev3.rules

# Fedora 21: use_bluetooth
# yum install pybluez
# EV3: enable bluetooth, remove old bluetooth connection
# PC:  run ./simple-agent to enter pin
#      (from bluez-5.23/test in bluez-5.23 source RPM package
#      (and bluezutils.py from same direcory)


# --------------------------------------------------------------------------

# Windows : use_hidapi = True or use_pywinusb = True
# no .inf is required

# hidapi.dll from EV3 Software or from MonoBrick Test Project, http://www.monobrick.dk/
# check if EV3 Software is disconnected and MonoBrick Test Project is not running

# --------------------------------------------------------------------------

# Windows : use_pyusb = True, use_device = False ( <-- important )

# .inf is required
# EV3 Software or MonoBrick Test Project cannot communicate with EV3 until .inf is removed

# libusb version 0.1
# http://www.libusb.org/wiki/libusb-win32
# http://sourceforge.net/projects/libusb-win32
# libusb-win32-bin-1.2.6.0.zip
# libusb-win32-devel-filter-1.2.6.0.exe
# install libusb-win32-devel-filter-1.2.6.0.exe, run inf-wizard.exe or install-filter-win.exe

# libusb version 1.0
# http://libusb.info/
# libusb-1.0.20.7z
# libusb-1.0.dll

# information: USBdeview (deview.exe) ( http://www.nirsoft.net/utils/usb_devices_view.html )
# driver installation: zadig ( http://zadig.akeo.ie/ )
# uninstall: pnputil ( MS Windows )

# --------------------------------------------------------------------------

if 0 :
   for p in sys.path : print (p)
   print

if 0 :
   for p in os.environ['PATH'].split (os.pathsep) : print (p)
   print

if 0 :
   if use_bluetooth :
      print ("performing inquiry...")
      # devices = bluetooth.discover_devices (duration=1, lookup_names=True, flush_cache=True, lookup_class=False)
      devices = bluetooth.discover_devices (duration=1, lookup_names=True, flush_cache=True)
      print ("found %d devices" % len (devices))
      for addr, name in devices :
         print ("  %s - %s" % (addr, name))
      # services = bluetooth.find_service ()
      # print ("found %d services" % len (services))
      # for service in services :
      #    for key, value in service.iteritems () :
      #       print (key, "=", value)
   if use_hidapi :
      hidapi.hid_init ()
      for d in hidapi.hid_enumerate () :
        print (d.description ())
   if use_pywinusb :
      hid.core.show_hids ()
   if use_pyusb :
      devices = usb.core.find (find_all=True)
      for d in devices :
          print (unicode (d).encode ("ascii", "replace"))

# --------------------------------------------------------------------------

device = None
message_count = 0

software_version = 0

trace = False
trace2 = False

windows = (sys.platform == "win32")

# --------------------------------------------------------------------------

if use_pywinusb :
   report = None

if use_pyusb and not use_device :
   ep_in = None
   ep_out = None

# --------------------------------------------------------------------------

if use_pywinusb :
   pywinusb_data = [ ]
   pywinusb_lock = threading.Lock ()

   def pywinusb_handler (data) :
       global pywinusb_data, pywinusb_lock
       # print("Raw data: {0}".format(data))
       # print("Raw data received", len (data))
       pywinusb_lock.acquire ()
       pywinusb_data.append (data)
       pywinusb_lock.release ()

   def pywinusb_read () :
       global pywinusb_data, pywinusb_lock
       ok = False
       while not ok :
          pywinusb_lock.acquire ()
          if len (pywinusb_data) != 0 :
             data = pywinusb_data [0]
             del pywinusb_data [0]
             ok = True
          pywinusb_lock.release ()
       return data

# --------------------------------------------------------------------------

def connectToEV3 () :
    global device

    if use_bluetooth :
       global bluetooth_name, bluetooth_address
       port = 1

       if bluetooth_address == "" :
          devices = bluetooth.discover_devices (duration=1, lookup_names=True, flush_cache=True, lookup_class=False)
          for addr, name in devices :
             if name == bluetooth_name :
                bluetooth_address = addr

       device = bluetooth.BluetoothSocket (bluetooth.RFCOMM)
       device.connect ((bluetooth_address, port))
       print ("Lego EV3 brick found")

    elif use_hidapi :
       hidapi.hid_init ()
       device = hidapi.hid_open (ID_VENDOR_LEGO, ID_PRODUCT_EV3)
       if device == None :
          sys.exit ("No Lego EV3 found")
       print ("Lego EV3 brick found")
       hidapi.hid_set_nonblocking (device,0)

    elif use_pywinusb :
       filter = hid.HidDeviceFilter (vendor_id = ID_VENDOR_LEGO, product_id = ID_PRODUCT_EV3)
       hid_device = filter.get_devices ()
       device = hid_device[0]
       device.open ()
       # print (hid_device)

       target_usage = hid.get_full_usage_id (0x00, 0x3f)
       device.set_raw_data_handler (pywinusb_handler)
       # print (target_usage)

       global report
       report = device.find_output_reports()
       # print (report)
       # print (report[0])

    elif use_pyusb :
       device = usb.core.find (idVendor=ID_VENDOR_LEGO, idProduct=ID_PRODUCT_EV3)

       if device is None:
          sys.exit ("No Lego EV3 found")

       print ("Lego EV3 brick found")
       if not windows :
          if device.is_kernel_driver_active (INTERFACE) :
             print ("Linux Kernel driver attached, need to detach it first")
             device.detach_kernel_driver (INTERFACE)

       # print ("claiming device")

       if use_device :
          device.set_configuration ()
          # usb.util.claim_interface (device, INTERFACE)

       else :
          cfg = device [0] # first configuration
          if 0 :
             print ("cfg", cfg)

          intf = cfg [(0,0)] # first interface, first alternative
          if 0 :
             print ("intf", intf)

          global ep_in, ep_out
          ep_in = intf [0] # second endpoint
          ep_out = intf [1] # second endpoint
          if 0 :
             print ("ep_in", ep_in)
             print ("ep_out", ep_out)

    else :
       sys.exit ("No Lego EV3 found")

    # Hack. Clean up the USB buffer, but why?
    if use_pyusb :
       clean_buffer ()

    if 0 :
       version = getVersion ()
       m = re.match ("LMS2012 V(\d)\.(\d)(\d)", getVersion ())
       if m != None :
          global software_version
          software_version = int (m.group(1) + m.group(2) + m.group(3))
          # print ("SOFTWARE_VERSION", software_version)
          # https://github.com/mindboards/ev3sources/blob/master/lms2012/lms2012/doc/Implementation

# --------------------------------------------------------------------------

def write_message (message) :
    global device, message_count
    message = WordToBytes (message_count) + message
    message = WordToBytes (len (message)) + message
    if trace :
       printChars ("write_message:", message)
    if use_bluetooth :
       device.send (message)
    elif use_hidapi :
       data = [ ]
       length = len (message)
       if windows :
          data.append (byte (0)) # report id
       for c in message :
          data.append (c)
       hidapi.hid_write (device, data)
    elif use_pywinusb :
       global report
       data = [ 0 ] # report id
       for c in message :
          data.append (ord (c))
       while len (data) < 1025 :
          data.append (0)
       # report[0].set_raw_data (data)
       # report[0].send ()
       report[0].send (data)
    elif use_pyusb :
       if use_device :
          device.write (EP_OUT, message, TIMEOUT)
       else :
          global ep_out
          ep_out.write (message, TIMEOUT)
    message_count = message_count + 1

# --------------------------------------------------------------------------

def variables (local_vars, global_vars) :
    local_vars = local_vars & 0x3F
    global_vars = global_vars & 0x03FF
    # print (local_vars, global_vars, format (local_vars << 10 | global_vars, '04x'))
    return WordToBytes (local_vars << 10 | global_vars);

def write_direct_command (message, local_vars = 32, global_vars = 32) :
    write_message (byte (DIRECT_COMMAND_NO_REPLY) + variables (local_vars, global_vars) + message)

def write_direct_command_reply (message, local_vars = 32, global_vars = 32) :
    write_message (byte (DIRECT_COMMAND_REPLY) + variables (local_vars, global_vars) + message)

def write_system_command (message) :
    write_message (byte (SYSTEM_COMMAND_NO_REPLY) + message)

def write_system_command_reply (message) :
    write_message (byte (SYSTEM_COMMAND_REPLY) + message)

# --------------------------------------------------------------------------

def read_reply (size = 1024) :
    global device
    # try :
    if use_bluetooth :
        char_data = device.recv (size)
        data = [ord (c) for c in char_data]
    elif use_hidapi :
        data = hidapi.hid_read_timeout (device, size, TIMEOUT)
    elif use_pywinusb :
        data = pywinusb_read ()
        data = data [1:] # skip report id
    elif use_pyusb :
        if use_device :
           data = device.read (EP_IN, size, TIMEOUT)
        else :
           global ep_in
           data = ep_in.read (size, TIMEOUT)
    # except usb.core.USBError as e:
    #   print (e)
    #   data = None
    if trace :
       printBytes ("reply:", data)
    return data

def repeat_read_reply (size = 1024) :
    ok = False
    while not ok :
       try :
          data = read_reply (size)
          ok = True
       except usb.core.USBError as e:
          pass
    if trace :
       printBytes ("reply:", data)
    return data

def clean_buffer () :
    timeout = 100 # 0.1 s
    size = 1024
    try :
        if use_pyusb :
            if use_device :
               data = device.read (EP_IN, size, timeout)
            else :
               global ep_in
               data = ep_in.read (size, timeout)
    except usb.core.USBError as e:
       pass

# --------------------------------------------------------------------------

def direct_command_reply_OK (data) :
    status = data [4]
    return status == DIRECT_REPLY

def check_direct_command_reply (data) :
    if not direct_command_reply_OK (data) :
       raise IOError ("Direct command reply error")

# --------------------------------------------------------------------------

def system_command_reply_OK (data) :
    reply_type = data [4]
    return reply_type == SYSTEM_REPLY

def check_system_command_reply (data) :
    if not system_command_reply_OK (data) :
       raise IOError ("System command reply error")

# --------------------------------------------------------------------------

def printChars (text, data, short = False) :
    n = 0

    length = len (data)
    last = length - 1
    if short :
       while last >= 0 and ord (data [last]) == 0 :
          last = last - 1

    print (text, end=' ')
    for c in data :
        if n == last:
           break
        print (format (ord (c), "02x"), end=' ')
        n = n + 1
        if n % 16 == 0 and n < length:
           print ()
    print ()

def printBytes (text, data, short = False) :
    print (text, end=' ')

    length = len (data)
    last = length - 1
    if short :
       while last >= 0 and data [last] == 0 :
          last = last - 1

    n = 0
    for c in data :
        if n == last:
           break
        print (format (c, "02x"), end=' ')
        n = n + 1
        if n % 16 == 0 and n < length:
           print ()
    print ()

def printData (data) :
    n = 0
    for v in data :
       print (format (v, '02x'), end=' ')
       n = n + 1
       if n % 16 == 0 :
          print ()
       elif n % 4 == 0 :
          print ("|", end=' ')
    print ()

def printAscii (data) :
    n = 0
    for v in data :
       if v >= 32 and v <= 127 :
          print ( chr (v), " ", end=' ')
       else :
          print (format (v, '02x'), end=' ')
       n = n + 1
       if n % 16 == 0 :
          print ()
       # elif n % 4 == 0 :
       #    print ("|", end=' ')
    print ()

# --------------------------------------------------------------------------

def print_direct_command_reply (data) :
    size = data [0] | data [1] << 8
    counter = data [2] | data [3] << 8
    status = data [4]
    if status == DIRECT_REPLY :
       status = "O.K."
    elif status == DIRECT_REPLY_ERROR :
       status = "ERROR"
    else :
       status = format (status, '02x')
    print ("direct command reply:", end=' ')
    print ("size =", size, end=' ')
    print ("message number =", counter, end=' ')
    print ("status =", status, end=' ')
    data = data [0:size+2]
    print ()
    printData (data [5:])

def print_system_command_reply (data) :
    size = data [0] | data [1] << 8
    counter = data [2] | data [3] << 8
    reply_type = data [4]
    command = data [5]
    status = data [6]

    status_name = (
       "SUCCESS",
       "UNKNOWN_HANDLE",
       "HANDLE_NOT_READY",
       "CORRUPT_FILE",
       "NO_HANDLES_AVAILABLE",
       "NO_PERMISSION",
       "ILLEGAL_PATH",
       "FILE_EXITS",
       "END_OF_FILE",
       "SIZE_ERROR",
       "UNKNOWN_ERROR",
       "ILLEGAL_FILENAME",
       "ILLEGAL_CONNECTION")

    print ("system command reply:", end=' ')
    print ("size =", size, end=' ')
    print ("message number =", counter, end=' ')
    print ("reply type =", format (reply_type, '02x'), end=' ')
    print ("command =", format (command, '02x'), end=' ')
    print ("status =", format (status, '02x'), status_name [status])

    data = data [0:size]
    printData (data [7:])

# --------------------------------------------------------------------------

def replyAsString (data) :
    size = data [0] | data [1] << 8
    counter = data [2] | data [3] << 8
    status = data [4]
    txt = ""
    if status == DIRECT_REPLY :
       data = data [0:2+size]
       for c in data [5:] :
          if c == 0 :
             break
          txt = txt + chr (c)
    return txt

def replyAsList (data) :
    size = data [0] | data [1] << 8
    counter = data [2] | data [3] << 8
    status = data [4]
    if status == DIRECT_REPLY :
       data = data [0:2+size]
       return data [5:]
    else :
       data = ( )
       return data

# --------------------------------------------------------------------------

def dataAsNumber (data) :
    return data[0] + (data[1] << 8) + (data[2] << 16) + (data[3] << 24)

def dataAsFloat (data) :
    b = chr (data [0]) + chr (data [1]) + chr (data [2]) + chr (data [3])
    return struct.unpack ('<f', b)[0]

def dataAsString (data) :
    s = ""
    length = data [0]
    i = 1
    while i < len (data) :
       if i == length :
          break
       if data [i] == 0 :
          break
       s = s + chr (data [i])
       i = i + 1
    return s

# --------------------------------------------------------------------------

def OnFwd (motors, power) :
    layer = 0
    message = ( byte (opOUTPUT_POWER) + byte (layer) + byte (motors) + byte (power) +
                byte (opOUTPUT_START) + byte (layer) + byte (motors) )
    write_direct_command (message)

def Off (motors) :
    layer = 0
    brake = 0
    message = byte (opOUTPUT_STOP) + byte (layer) + byte (motors) + byte (brake)
    write_direct_command (message)

# --------------------------------------------------------------------------

def brickName () :

    answer_size = 80
    message = ( byte (opCOM_GET) + byte (GET_BRICKNAME) + LC0(answer_size) + GV0(0) )
    # LC0(n) String length
    # GV0(0) Global variable for response

    write_direct_command_reply (message, local_vars = 0, global_vars = answer_size)

    data = read_reply ()
    check_direct_command_reply (data)
    return replyAsString (data)

# http://github.com/esteve/python-ev3/blob/master/get_brickname.py

# http://matlab-toolboxes-robotics-vision.googlecode.com/svn/matlab/robot/trunk/interfaces/EV3/Brick.m
# http://matlab-toolboxes-robotics-vision.googlecode.com/svn/matlab/robot/trunk/interfaces/EV3/Command.m

# http://ev3.fantastic.computer/doxygen/directcommands.html
# http://github.com/mindboards/ev3sources/blob/master/lms2012/c_com/source/c_com.h

def getVersion () :

    answer_size = 40
    message = ( byte (opUI_READ) + LC0(GET_VERSION) + LC(answer_size) + GV0(0) )
    # LC0(n) String length
    # GV0(0) Global variable for response

    write_direct_command_reply (message, local_vars = 0, global_vars = answer_size)

    data = read_reply ()
    check_direct_command_reply (data)
    return replyAsString (data)

def batteryInfo () :
    message = ( byte (opUI_READ) + LC0(GET_VBATT) + GV0(0) +
                byte (opUI_READ) + LC0(GET_IBATT) + GV0(4) +
                byte (opUI_READ) + LC0(GET_LBATT) + GV0(8) )
    local_vars = 0
    global_vars = 9
    write_direct_command_reply (message, local_vars, global_vars)

    data = read_reply ()
    check_direct_command_reply (data)
    data = replyAsList (data)

    vbatt = dataAsFloat (data [0:4])
    ibatt = dataAsFloat (data [4:8])
    lbatt = data [8]
    return (vbatt, ibatt, lbatt)

# --------------------------------------------------------------------------

def sensorName (sensor, typ = 0, mode = -1) :

    # opINPUT_DEVICE (CMD, .....)

    # CMD = GET_NAME
    # Get device name

    # param  (DATA8)   LAYER        - Chain layer number [0..3]
    # param  (DATA8)   NO           - Port number
    # param  (DATA8)   LENGTH       - Maximal length of string returned (-1 = no check)

    # return (DATA8)   DESTINATION  - String variable or handle to string

    layer = 0
    answer_size = 16
    message = ( byte (opINPUT_DEVICE) + byte (GET_NAME) +
                LC0 (layer) + LC0 (sensor) + LC (answer_size) + GV0(0) )

    write_direct_command_reply (message, local_vars = 0, global_vars = answer_size)

    data = read_reply ()
    check_direct_command_reply (data)

    return replyAsString (data)

def readSensor (sensor, typ = 0, mode = -1) :

    # opINPUT_READ (LAYER, NO, TYPE, MODE, PCT)

    # Read device value in Percent
    # Dispatch status unchanged

    # param  (DATA8)   LAYER   - Chain layer number [0..3]
    # param  (DATA8)   NO      - Port number
    # param  (DATA8)  "TYPE"   - Device type (0 = don't change type)
    # param  (DATA8)   MODE    - Device mode [0..7] (-1 = don't change mode)
    # return (DATA8)   PCT     - Percent value from device

    layer = 0
    message = ( byte (opINPUT_READ) + LC0(layer) + LC0(sensor) + LC0(typ) + LC0(mode) + GV0(0) )

    local_vars = 0
    global_vars = 1
    write_direct_command_reply (message, local_vars, global_vars)

    data = read_reply ()
    check_direct_command_reply (data)

    return replyAsList (data) [0]

# http://github.com/mindboards/ev3sources/blob/master/lms2012/c_input/source/c_input.c

# --------------------------------------------------------------------------

def setLed (color) :
    data = [opUI_WRITE, LC0(LED), LC0(color) ]
    write_direct_command (listToStr (data))

def fillWindow () :
    data = [ opUI_DRAW, LC0(FILLWINDOW), LC0(0), LC0(0), LC0(0) ]
    write_direct_command (listToStr (data))

def drawLine (color, x0, y0, x1, y1) :
    data = [ opUI_DRAW, LC0(LINE), LC(color), LC0(x0), LC0(y0), LC1(x1), LC1(y1) ]
    write_direct_command (listToStr (data))

def drawText (color, x, y, text) :
    data = [opUI_DRAW, LC0(TEXT), LC0(color), LC(x), LC(y), LCS(text) ]
    write_direct_command (listToStr (data))


def clearText () :
    data = [opUI_WRITE, LC0(INIT_RUN)]
    write_direct_command (listToStr (data))

# --------------------------------------------------------------------------

def writeFile (fileName, fileData) :
    file_size = len (fileData)
    message = byte (BEGIN_DOWNLOAD) + LongToBytes (file_size) + fileName + byte (0)
    # NO LCS before file name
    write_system_command_reply (message)

    data = read_reply ()
    check_system_command_reply (data)
    command = data [5]
    status = data [6]
    handle = data [7]
    if trace2 :
       print ("command=", format (command, '02x'), "status=", format (status, '02x'), "handle=", format (handle, '02x'))

    if status == SUCCESS :
       message = byte (CONTINUE_DOWNLOAD) + byte (handle) + fileData
       write_system_command_reply (message)
       data = read_reply ()
       check_system_command_reply (data)

       command = data [5]
       status = data [6]
       handle = data [7]
       if trace2 :
          print ("command=", format (command, '02x'), "status=", format (status, '02x'), "handle=", format (handle, '02x'))

def readFile (fileName) :
    max_bytes = 512
    message = byte (BEGIN_UPLOAD) + WordToBytes (max_bytes) + fileName + byte (0)
    # NO LCS before path
    write_system_command_reply (message)

    data = read_reply ()
    check_system_command_reply (data)
    command = data [5]
    status = data [6]
    size = dataAsNumber (data [7:11])
    handle = data [11]
    if trace2 :
       print ("command=", format (command, '02x'), "status=", format (status, '02x'))
    text = ""
    for c in data [12:] :
        text = text + chr (c)
    return text

def deleteFile (fileName) :
    message = byte (DELETE_FILE) + fileName + byte (0)
    write_system_command_reply (message)

    data = read_reply ()
    # no check_system_command_reply (data)
    command = data [5]
    status = data [6]
    handle = data [7]
    if trace2 :
       print ("delete file", "status =", format (status, '02x'), "handle =", format (handle, '02x'))

def listFiles (path = "") :
    # path is relative from "lms2012/sys" ( "/home/root/lms2012/sys")
    # "..", "../apps" , "../tools" or "../prjs"
    max_bytes = 1024
    message = byte (LIST_FILES) + WordToBytes (max_bytes) + path + byte (0)
    # NO LCS before path
    write_system_command_reply (message)

    data = read_reply (max_bytes)
    check_system_command_reply (data)
    status = data [6]
    text = ""
    for c in data [12:] :
       text = text + chr (c)
    print ("-" * 40)
    print ("list files", path)
    print ("status =", status)
    print (text, end=' ')
    if False :
       print ("lines:")
       for line in text.split ("\n") :
          # print "(" + line + ")", len (line)
          print (len (line), "(", end=' ')
          for c in line :
             print (ord (c), end=' ')
          print (")")
    print ("end of file list ")
    print ("-" * 40)

def runFile (fileName) :
    message = byte (opFILE) + LC0 (LOAD_IMAGE) + LC0 (USER_SLOT) + LCS (fileName) + LV0(0) + LV0(4)
    message = message + byte (opPROGRAM_START) + LC0 (USER_SLOT) + LC0(0) + LV0(4) + LC0(0)
    write_direct_command (message, local_vars = 32, global_vars = 32) # local_vars - important

def stopProgram () :
    message = byte (opPROGRAM_STOP) + LC0 (USER_SLOT)
    write_direct_command (message)

def getStatus () :
    message = ( byte (opPROGRAM_INFO) + LC0 (GET_STATUS) + LC0 (USER_SLOT) + GV0(0) )
    write_direct_command_reply (message, local_vars=0, global_vars=4)

    data = read_reply ()
    print_direct_command_reply (data)

def writeMemory () :
    object_id = 0
    start = 0
    message = (byte (opINIT_BYTES) + LV0(0) + LC0(5) + byte (1) + byte (2)+byte (3) + byte (4) + byte (5) +
               byte (opMEMORY_WRITE)+LC0(USER_SLOT)+LC0(0)+LC0(16)+LC0(5)+LV0(0))
    write_direct_command (message, local_vars=16, global_vars=32)

def readMemory (count) :
    object_id = 0
    start = 0

    message = ( byte (opMEMORY_READ) + LC0 (USER_SLOT) + LC0 (object_id) +
                LC (start) + LC (count) + GV0(0) )
    write_direct_command_reply (message, local_vars=0, global_vars=count)

    data = read_reply ()
    print_direct_command_reply (data)

def probeMemory (count) :
    object_id = 0
    start = 0

    message = ( byte (opPROBE) + LC0 (USER_SLOT) + LC0 (object_id) +
                LC (start) + LC (count))
    local_vars = 0
    global_vars = 0
    write_direct_command (message, local_vars, global_vars)

def execute (cmd) :
    # opSYSTEM(COMMAND, STATUS)
    # Executes a system command
    # param  (DATA8)   COMMAND  - Command string (HND)
    # return (DATA32)  STATUS   - Return status of the command
    message = byte (opSYSTEM) + LCS (cmd) + LV0 (0)
    write_direct_command_reply (message, local_vars = 0, global_vars = 4)

    # time.sleep (1) # important
    data = repeat_read_reply ()
    check_direct_command_reply (data)
    if trace2 :
       print_direct_command_reply (data)

def setBluetoothPin (mac_addr, pin) :
    mac_addr = mac_addr.replace (":", "")

    mac_addr = mac_addr [:12]
    while len (mac_addr) < 12 :
        mac_addr = mac_adr + byte (0)

    pin = pin [:6]
    while len (pin) < 6 :
        pin = pin + byte (0)

    s = mac_addr
    mac_addr = bytearray ([])
    for c in s :
       mac_addr.append (ord (c))

    mac_addr = mac_addr + byte (0)
    pin = pin + byte (0)

    message = ( byte (BLUETOOTHPIN) +
                byte (len (mac_addr)) + mac_addr +
                byte (len (pin)) + pin )

    write_system_command_reply (message)

    data = read_reply ()

    if 1 or trace2 :
       # printChars ("command", message)
       # printBytes ("reply", data, short = True)
       print_system_command_reply (data)

       mac_addr = data [7:22]
       printBytes ("mac_addr", mac_addr)
       pin = data [21:30]
       printBytes ("pin", pin)

    check_system_command_reply (data)

    mac_addr = dataAsString (data [7:22])
    s = ""
    for i in range (len (mac_addr)) :
       if i % 2 == 0 and i != 0 :
          s = s + ":"
       s = s + mac_addr [i]
    mac_addr = s
    print ("mac_addr", mac_addr)

    pin = dataAsString (data [21:30])
    print ("pin", pin)

# --------------------------------------------------------------------------

def updateProgramSize (prg) :
    cnt = len (prg)
    prg = prg [:4] + LongToBytes (cnt) + prg [8:]
    return prg

def printProgram (prg) :
    n = 0
    for c in prg :
       print (format (c, '02x'), end=' ')
       n = n + 1
       if n % 16 == 0 :
          print ( )
       elif n % 4 == 0 :
          print ("|", end=' ')
    print ()

# --------------------------------------------------------------------------

def smallProgram () :
    prg = ( PROGRAMHeader (0, 1, 0) + #  VersionInfo, NumberOfObjects, GlobalBytes
            VMTHREADHeader (0x1c, 0) +   #  OffsetToInstructions, LocalBytes

            # command to start motor on port A at speed 20
            byte (opOUTPUT_POWER) + LC0 (0) + LC0 (1) + LC0 (20) +
            byte (opOUTPUT_START) + LC0 (0) + LC0 (1) +

            byte (opOBJECT_END) )

    prg = updateProgramSize (prg)

    if trace2 :
       printProgram (prg)

    return prg

# --------------------------------------------------------------------------

def middleProgram () :
    prg = ( PROGRAMHeader (0, 1, 0) + #  VersionInfo, NumberOfObjects, GlobalBytes
            VMTHREADHeader (0x1c, 4) +   #  OffsetToInstructions, LocalBytes
            byte (opUI_WRITE) + LC0(LED) + LC0(LED_ORANGE) +

            # command to start motor on port A at speed 20
            byte (opOUTPUT_POWER) + LC0 (0) + LC0 (1) + LC0 (20) +
            byte (opOUTPUT_START) + LC0 (0) + LC0 (1) +

            byte (opTIMER_WAIT) + LC(500) + LV(0) +
            byte (opTIMER_READY) + LV(0) +

            byte (opUI_WRITE) + LC0(LED) + LC0(LED_RED) +

            byte (opTIMER_WAIT) + LC(500) + LV(0) +
            byte (opTIMER_READY) + LV(0) +

            # stop motors
            byte (opOUTPUT_STOP) + byte (0) + byte (15) + byte (0) +

            byte (opOBJECT_END) )

    prg = updateProgramSize (prg)

    if trace2 :
       printProgram (prg)

    return prg

# --------------------------------------------------------------------------

def simpleInstr () :
    message = ( byte (opMOVE32_32) + LC4(1) + GV0(0) +
                byte (opADD32) + LC4(7) + GV0(0) + GV0(4) )
    local_vars = 0
    global_vars = 8
    write_direct_command_reply (message, local_vars, global_vars)

    data = read_reply ()
    print_direct_command_reply (data)

# --------------------------------------------------------------------------

if __name__ == '__main__':

    connectToEV3 ()

    if 1 :
       print ("brick name:", brickName ())
       print ("version:", getVersion ())
       print ("battery info:", batteryInfo ())

    if 0 :
       for i in range (4) :
          print ("sensor name", i, ":", sensorName (i))

       for i in range (4) :
          print ("sensor", i, ":", readSensor (i))

    if 0 :
       mac_addr = bluetooth_address
       # setBluetoothPin (mac_addr, "0")
       setBluetoothPin (mac_addr, "1234")
       # setBluetoothPin (mac_addr, "7788")
       # setBluetoothPin (mac_addr, "778899")
       # setBluetoothPin ("00:00:00:00:00:00", "")

    if 0 :
       deleteFile ("../prjs/test/test.txt")
       listFiles ("../prjs/test")
       execute ("ls -l / >  ../prjs/test/test.txt")
       listFiles ("../prjs/test")
       print ("answer is: ")
       print (readFile ("../prjs/test/test.txt"))

    if 0 :
       simpleInstr ()

    if 0 :
       listFiles ("../prjs/BrkProg_SAVE")
       runFile ("../prjs/BrkProg_SAVE/Demo.rpf")
       time.sleep (1)
       stopProgram ()

    if 0 :
       # prog_list = smallProgram ()
       prog_list = middleProgram ()
       printProgram (prog_list)
       deleteFile ("../prjs/test/test.rbf")
       writeFile ("../prjs/test/test.rbf", prog_list)
       listFiles ("../prjs/test")
       runFile ("../prjs/test/test.rbf")
       time.sleep (1)
       stopProgram ()
       Off (15)

    if 1 :
       prog_list = microProgram ()
       deleteFile ("../prjs/test/test.rbf")
       writeFile ("../prjs/test/test.rbf", prog_list)
       listFiles ("../prjs/test")
       runFile ("../prjs/test/test.rbf")
       print ("======")
       time.sleep (2)
       print ("======")
       stopProgram ()
       Off (15)

    if 0 :
       prog_list = miniProgram ()

       deleteFile ("../prjs/test/test.rbf")
       writeFile ("../prjs/test/test.rbf", prog_list)
       listFiles ("../prjs/test")
       runFile ("../prjs/test/test.rbf")
       # NO getStatus ()
       print ("======")
       time.sleep (4)
       readMemory (16)
       print ("======")
       getStatus ()
       stopProgram ()
       Off (15)

    if 0 :
       OnFwd (1, 20)
       time.sleep (1)
       Off (15)

# --------------------------------------------------------------------------

# http://github.com/esteve/python-ev3
# http://thiagomarzagao.com/2014/06/24/rise-of-the-machines-part-2-2/

# http://github.com/mindboards/ev3sources/blob/master/lms2012/lms2012/source/bytecodes.h
# http://github.com/mindboards/ev3sources/blob/master/lms2012/c_com/source/c_com.h
# http://github.com/mindboards/ev3sources/blob/master/lms2012/c_input/source/c_input.c

# http://ev3.fantastic.computer/doxygen/directcommands.html
# http://ev3.fantastic.computer/doxygen/systemcommands.html

# http://topikachu.github.io/python-ev3/bytecodedef.html

# -- QUT EV3 MATLAB toolkit, Queensland University of Technology, Brisbane, Australia
# http://wiki.qut.edu.au/display/cyphy/QUT+EV3+MATLAB+toolkit
# http://wiki.qut.edu.au/display/cyphy/VM+Instructions
# http://matlab-toolboxes-robotics-vision.googlecode.com/svn/matlab/robot/trunk/interfaces/EV3
# http://matlab-toolboxes-robotics-vision.googlecode.com/svn/matlab/robot/trunk/interfaces/EV3/Command.m
# http://matlab-toolboxes-robotics-vision.googlecode.com/svn/matlab/robot/trunk/interfaces/EV3/Brick.m
# http://code.google.com/p/matlab-toolboxes-robotics-vision/source/browse/matlab/robot/trunk/interfaces/EV3/Brick.m

# -- Line Follower example
# http://github.com/mindboards/ev3sources/blob/master/lms2012/lmssrc/tst/p5.c
# http://ev3.fantastic.computer/doxygen/programexample1.html
# http://ev3.fantastic.computer/doxygen/programs.html

# -- EV3 API for .NET
# http://github.com/BrianPeek/legoev3

# http://www.monobrick.dk/software/monobrick/
# http://github.com/mikeobrien/HidLibrary

# --------------------------------------------------------------------------

# /etc/udev/rules.d/99-ev3.rules
# ACTION=="add", SUBSYSTEMS=="usb", ATTRS{idVendor}=="0694", ATTRS{idProduct}=="0005", GROUP="users", MODE="0666"

# chown root:root /etc/udev/rules.d/99-ev3.rules
# chmod 644 /etc/udev/rules.d/99-ev3.rules

# http://icube-avr.unistra.fr/en/index.php/EV3.14

# --------------------------------------------------------------------------

# http://www.depts.ttu.edu/coe/stem/gear/ev3/documents/Ev3-Connect-Computer.pdf

# port 1: touch sensor
# port 3: color sensor
# port 4: ultrasonic/infared sensor

# port A: medium motor
# port B: large motor
# port C: large motor

# --------------------------------------------------------------------------

# http://forums.usfirst.org/showthread.php?20835-EV3-lock-ups-and-rebooting

# 2. Hold down the Back, Center, and Left buttons on the EV3 Brick.
# 3. When the screen goes blank, release the Back button.

# --------------------------------------------------------------------------

# yum install pyusb

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
