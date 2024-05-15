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

##############################################
#Handle the pins definition and sensor definition
diop = diopinset()
s1, s2, s3, s4, s5, s6, b1, ths, sms = diop[0], diop[1], diop[2], diop[3], diop[4], diop[5], diop[6], diop[7], diop[8]

#Note, pump circuit usually s1

def autowater(wvol): #define autowater func with water volume input in mL
    try:#check water level
        #Note that the float switch's reed switch is open in the bottom float position (low water) and closed when in the top position (high water)
        #Note that b1 (GPIO10 / Pin 19) is set with a pull-up resistor
        if b1.value == False:
            pass 
        elif b1.value == True: #if the water level is low
            return 2
        else:
            return 0
    
        wrate = 28.5 #rate of watering in mL/s
        t = wvol/wrate #time required to water in seconds
        s1.value = True #turns on pump
        time.sleep(t) #sleep for t seconds while pump is on
        s1.value = False #turns off pump
        return 1
    
    except:
        return 0    