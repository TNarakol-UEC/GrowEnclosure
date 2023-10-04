# Plant Growth Enclosure Controller - Rapsberry Pi Pico W
# Chris Seymour, 2023
#########################################################
import os
import time
import wifi
import ssl
import socketpool
import board
import busio
import digitalio
import adafruit_ahtx0
import adafruit_requests
from adafruit_io.adafruit_io import IO_HTTP
from adafruit_seesaw.seesaw import Seesaw
import adafruit_ina219
import adafruit_asyncio

#########################################################
# Setup
#########################################################

# Wifi Setup:
wifi.radio.connect(  # todo, make this a try / exept block
    os.getenv('WIFI_SSID'),
    os.getenv('WIFI_PASSWORD')
    )
pool = socketpool.SocketPool(wifi.radio)
requests = adafruit_requests.Session(pool, ssl.create_default_context())

# QWIIC Bus
qwiic = busio.I2C(scl=board.GP17, sda=board.GP16)

# Temperature & Humidity Sensor
ths = adafruit_ahtx0.AHTx0(qwiic)

# Soil Moisture Sensor
sms = Seesaw(qwiic, addr=0x36)

# Current Sensor
cs = adafruit_ina219.INA219(qwiic)

# Adafruit IO
aio_username = os.getenv('AIO_USERNAME')
aio_key = os.getenv('AIO_KEY')
aio = IO_HTTP(aio_username, aio_key, requests)
rateLimit = 30  # updates per minute
rateDelay = 60/rateLimit  # how long to wait between updates, seconds

tempFeed = aio.get_feed("grow-enclosure.temperature")
rhFeed = aio.get_feed("grow-enclosure.humidity")
smsFeed = aio.get_feed("grow-enclosure.soil-moisture")

# Actuator circuts
s1 = digitalio.DigitalInOut(board.GP2)
s2 = digitalio.DigitalInOut(board.GP3)
s3 = digitalio.DigitalInOut(board.GP4)
s4 = digitalio.DigitalInOut(board.GP5)
s5 = digitalio.DigitalInOut(board.GP6)

for s in [s1, s2, s3, s4, s5]:
    s.direction = digitalio.Direction.OUTPUT
    s.drive_mode = digitalio.DriveMode.PUSH_PULL
    s.value = False

# Dashboard actuator switches
fanFeed = aio.get_feed("grow-enclosure.fan")
pumpFeed = aio.get_feed("grow-enclosure.pump")
lightFeed = aio.get_feed("grow-enclosure.light")

#########################################################
# Functions
#########################################################

async def update


#########################################################
# Main loop
#########################################################

while True:
    temp = ths.temperature
    print("temp = ", temp)
    aio.send_data(tempFeed["key"], temp)
    time.sleep(rateDelay)

    rh = ths.relative_humidity
    print("%rh = ", rh)
    aio.send_data(rhFeed["key"], rh)
    time.sleep(rateDelay)

    moist = sms.moisture_read()
    print("soil moisture = ", moist)
    aio.send_data(smsFeed["key"], moist)
    time.sleep(rateDelay)

    pumpCurrent = cs.current
    print("pump current = ", pumpCurrent)
    time.sleep(rateDelay)

    lightState = aio.receive_data(lightFeed["key"])
    lightState = bool(int(lightState["value"]))
    print("light state = ", lightState)
    if lightState:
        s1.value = True
    else:
        s1.value = False
    time.sleep(rateDelay)

    pumpState = aio.receive_data(pumpFeed["key"])
    pumpState = bool(int(pumpState["value"]))
    print("pump state = ", pumpState)
    if pumpState:
        s2.value = True
    else:
        s2.value = False
    time.sleep(rateDelay)

    fanState = aio.receive_data(fanFeed["key"])
    fanState = bool(int(fanState["value"]))
    print("fan state = ", fanState)
    if fanState:
        s3.value = True
    else:
        s3.value = False
    time.sleep(rateDelay)
