from machine import I2C
from machine import Pin
from machine import sleep
import mpu6050

import urequests
import time
from machine import Timer
import esp32
import machine

# Constants
SENSITIVITY = 0.5

ledRed = Pin(26, Pin.OUT)
ledGreen = Pin(25, Pin.OUT)
sensorState = 0

##### Sensor Calibration #####
i2c = I2C(scl=Pin(22), sda=Pin(23))     #initializing the I2C method for ESP32
mpu = mpu6050.accel(i2c)

# Calibration
print("Let the sensor remain flat and stand still for 5 seconds...")
time.sleep(5)
def getReadings():
    ax = 0.0
    ay = 0.0
    az = 0.0
    for i in range(0, 100):
        test = mpu.get_values()
        ax = ax + test['AcX']
        ay = ay + test['AcY']
        az = az + test['AcZ']

    ax = ax / 100.0
    ay = ay / 100.0
    az = az / 100.0
    return [ax, ay, az]

readingList = getReadings()
dz = mpu6050.STANDARD_GRAVITY - readingList[2]
dx = 0.0 - readingList[0]
dy = 0.0 - readingList[1]
readingList[2] = readingList[2] + dz
readingList[0] = readingList[0] + dx
readingList[1] = readingList[1] + dy
print(readingList)
print("Calibration done!")
   
# Status Check
def getStatus(self):
    global sensorState
    global ledGreen
    global ledRed
    request = urequests.get("https://api.thingspeak.com/channels/1715955/fields/1.json?api_key=1Y1Y8Z9P2JVT736N&results=2").text
    texts = request[-25 : ]
    if texts.find("deactivate") < 0:
        sensorState = 1
        ledGreen.on()
        ledRed.off()
    else:
        sensorState = 0
        ledGreen.off()
    
def getMeasurements(self):
    global ledRed
    global sensorState
    if sensorState == 1:
        readingList = getReadings()
        myValues = {}
        myValues['AcZ'] = readingList[2] + dz
        myValues['AcX'] = readingList[0] + dx
        myValues['AcY'] = readingList[1] + dy
        
        if abs(myValues['AcX']) >= SENSITIVITY or abs(myValues['AcY']) >= SENSITIVITY or abs(abs(myValues['AcZ']) - mpu6050.STANDARD_GRAVITY) >= SENSITIVITY:
            readings = {'value1': 'AccelX ' + str(myValues['AcX']), 'value2': 'AccelY ' + str(myValues['AcY']), 'value3': 'AccelZ '+ str(myValues['AcZ'])}
            request = urequests.post("https://maker.ifttt.com/trigger/Motion_Detected/with/key/wsTFwzA3o_bk2VYfFrOFs", json = readings)
            request.close()
            ledRed.on()
        else:
            ledRed.off()
    else:
        ledRed.off()


statusTimer = Timer(0)
statusPeriod = 30
statusTimer.init(period = statusPeriod * 1000, mode=machine.Timer.PERIODIC, callback = getStatus)

measurementTimer = Timer(1)
measurePeriod = 5
measurementTimer.init(period = measurePeriod * 1000, mode=machine.Timer.PERIODIC, callback = getMeasurements)