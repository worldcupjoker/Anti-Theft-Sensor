# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
#import webrepl
#webrepl.start()

import network
import urequests
from machine import Timer
import esp32
import machine

import esp
esp.osdebug(None)

import gc
gc.collect()

##### Internet Connection #####
ssid = 'WIFINAME'
password = 'PASSWORD'

station = network.WLAN(network.STA_IF)

station.active(True)
station.connect(ssid, password)

while station.isconnected() == False:
    pass

print("Connected to " + ssid)
print("IP Address: " + str(station.ifconfig()[0]))