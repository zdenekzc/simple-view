#! /usr/bin/env python

# http://bricks.stackexchange.com/questions/4256/cant-send-multiple-commands-to-ev3-using-python
# http://blog.thekitchenscientist.co.uk/2014/12/commanding-ev3-from-linux-pc-part-1.html

import time, bluetooth

# command to start motor on port A at speed 20
start_motor = '\x0C\x00\x00\x00\x80\x00\x00\xA4\x00\x01\x14\xA6\x00\x01'

# command to stop motor on port A
stop_motor = '\x09\x00\x01\x00\x80\x00\x00\xA3\x00\x01\x00'

play_tone = '\x0F\x00\x00\x00\x80\x00\x00\x94\x01\x81\x02\x82\xE8\x03\x82\xE8\x03'

# send commands to EV3 via bluetooth

if 0 :
   # with open('/dev/rfcomm0', 'w', 0) as bt:
      bt.write (start_motor)
      time.sleep (5)
      bt.write (stop_motor)
      bt.write (play_tone)
else :    
    serverMACAddress = "00:16:53:40:54:02"
    port = 1
    s = bluetooth.BluetoothSocket (bluetooth.RFCOMM)
    s.connect ((serverMACAddress, port))

    s.send (start_motor)
    time.sleep (5)
    s.send (stop_motor)
    s.send (play_tone)

# --------------------------------------------------------------------------

#
# RFCOMM configuration file.
#

# rfcomm0 {
#     # Automatically bind the device at startup
#     bind yes;
#
#     # Bluetooth address of the device
#     device 00:16:53:40:54:02;
#
#     # RFCOMM channel for the connection
#     channel    1;
#
#     # Description of the connection
#     comment "My EV3";
#  }

# --------------------------------------------------------------------------

# http://blog.thekitchenscientist.co.uk/2014/12/commanding-ev3-from-linux-pc-part-1.html
# hcitool scan
# gedit /etc/bluetooth/rfcomm.conf
# ./simple-agent (from bluez-5.29/test) (Fedora 22)
# rfcomm connect 0 00:16:53:40:54:02 1

# --------------------------------------------------------------------------

# hcidump
# hciconfig
# hciconfig hci0 up piscan
# EV3 ... bluetooth ... connections ... PC ... remove

# bluetoothctl
#   pairable on
#   discoverable on
#   agent KeyboardOnly
#   pair 00:16:53:40:54:02
#   trust 00:16:53:40:54:02
#   connect 00:16:53:40:54:02

# --------------------------------------------------------------------------

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all

