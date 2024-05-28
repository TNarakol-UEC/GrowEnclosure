#Ulnooweg Education Centre - ulnoowegeducation.ca
#Growth enclosure V1.0
#All rights reserved
#
#This function is the main function
#This functions should call other submodules/functions and execute them as needed/scheduled
#This functions always run under grobot service
#
##############################################
#MODULE IMPORTS
from datetime import time, datetime
import time as time2 #We already import time from datetime so time library is imported as time2
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
Plant = None

# Function to load plant settings dynamically
def load_plant_settings(filename="plant_settings.json"):
    global Plant
    try:
        with open(filename, "r") as f:
            data = json.load(f)
        Plant = PlantDef(
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
        Plant = PlantDef(
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

def reload_settings():
    load_plant_settings()
    update_schedules()

def update_schedules():
    global watersettime, sunrisesettime, sunsetsettime
    watersettime = timestr(Plant.checkTime)
    sunrisesettime = timestr(Plant.sunrise)
    sunsetsettime = timestr(Plant.sunset)
    schedule.clear()
    schedule.every().hour.at(":15").do(run_threaded, EveryXX15)
    schedule.every().hour.at(":25").do(run_threaded, EveryXX25)
    schedule.every().hour.at(":35").do(run_threaded, EveryXX35)
    schedule.every().day.at(watersettime).do(run_threaded, EverySETTIME)
    schedule.every().day.at(sunrisesettime).do(run_threaded, EverySUNRISE)
    schedule.every().day.at(sunsetsettime).do(run_threaded, EverySUNSET)

def has_file_changed(filepath, last_modified_time):
    current_modified_time = os.path.getmtime(filepath)
    return current_modified_time != last_modified_time, current_modified_time

def check_for_updates():
    global Plant, last_modified_time
    has_changed, new_modified_time = has_file_changed("plant_settings.json", last_modified_time)
    if has_changed:
        reload_settings()
        last_modified_time = new_modified_time   

# Multithreading
def run_threaded(job_func):
    job_thread = threading.Thread(target=job_func)
    job_thread.start()

# Function definitions moved before the schedule setup
def EveryXX15():  # This schedule grouping runs at every quarter of hour
import configparser

config = configparser.ConfigParser()

from lcddispfunc import main_menu, lcd, debounce, lcd_menu_thread, set_lcd_color

##############################################
################# ON BOOTUP ##################
##############################################

# This only initialize once on bootup
set_lcd_color("normal")  # Set LCD color to green on bootup

# Start the LCD menu thread immediately
lcd_thread = threading.Thread(target=lcd_menu_thread)
lcd_thread.daemon = True
lcd_thread.start()

# Starts with reading values from sensor
try:
    ReadVal = feedread() # T RH SRH in order
    if isinstance(ReadVal, tuple) == True: # Check if there is an actual value from feedread
        pass
    elif ReadVal == 0: # If returns 0 there is a failure in feedread
        set_lcd_color("error")  # Set LCD color to red on error
        raise RuntimeError('SENSOR FAIL') # Force code to quit and systemd will force it to restart
    else: # For any unknown error
        set_lcd_color("error")  # Set LCD color to red on error
        raise RuntimeError('UKNOWN FAILURE')
    
    #Now do an initial read of the configuration value
    ################## START DEFAULT READ CONFIG BLOCK #################
    config.read("grobot_cfg.ini")
    sunrise = [int(x) for x in config['PLANTCFG']['sunrise'].split(",")]
    sunset = [int(x) for x in config['PLANTCFG']['sunset'].split(",")]
    checkTime = [int(x) for x in config['PLANTCFG']['checkTime'].split(",")]
    dryValue = int(config['PLANTCFG']['dryValue'])
    maxTemp = int(config['PLANTCFG']['maxTemp'])
    maxHumid = int(config['PLANTCFG']['maxHumid'])
    waterVol = int(config['PLANTCFG']['waterVol'])
    fanTime = int(config['PLANTCFG']['fanTime'])
    ################## END DEFAULT READ CONFIG BLOCK #################

    # Now check if light needs to be on or off
    if is_time_between(time(sunrise[0], sunrise[1]), time(sunset[0], sunset[1])) == True:
        grstatus = growlighton()
        if grstatus == 1:
            pass
        elif grstatus == 0:
            set_lcd_color("error")  # Set LCD color to red on error
            raise RuntimeError('LIGHT FAIL') # Force code to quit and systemd will force it to restart
        else: # For any unknown error
            set_lcd_color("error")  # Set LCD color to red on error
            raise RuntimeError('UKNOWN FAILURE')
    elif is_time_between(time(sunrise[0], sunrise[1]), time(sunset[0], sunset[1])) == False:
        grstatus = growlightoff()
        if grstatus == 1:
            pass
        elif grstatus == 0:
            set_lcd_color("error")  # Set LCD color to red on error
            raise RuntimeError('LIGHT FAIL') # Force code to quit and systemd will force it to restart
        else: # For any unknown error
            set_lcd_color("error")  # Set LCD color to red on error
            raise RuntimeError('UKNOWN FAILURE')
    else:
        set_lcd_color("error")  # Set LCD color to red on error
        raise RuntimeError('UKNOWN FAILURE')

    # Check if internal humidity or temperature is too high and the fan needs to be on
    if ReadVal[0] > maxTemp or ReadVal[1] > maxHumid:
        fanstatus = fanon(fanTime)
        if fanstatus == 1:
            pass
        elif fanstatus == 0:
            set_lcd_color("error")  # Set LCD color to red on error
            pass
        else:
            set_lcd_color("error")  # Set LCD color to red on error
            raise RuntimeError('UKNOWN FAILURE')
    elif ReadVal[0] <= maxTemp and ReadVal[1] <= maxHumid:
        pass
    else:
        set_lcd_color("error")  # Set LCD color to red on error
        raise RuntimeError('UKNOWN FAILURE')

except RuntimeError as e:
    set_lcd_color("error")  # Set LCD color to red on error
    raise e

##############################################
##############   SCHEDULED CODE   ############
##############################################

def EveryXX15(): # This schedule grouping runs at every quarter of hour
    try:

        ################## START DEFAULT READ CONFIG BLOCK #################
        config.read("grobot_cfg.ini")
        sunrise = [int(x) for x in config['PLANTCFG']['sunrise'].split(",")]
        sunset = [int(x) for x in config['PLANTCFG']['sunset'].split(",")]
        checkTime = [int(x) for x in config['PLANTCFG']['checkTime'].split(",")]
        dryValue = int(config['PLANTCFG']['dryValue'])
        maxTemp = int(config['PLANTCFG']['maxTemp'])
        maxHumid = int(config['PLANTCFG']['maxHumid'])
        waterVol = int(config['PLANTCFG']['waterVol'])
        fanTime = int(config['PLANTCFG']['fanTime'])
        ################## END DEFAULT READ CONFIG BLOCK #################

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
        if ReadVal[0] > maxTemp or ReadVal[1] > maxHumid:
            fanstatus = fanon(fanTime)
            if fanstatus == 1:
                pass
            elif fanstatus == 0:
                set_lcd_color("error")  # Set LCD color to red on error
                pass
            else:
                set_lcd_color("error")  # Set LCD color to red on error
                raise RuntimeError('UKNOWN FAILURE')
        elif ReadVal[0] <= maxTemp and ReadVal[1] <= maxHumid:
            pass
        else:
            set_lcd_color("error")  # Set LCD color to red on error

        set_lcd_color("normal")  # Set LCD color to green when done

    except RuntimeError as e:
        set_lcd_color("error")  # Set LCD color to red on error
        print(f"Error in EveryXX15: {e}")

def EverySETTIME():  # This runs every settime read from addclass.py
    try:

        ################## START DEFAULT READ CONFIG BLOCK #################
        config.read("grobot_cfg.ini")
        sunrise = [int(x) for x in config['PLANTCFG']['sunrise'].split(",")]
        sunset = [int(x) for x in config['PLANTCFG']['sunset'].split(",")]
        checkTime = [int(x) for x in config['PLANTCFG']['checkTime'].split(",")]
        dryValue = int(config['PLANTCFG']['dryValue'])
        maxTemp = int(config['PLANTCFG']['maxTemp'])
        maxHumid = int(config['PLANTCFG']['maxHumid'])
        waterVol = int(config['PLANTCFG']['waterVol'])
        fanTime = int(config['PLANTCFG']['fanTime'])
        ################## END DEFAULT READ CONFIG BLOCK #################

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
        if ReadVal[2] <= dryValue and not manual_override["watering"]:
            wtrstatus = autowater(waterVol)
            if wtrstatus != 1:
                set_lcd_color("error")  # Set LCD color to red on error
                raise RuntimeError('UKNOWN FAILURE')
        elif ReadVal[2] > dryValue:
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

# Initialize Plant object from file
load_plant_settings()
last_modified_time = os.path.getmtime("plant_settings.json")
update_schedules()

##############################################
################# ON BOOTUP ##################
##############################################

# This only initializes once on bootup
set_lcd_color("normal")  # Set LCD color to green on bootup

# Start the LCD menu thread immediately
lcd_thread = threading.Thread(target=lcd_menu_thread)
lcd_thread.daemon = True
lcd_thread.start()

#This is now the main running thread, one while loop that spawns subthreads as needed.
while 1:
    ################## START DEFAULT READ CONFIG BLOCK #################
    config.read("grobot_cfg.ini")
    sunrise = [int(x) for x in config['PLANTCFG']['sunrise'].split(",")]
    sunset = [int(x) for x in config['PLANTCFG']['sunset'].split(",")]
    checkTime = [int(x) for x in config['PLANTCFG']['checkTime'].split(",")]
    dryValue = int(config['PLANTCFG']['dryValue'])
    maxTemp = int(config['PLANTCFG']['maxTemp'])
    maxHumid = int(config['PLANTCFG']['maxHumid'])
    waterVol = int(config['PLANTCFG']['waterVol'])
    fanTime = int(config['PLANTCFG']['fanTime'])
    ################## END DEFAULT READ CONFIG BLOCK #################

    currhour = datetime.now().hour
    currminute = datetime.now().minute
    currsecond = datetime.now().second

    currtime = [datetime.now().hour, datetime.now().minute, datetime.now().second]

    #The first case only match function for minutes
    match currminute:
        case 15:
            run_threaded(EveryXX15)
        case 25:
            run_threaded(EveryXX25)
        case 35:
            run_threaded(EveryXX35)
        case _:
            pass
    
    #This one requires matching both hour and minute
    if currhour == sunset[0] and currminute == sunset[1]:
        run_threaded(EverySUNSET)
    if currhour == sunrise[0] and currminute == sunrise[1]:
        run_threaded(EverySUNRISE)
    if currhour == checkTime[0] and currminute == checkTime[1]:
        run_threaded(EverySETTIME)
    
    time2.sleep(60) #This code only use the minute hand so sleeping for 30 second should allow for any change in minute to execute
