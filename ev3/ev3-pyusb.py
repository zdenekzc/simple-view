#! /usr/bin/env python

import usb

# yum install pyusb

# devices = usb.core.find (find_all=True)
# for d in devices :
#    print d

device = usb.core.find (idVendor=0x0694, idProduct=0x0005)
if device :
   print device

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all

