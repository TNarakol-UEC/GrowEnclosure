#Growth Enclosure main Python code
#Ulnooweg Education Centre - All rights reserved
#Contact: ulnoowegeducation.ca

#NOTES: THIS VERSION IS USING IMPORTED BLINKA LIBRARIES. NATIVE LIBRARIES WILL BE USED IN NEXT REFACTOR.
########################################

#import important library
#Standard python library
import asyncio
import time
import json

#All these are part of Blinka
#import os #Not used anymore, os level ops above the code
#import supervisor #Not used anymore, code do not have supervisor reload privilege unlike microcontroller
#import wifi Wifi not needed anymore
import ssl
#import socketpool #socketpool not needed
import board
import busio
import digitalio
#import rtc #Pi 3A+ do not use RTC as OS handles date time ops

#Library requiring additional installation other than standard Blinka install
import adafruit_ahtx0
import adafruit_requests
from adafruit_io.adafruit_io import IO_HTTP, AdafruitIO_RequestError
from adafruit_seesaw.seesaw import Seesaw
import adafruit_ina219
#import adafruit_ntp #ntp handled OS level

#Functions/Class from other file
from addclass import Plant #import plant as a class from file addclass

#Configure global parameters for various options in the code
rateLimit = 30 # Adafruit IO updates per minute
plant = plants.testPlant # which plant are we growing

#Setup pinouts for hardware used
#Current: Raspberry Pi 3 A+ with BCRobotics Irrigation Hat V2
pins = {
    'S1' : board.GP13, #This is MOSFET control pin 1 (System 1). Other S pin controls n MOSFET.
    'S2' : board.GP16, #GP Corresponds to GPIO pins
    'S3' : board.GP19,
    'S4' : board.GP20,
    'S5' : board.GP26, #This is button input pin 1. Other B pin receive n button command
    'B1' : board.GP12,
    'B2' : board.GP6,
    'B3' : board.GP5,
    'B4' : board.GP25,
    #'B5' : board.GP15, #Comment out any B5 or GP15 as there's currently only 4 analog control
    'QWIIC_SCL' : board.GP2, #Define I2C pin CLOCK
    'QWIIC_SDA' : board.GP3 #Define I2C pin DATA
    }

#Setup Actuator circuts
print("initalizing actuator circuts")

s1 = digitalio.DigitalInOut(pins['S1'])
s2 = digitalio.DigitalInOut(pins['S2'])
s3 = digitalio.DigitalInOut(pins['S3'])
s4 = digitalio.DigitalInOut(pins['S4'])
s5 = digitalio.DigitalInOut(pins['S5'])

for s in [s1, s2, s3, s4, s5]:
    s.direction = digitalio.Direction.OUTPUT
    s.drive_mode = digitalio.DriveMode.PUSH_PULL
    s.value = False

# Front Panel Buttons
b1 = digitalio.DigitalInOut(pins['B1'])
b2 = digitalio.DigitalInOut(pins['B2'])
b3 = digitalio.DigitalInOut(pins['B3'])
b4 = digitalio.DigitalInOut(pins['B4'])
#b5 = digitalio.DigitalInOut(pins['B5'])

for b in [b1, b2, b3, b4]: #because of the way these are defined, true = unpressed; b5 removed
    b.direction = digitalio.Direction.INPUT
    b.pull = digitalio.Pull.UP

# Setup QWIIC Bus
print("initalizing I2C bus")
qwiic = busio.I2C(scl=pins['QWIIC_SCL'], sda=pins['QWIIC_SDA'])

# Setup Sensors
print("initalizing sensors")
try:
    ths = adafruit_ahtx0.AHTx0(qwiic) # Temperature & Humidity Sensor
    sms = Seesaw(qwiic, addr=0x36) # Soil Moisture Sensor
    cs = adafruit_ina219.INA219(qwiic) # Pump Current Sensor
except:
    print("UNABLE TO INITALIZE SENSORS; RELOADING")
    raise RuntimeError('SENSOR ERROR') #The code will reboot by the forced restart systemd flag after error is raised and the code exited

# onboard led as warning light (temp?)
warnLED = digitalio.DigitalInOut(board.LED)
warnLED.direction = digitalio.Direction.OUTPUT

# Creating actuator objects
class Actuator:
    def __init__(self, circut, button, default = False, flowRate = None, minCurrent = None):
        self.circut     = circut
        self.button     = button
        self.default    = default
        self.flowRate   = flowRate
        self.minCurrent = minCurrent

    def buttonInput(self):
        if self.button.value == False:
            self.circut.value = True
        else:
            self.circut.value = self.default
        return

pump = Actuator(circut = s1, button = b1, flowRate = 66.7, minCurrent = 600)
light = Actuator(circut = s2, button = b2)
fan = Actuator(circut = s3, button = b3)

#Wifi setup is not needed for Pi 3A+ as this is handled OS level
# Wifi Setup:
#print("connecting to Wifi network:", os.getenv('WIFI_SSID'))
#try:
#    wifi.radio.connect(  # todo, make this a try / exept block
#        os.getenv('WIFI_SSID'),
#        os.getenv('WIFI_PASSWORD')
#        )
#    pool = socketpool.SocketPool(wifi.radio)
#    requests = adafruit_requests.Session(pool, ssl.create_default_context())
#except ConnectionError:
#    print('UNABLE TO CONNECT TO NETWORK; RELOADING')
#    supervisor.reload()

# DEPRECATED, NO NEED FOR RTC AS OS HANDLES IT; real time clock (RTC) sync via network time protocol (NTP)
#print("synchronizing real time clock")
#try:
#    ntp = adafruit_ntp.NTP(pool, tz_offset=os.getenv('TZ_OFFSET'))
#    rtc.RTC().datetime = ntp.datetime
#except OSError:
#    print("RTC SYNC TIMEOUT; RELOADING")
#    supervisor.reload()

#Open file with 'with' statement as json_file. This autoclose file. Load data as a dict into extdata
with open('datastore.json') as json_file:
    extdata = json.load(json_file)

# Setup Adafruit IO
print("initalizing Adafruit IO connection to user:", extdata["Adafruit_IO"][0]["AIO_USERNAME"])
try:
    aio_username = extdata["Adafruit_IO"][0]["AIO_USERNAME"] #This returns username as setup in our json file.
    aio_key = extdata["Adafruit_IO"][0]["AIO_KEY"]
    aio = IO_HTTP(aio_username, aio_key, requests)
except: #todo, find out what exeptions will actually be raised and specifically catch them
    print("UNABLE TO CONNECT TO ADAFRUIT IO; RELOADING")
    raise RuntimeError('ADA_IO_CONN_ERROR')

sn = extdata["Enclosure"][0]["Serial"] # enclosure serial number
groupKey = 'grow-enclosure-'+sn
print("connecting to group: ",groupKey)
try:
    sensor_group = aio.get_group(groupKey)
except AdafruitIO_RequestError:
    print('GROUP NOT FOUND; CREATING NEW ONE')
    sensor_group = aio.create_new_group('grow-enclosure-'+sn,'Grow Enclosure Sensors')

print('connecting to sensor data feeds')
try:
    tempFeed = aio.get_feed(groupKey+'.temperature')
    rhFeed   = aio.get_feed(groupKey+'.humidity')
    smsFeed  = aio.get_feed(groupKey+'.soil-moisture')
except AdafruitIO_RequestError:
    print("FEEDS NOT FOUND, CREATING NEW ONES")
    tempFeed = aio.create_feed_in_group(groupKey,'temperature')
    rhFeed   = aio.create_feed_in_group(groupKey,'humidity')
    smsFeed  = aio.create_feed_in_group(groupKey,'soil-moisture')

#Main Functions
async def updateSensorData(updateRate = 1):

    # update rate in updates / min
    updateDelay = 60/updateRate

    while True:
        # read sensors
        temp = ths.temperature
        rh = ths.relative_humidity
        moist = sms.moisture_read()

        t = time.localtime(time.time())
        print("Time:",t[3:6],"Temp(C)=", temp, "%RH=", rh, "Soil Moisture=", moist)

        # send data to dashboard
        aio.send_data(tempFeed["key"], temp)
        aio.send_data(rhFeed["key"], rh)
        aio.send_data(smsFeed["key"], moist)

        await asyncio.sleep(updateDelay)

        continue
    return

async def buttonControl():

    while True:
        pump.buttonInput()
        light.buttonInput()
        fan.buttonInput()
        await asyncio.sleep(0.5)
        continue
    return

async def climateControl(plant, rate = 6):
    rateDelay = 60/rate
    while True:
        t_now     = time.time() # already in unix format
        t_check   = hhmm2unixToday(plant.checkTime)
        t_sunrise = hhmm2unixToday(plant.sunrise)
        t_sunset  = hhmm2unixToday(plant.sunset)

        temp = ths.temperature
        rh = ths.relative_humidity

        # Read the soil moisture and water once per day
        if abs(t_now - t_check) <= rateDelay:
            print("CHECKING SOIL MOISTURE")
            moist = sms.moisture_read()
            if moist <= plant.dryValue:
                print("SOIL TOO DRY")
                autoWater(plant.waterVol, pump)

        # light on at 'sunrise' and off at 'sunset'
        if (t_sunrise <= t_now) and (t_sunset >= t_now):
            light.circut.value = True
            light.default = True
        else:
            light.circut.value = False
            light.default = False

        # turn on fan if temp or humidity is too high
        if (temp >= plant.maxTemp) or (rh >= plant.maxHumid):
            fan.circut.value = True
            fan.default = True
        else:
            fan.circut.value = False
            fan.default = False

        await asyncio.sleep(rateDelay)
        continue
    return

def autoWater(V_water, P = pump):
    t_water = int(V_water / P.flowRate) # how long to run the pump to achieve desired water vol.
    t_start = time.time()
    while time.time() <= (t_start+t_water):
        P.circut.value = True
        time.sleep(1)
        I_pump = cs.current
        if False: #I_pump >= P.minCurrent: #run dry detection disabled pending further testing
            warnLED.value = True
            print("WARNING: PUMP RUNNING DRY")
            print("Pump Current = ",I_pump," mA")
        else:
            warnLED.value = False
            print("AUTOWATERING IN PROGRESS")
            print("Pump Current = ",I_pump," mA")
    P.circut.value = False
    print("AUTOWATERING COMPLETE")

    return

def hhmm2unixToday(t):
    '''
    converts a tuple of t=(hh,mm) to the unix int
    of that time today
    '''
    assert type(t) == tuple
    assert len(t) == 2
    assert (type(t[0]) == int) and (type(t[1]) == int)
    t_unix = time.localtime(time.time())
    t_unix = time.mktime((
            t_unix.tm_year,
            t_unix.tm_mon,
            t_unix.tm_mday,
            t[0],
            t[1],
            0,
            t_unix.tm_wday,
            t_unix.tm_yday,
            t_unix.tm_isdst,
    ))
    return t_unix

#Main loop
print("setup complete")

async def main():

    updateSensorTask = asyncio.create_task(updateSensorData())
    buttonControlTask = asyncio.create_task(buttonControl())
    climateControlTask = asyncio.create_task(climateControl(plant))

    await asyncio.gather(
    updateSensorTask,
    buttonControlTask,
    climateControlTask
    )

try:
    asyncio.run(main())
except MemoryError:
    print("MEMORY ERROR; RELOADING")
    raise RuntimeError('MEMORY_ERROR')
except:
    print("UNHANDLED EXCEPTION; RELOADING")
    for s in [s1, s2, s3, s4, s5]:
        s.direction = digitalio.Direction.OUTPUT
        s.drive_mode = digitalio.DriveMode.PUSH_PULL
        s.value = False
    raise RuntimeError('PC_LOAD_LETTER')