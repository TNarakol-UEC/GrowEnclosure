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
import schedule
from datetime import time
import time as time2 #We already import time from datetime so time library is imported as time2
import threading

#Submodules import, these require files to be present in local dir
from sensorfeed import feedread
from watercontrol import autowater
from fancontrol import fanon
from lightcontrol import growlighton, growlightoff
from picamera import picam_capture
from dataout import excelout
from timecheck import is_time_between
from timestrconvert import timestr

#Import plant data used as a basis
from addclass import Plant #This import plant as a class, this is imported globally

##############################################
################# ON BOOTUP ##################
##############################################

#This only initialize once on bootup
#Starts with reading values from sensor
ReadVal = feedread() #T RH SRH in order
if isinstance(ReadVal, tuple) == True: #Check if there is an actual value from feedread
    pass
elif ReadVal == 0: #If returns 0 there is a failure in feedread
    #####
    #TBD# EXECUTION ERROR DISPLAY TO LCD
    #####
    raise RuntimeError('SENSOR FAIL') #Force code to quit and systemd will force it to restart
else: #For any unknown error
    raise RuntimeError('UKNOWN FAILURE')

#Now check if light needs to be on or off
if is_time_between(time(Plant.sunrise[0],Plant.sunrise[1]),time(Plant.sunset[0],Plant.sunset[1])) == True:
    grstatus = growlighton()
    if grstatus == 1:
        pass
    elif grstatus == 0:
        #####
        #TBD# EXECUTION ERROR DISPLAY TO LCD
        #####
        raise RuntimeError('LIGHT FAIL') #Force code to quit and systemd will force it to restart
    else: #For any unknown error
        raise RuntimeError('UKNOWN FAILURE')
elif is_time_between(time(Plant.sunrise[0],Plant.sunrise[1]),time(Plant.sunset[0],Plant.sunset[1])) == False:
    grstatus = growlightoff()
    if grstatus == 1:
        pass
    elif grstatus == 0:
        #####
        #TBD# EXECUTION ERROR DISPLAY TO LCD
        #####
        raise RuntimeError('LIGHT FAIL') #Force code to quit and systemd will force it to restart
    else: #For any unknown error
        raise RuntimeError('UKNOWN FAILURE')
else:
    raise RuntimeError('UKNOWN FAILURE')

#Check if internal humidity or temperature is too high and the fan needs to be on
if ReadVal[0] > Plant.maxTemp or ReadVal[1] > Plant.maxHumid:
    fanstatus = fanon(Plant.fanTime)
    if fanstatus == 1:
        pass
    elif fanstatus == 0:
        #####
        #TBD# EXECUTION ERROR DISPLAY TO LCD
        #####
        pass
    else:
        raise RuntimeError('UKNOWN FAILURE')
elif ReadVal[0] <= Plant.maxTemp and ReadVal[1] <= Plant.maxHumid:
    pass
else:
    raise RuntimeError('UKNOWN FAILURE')

##############################################
##############   SCHEDULED CODE   ############
##############################################

#Convert settime to usable string by schedule
watersettime = timestr(Plant.checkTime)
sunrisesettime = timestr(Plant.sunrise)
sunsetsettime = timestr(Plant.sunset)

def EveryXX15(): #This schedule grouping runs at every quarter of hour
    #This should read value from sensor and turn fan on or off
    #Read value from sensor
    ReadVal = feedread() #T RH SRH in order
    if isinstance(ReadVal, tuple) == True: #Check if there is an actual value from feedread
        pass
    elif ReadVal == 0: #If returns 0 there is a failure in feedread
        #####
        #TBD# EXECUTION ERROR DISPLAY TO LCD
        #####
        raise RuntimeError('SENSOR FAIL') #Force code to quit and systemd will force it to restart
    else: #For any unknown error
        raise RuntimeError('UKNOWN FAILURE')

    #Turn on fan if temp or humidity exceeds the limit 
    if ReadVal[0] > Plant.maxTemp or ReadVal[1] > Plant.maxHumid:
        fanstatus = fanon(Plant.fanTime)
        if fanstatus == 1:
            pass
        elif fanstatus == 0:
            #####
            #TBD# EXECUTION ERROR DISPLAY TO LCD
            #####
            pass
        else:
            raise RuntimeError('UKNOWN FAILURE')
    elif ReadVal[0] <= Plant.maxTemp and ReadVal[1] <= Plant.maxHumid:
        pass
    else:
        raise RuntimeError('UKNOWN FAILURE')

def EverySETTIME(): #This runs every settime read from addclass.py
    #This should read value from sensor and autowater if Soil moisture too low
    #Read value from sensor
    ReadVal = feedread() #T RH SRH in order
    if isinstance(ReadVal, tuple) == True: #Check if there is an actual value from feedread
        pass
    elif ReadVal == 0: #If returns 0 there is a failure in feedread
        #####
        #TBD# EXECUTION ERROR DISPLAY TO LCD
        #####
        raise RuntimeError('SENSOR FAIL') #Force code to quit and systemd will force it to restart
    else: #For any unknown error
        raise RuntimeError('UKNOWN FAILURE')
    
    #Now water plant if soil too dry
    if ReadVal[2] <= Plant.dryValue:
        wtrstatus = autowater(Plant.waterVol)
        if wtrstatus == 1:
            pass
        elif wtrstatus == 2:
            #####
            #TBD# EXECUTION ERROR DISPLAY TO LCD
            #####
            pass
        elif wtrstatus == 0:
            #####
            #TBD# EXECUTION ERROR DISPLAY TO LCD
            #####
            raise RuntimeError('WATER FAIL')
        else:
            raise RuntimeError('UKNOWN FAILURE')
    elif ReadVal[2] > Plant.dryValue:
        pass
    else:
        raise RuntimeError('UKNOWN FAILURE')

def EveryXX25(): #This code runs at every 25 minute mark of the hour
    #Read value from sensor and write it out to excel
    #Read value from sensor
    ReadVal = feedread() #T RH SRH in order
    if isinstance(ReadVal, tuple) == True: #Check if there is an actual value from feedread
        pass
    elif ReadVal == 0: #If returns 0 there is a failure in feedread
        #####
        #TBD# EXECUTION ERROR DISPLAY TO LCD
        #####
        raise RuntimeError('SENSOR FAIL') #Force code to quit and systemd will force it to restart
    else: #For any unknown error
        raise RuntimeError('UKNOWN FAILURE')
    
    #Write data out to excel file
    excelstatus = excelout(ReadVal[0],ReadVal[1],ReadVal[2])
    if excelstatus == 1:
        pass
    elif excelstatus == 2:
        #####
        #TBD# EXECUTION ERROR DISPLAY TO LCD
        #####
        pass
    elif excelstatus == 0:
        #####
        #TBD# EXECUTION ERROR DISPLAY TO LCD
        #####
        raise RuntimeError('DATAOUT FAIL')
    else: #For any unknown error
        raise RuntimeError('UKNOWN FAILURE')

def EveryXX35(): #Runs every 35 minute mark of the hour
    #Take picture with pi camera
    pcamstatus = picam_capture()
    if pcamstatus == 1:
        pass
    elif pcamstatus == 2:
        #####
        #TBD# EXECUTION ERROR DISPLAY TO LCD
        #####
        pass
    elif pcamstatus == 0:
        #####
        #TBD# EXECUTION ERROR DISPLAY TO LCD
        #####
        raise RuntimeError('PICAMERA FAIL')
    else: #For any unknown error
        raise RuntimeError('UKNOWN FAILURE')
    
def EverySUNRISE(): #This should run every sunrise time to turn on the light
    grstatus = growlighton()
    if grstatus == 1:
        pass
    elif grstatus == 0:
        #####
        #TBD# EXECUTION ERROR DISPLAY TO LCD
        #####
        raise RuntimeError('LIGHT FAIL') #Force code to quit and systemd will force it to restart
    else: #For any unknown error
        raise RuntimeError('UKNOWN FAILURE')
    
def EverySUNSET(): #Thus should run every sunset time to turn off light
    grstatus = growlightoff()
    if grstatus == 1:
        pass
    elif grstatus == 0:
        #####
        #TBD# EXECUTION ERROR DISPLAY TO LCD
        #####
        raise RuntimeError('LIGHT FAIL') #Force code to quit and systemd will force it to restart
    else: #For any unknown error
        raise RuntimeError('UKNOWN FAILURE')
       
#Multithreading
def run_threaded(job_func):
    job_thread = threading.Thread(target=job_func)
    job_thread.start()

#Scheduler calls
schedule.every().hour.at(":15").do(run_threaded, EveryXX15)
schedule.every().hour.at(":25").do(run_threaded, EveryXX25)
schedule.every().hour.at(":35").do(run_threaded, EveryXX35)
schedule.every().day.at(watersettime).do(run_threaded, EverySETTIME)
schedule.every().day.at(sunrisesettime).do(run_threaded, EverySUNRISE)
schedule.every().day.at(sunsetsettime).do(run_threaded, EverySUNSET)

while 1:
    schedule.run_pending()
    time2.sleep(1)