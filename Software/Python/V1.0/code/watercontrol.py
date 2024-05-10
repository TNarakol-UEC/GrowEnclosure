#Ulnooweg Education Centre - ulnoowegeducation.ca
#Growth enclosure V1.0
#All rights reserved
#
#This function controls watering
#This functions execute with desired volume
#returns 0 on failure, 1 on success, 2 on low water
#
##############################################
#MODULE IMPORTS
import time #need time for sleep function
from diopinsetup import diopinset
import RPi.GPIO as GPIO

##############################################
#Handle the pins definition and sensor definition
diop = diopinset()
s1, s2, s3, s4, s5, s6, ths, sms = diop[0], diop[1], diop[2], diop[3], diop[4], diop[5], diop[6], diop[7]

#Note, pump circuit usually s1

#Setup GPIO10 as input for float switch
#Note that the float switch's reed switch is open in the bottom float position (low water) and closed when in the top position (high water)
#GPIO.setmode(GPIO.BOARD) #use broadcoam GPIO numbers
#GPIO.setup(19, GPIO.IN, pull_up_down=GPIO.PUD_UP) #set pin 19 / GPIO10 as input with pull-up resistor


def autowater(wvol): #define autowater func with water volume input in mL
    try:#check water level
        if GPIO.input(19) == True: #if water level is low
            return 2 #return 2 for low water level
        
        wrate = 28.5 #rate of watering in mL/s
        t = wvol/wrate #time required to water in seconds
        s1.value = True #turns on pump
        time.sleep(t) #sleep for t seconds while pump is on
        s1.value = False #turns off pump
        return 1
    
    except Exception:
        return 0    