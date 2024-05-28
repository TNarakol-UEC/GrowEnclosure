import schedule
from datetime import time, datetime
import time as time2  # We already import time from datetime so time library is imported as time2
import threading
import json
import os

# Submodules import, these require files to be present in local dir
from sensorfeed import feedread
from watercontrol import autowater, stopwater
from fancontrol import fanon, fanoff
from lightcontrol import growlighton, growlightoff
from picamera import picam_capture
from dataout import excelout
from timecheck import is_time_between
from timestrconvert import timestr
from lcddispfunc import main_menu, lcd, debounce, lcd_menu_thread, set_lcd_color, manual_control_menu, manual_override

# Import plant data used as a basis
from addclass import PlantDef  # This import plant as a class, this is imported globally

# Function to load plant settings dynamically
def load_plant_settings(filename="plant_settings.json"):
    try:
        with open(filename, "r") as f:
            data = json.load(f)
        return PlantDef(
            name=data["name"],
            dryValue=data["dryValue"],
            maxTemp=data["maxTemp"],
            maxHumid=data["maxHumid"],
            waterVol=data["waterVol"],
            checkTime=tuple(data["checkTime"]),
            sunrise=tuple(data["sunrise"]),
            sunset=tuple(data["sunset"]),
            fanTime=data["fanTime"]
        )
    except FileNotFoundError:
        return PlantDef(
            name='Default Plant',
            dryValue=800,
            maxTemp=30,
            maxHumid=90,
            waterVol=600,  # water volume in mL
            checkTime=(9, 30),  # use 24h time!
            sunrise=(7, 0),  # Cannot use 07 - leading zeroes not permitted in CheckTIme, sunrise, sunset
            sunset=(17, 0),  # Note: All these are defined as tuple eg. (HH:MM) is a tuple of HH and MM
            fanTime=30
        )

# Function to check if the JSON file has been updated
def has_file_changed(filepath, last_modified_time):
    current_modified_time = os.path.getmtime(filepath)
    return current_modified_time != last_modified_time, current_modified_time

# Initialize Plant object from file
Plant = load_plant_settings()
last_modified_time = os.path.getmtime("plant_settings.json")

##############################################
################# ON BOOTUP ##################
##############################################

# This only initializes once on bootup
set_lcd_color("normal")  # Set LCD color to green on bootup

# Start the LCD menu thread immediately
lcd_thread = threading.Thread(target=lcd_menu_thread)
lcd_thread.daemon = True
lcd_thread.start()

# Starts with reading values from sensor
try:
    ReadVal = feedread()  # T RH SRH in order
    if isinstance(ReadVal, tuple):  # Check if there is an actual value from feedread
        pass
    elif ReadVal == 0:  # If returns 0 there is a failure in feedread
        set_lcd_color("error")  # Set LCD color to red on error
        raise RuntimeError('SENSOR FAIL')  # Force code to quit and systemd will force it to restart
    else:  # For any unknown error
        set_lcd_color("error")  # Set LCD color to red on error
        raise RuntimeError('UKNOWN FAILURE')

    # Now check if light needs to be on or off
    if not manual_override["light"]:  # Skip automatic control if manual override is active
        if is_time_between(time(Plant.sunrise[0], Plant.sunrise[1]), time(Plant.sunset[0], Plant.sunset[1])):
            grstatus = growlighton()
            if grstatus != 1:
                set_lcd_color("error")  # Set LCD color to red on error
        else:
            grstatus = growlightoff()
            if grstatus != 1:
                set_lcd_color("error")  # Set LCD color to red on error

    # Check if internal humidity or temperature is too high and the fan needs to be on
    if ReadVal[0] > Plant.maxTemp or ReadVal[1] > Plant.maxHumid:
        fanstatus = fanon(Plant.fanTime)
        if fanstatus != 1:
            set_lcd_color("error")  # Set LCD color to red on error
    elif ReadVal[0] <= Plant.maxTemp and ReadVal[1] <= Plant.maxHumid:
        pass
    else:
        set_lcd_color("error")  # Set LCD color to red on error

except RuntimeError as e:
    set_lcd_color("error")  # Set LCD color to red on error
    print(f"Error on startup: {e}")

##############################################
##############   SCHEDULED CODE   ############
##############################################

# Convert settime to usable string by schedule
watersettime = timestr(Plant.checkTime)
sunrisesettime = timestr(Plant.sunrise)
sunsetsettime = timestr(Plant.sunset)

def EveryXX15():  # This schedule grouping runs at every quarter of hour
    try:
        set_lcd_color("in_progress")  # Set LCD color to blue when in progress

        # This should read value from sensor and turn fan on or off
        # Read value from sensor
        ReadVal = feedread()  # T RH SRH in order
        if isinstance(ReadVal, tuple):  # Check if there is an actual value from feedread
            pass
        elif ReadVal == 0:  # If returns 0 there is a failure in feedread
            set_lcd_color("error")  # Set LCD color to red on error
            return
        else:  # For any unknown error
            set_lcd_color("error")  # Set LCD color to red on error
            return

        # Turn on fan if temp or humidity exceeds the limit
        if ReadVal[0] > Plant.maxTemp or ReadVal[1] > Plant.maxHumid:
            fanstatus = fanon(Plant.fanTime)
            if fanstatus != 1:
                set_lcd_color("error")  # Set LCD color to red on error
        elif ReadVal[0] <= Plant.maxTemp and ReadVal[1] <= Plant.maxHumid:
            pass
        else:
            set_lcd_color("error")  # Set LCD color to red on error

        set_lcd_color("normal")  # Set LCD color to green when done

    except RuntimeError as e:
        set_lcd_color("error")  # Set LCD color to red on error
        print(f"Error in EveryXX15: {e}")

def EverySETTIME():  # This runs every settime read from addclass.py
    try:
        set_lcd_color("in_progress")  # Set LCD color to blue when in progress

        # This should read value from sensor and autowater if Soil moisture too low
        # Read value from sensor
        ReadVal = feedread()  # T RH SRH in order
        if isinstance(ReadVal, tuple):  # Check if there is an actual value from feedread
            pass
        elif ReadVal == 0:  # If returns 0 there is a failure in feedread
            set_lcd_color("error")  # Set LCD color to red on error
            return
        else:  # For any unknown error
            set_lcd_color("error")  # Set LCD color to red on error
            return

        # Now water plant if soil too dry
        if ReadVal[2] <= Plant.dryValue and not manual_override["watering"]:
            wtrstatus = autowater(Plant.waterVol)
            if wtrstatus != 1:
                set_lcd_color("error")  # Set LCD color to red on error
        elif ReadVal[2] > Plant.dryValue:
            pass
        else:
            set_lcd_color("error")  # Set LCD color to red on error

        set_lcd_color("normal")  # Set LCD color to green when done

    except RuntimeError as e:
        set_lcd_color("error")  # Set LCD color to red on error
        print(f"Error in EverySETTIME: {e}")

def EveryXX25():  # This code runs at every 25 minute mark of the hour
    try:
        set_lcd_color("in_progress")  # Set LCD color to blue when in progress

        # Read value from sensor and write it out to excel
        # Read value from sensor
        ReadVal = feedread()  # T RH SRH in order
        if isinstance(ReadVal, tuple):  # Check if there is an actual value from feedread
            pass
        elif ReadVal == 0:  # If returns 0 there is a failure in feedread
            set_lcd_color("error")  # Set LCD color to red on error
            return
        else:  # For any unknown error
            set_lcd_color("error")  # Set LCD color to red on error
            return

        # Write data out to excel file
        excelstatus = excelout(ReadVal[0], ReadVal[1], ReadVal[2])
        if excelstatus != 1:
            set_lcd_color("error")  # Set LCD color to red on error

        set_lcd_color("normal")  # Set LCD color to green when done

    except RuntimeError as e:
        set_lcd_color("error")  # Set LCD color to red on error
        print(f"Error in EveryXX25: {e}")

def EveryXX35():  # Runs every 35 minute mark of the hour
    try:
        set_lcd_color("in_progress")  # Set LCD color to blue when in progress

        # Take picture with pi camera
        pcamstatus = picam_capture()
        if pcamstatus != 1:
            set_lcd_color("error")  # Set LCD color to red on error

        set_lcd_color("normal")  # Set LCD color to green when done

    except RuntimeError as e:
        set_lcd_color("error")  # Set LCD color to red on error
        print(f"Error in EveryXX35: {e}")

def EverySUNRISE():  # This should run every sunrise time to turn on the light
    try:
        set_lcd_color("in_progress")  # Set LCD color to blue when in progress

        if not manual_override["light"]:
            grstatus = growlighton()
            if grstatus != 1:
                set_lcd_color("error")  # Set LCD color to red on error

        set_lcd_color("normal")  # Set LCD color to green when done

    except RuntimeError as e:
        set_lcd_color("error")  # Set LCD color to red on error
        print(f"Error in EverySUNRISE: {e}")

def EverySUNSET():  # This should run every sunset time to turn off light
    try:
        set_lcd_color("in_progress")  # Set LCD color to blue when in progress

        if not manual_override["light"]:
            grstatus = growlightoff()
            if grstatus != 1:
                set_lcd_color("error")  # Set LCD color to red on error

        set_lcd_color("normal")  # Set LCD color to green when done

    except RuntimeError as e:
        set_lcd_color("error")  # Set LCD color to red on error
        print(f"Error in EverySUNSET: {e}")

# Multithreading
def run_threaded(job_func):
    job_thread = threading.Thread(target=job_func)
    job_thread.start()

# Scheduler calls
schedule.every().hour.at(":15").do(run_threaded, EveryXX15)
schedule.every().hour.at(":25").do(run_threaded, EveryXX25)
schedule.every().hour.at(":35").do(run_threaded, EveryXX35)
schedule.every().day.at(watersettime).do(run_threaded, EverySETTIME)
schedule.every().day.at(sunrisesettime).do(run_threaded, EverySUNRISE)
schedule.every().day.at(sunsetsettime).do(run_threaded, EverySUNSET)

# Function to periodically check for JSON file updates
def check_for_updates():
    global Plant, last_modified_time
    has_changed, new_modified_time = has_file_changed("plant_settings.json", last_modified_time)
    if has_changed:
        Plant = load_plant_settings()
        last_modified_time = new_modified_time
        # Update schedule times
        global watersettime, sunrisesettime, sunsetsettime
        watersettime = timestr(Plant.checkTime)
        sunrisesettime = timestr(Plant.sunrise)
        sunsetsettime = timestr(Plant.sunset)
        # Re-schedule tasks with updated times
        schedule.clear()
        schedule.every().hour.at(":15").do(run_threaded, EveryXX15)
        schedule.every().hour.at(":25").do(run_threaded, EveryXX25)
        schedule.every().hour.at(":35").do(run_threaded, EveryXX35)
        schedule.every().day.at(watersettime).do(run_threaded, EverySETTIME)
        schedule.every().day.at(sunrisesettime).do(run_threaded, EverySUNRISE)
        schedule.every().day.at(sunsetsettime).do(run_threaded, EverySUNSET)

# Add a scheduler to check for JSON updates every minute
schedule.every(1).minute.do(check_for_updates)

# Main loop to monitor current time against sunrise and sunset times
def monitor_lights():
    while True:
        if not manual_override["light"]:  # Skip automatic control if manual override is active
            current_time = datetime.now().time()
            if is_time_between(time(Plant.sunrise[0], Plant.sunrise[1]), time(Plant.sunset[0], Plant.sunset[1]), current_time):
                growlighton()
            else:
                growlightoff()
        time2.sleep(1)  # Check every second

# Start monitoring lights in a separate thread
monitor_thread = threading.Thread(target=monitor_lights)
monitor_thread.daemon = True
monitor_thread.start()

# Main loop to monitor temperature and humidity for fan control
def monitor_fan():
    while True:
        if not manual_override["fan"]:  # Skip automatic control if manual override is active
            ReadVal = feedread()  # Read sensor values
            if isinstance(ReadVal, tuple):  # Ensure valid readings
                if ReadVal[0] > Plant.maxTemp or ReadVal[1] > Plant.maxHumid:
                    fanstatus = fanon(Plant.fanTime)
                    if fanstatus != 1:
                        set_lcd_color("error")  # Set LCD color to red on error
        time2.sleep(1)  # Check every second

# Start monitoring fan in a separate thread
fan_thread = threading.Thread(target=monitor_fan)
fan_thread.daemon = True
fan_thread.start()

while True:
    schedule.run_pending()
    time2.sleep(1)
