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
s1, s2, s3, s4, s5, s6, ths, sms = diop[0], diop[1], diop[2], diop[3], diop[4], diop[5], diop[6], diop[7]

#Note, pump circuit usually s1

def autowater(wvol): #define autowater func with water volume input in mL
    try:
        wrate = 28.5 #rate of watering in mL/s
        t = wvol/wrate #time required to water in seconds
        ###################
        ###NEEDS FLOATSWITCH HERE and return integer 2
        ##################
        s1.value = True #turns on pump
        time.sleep(t) #sleep for t seconds while pump is on
        s1.value = False #turns off pump
        return 1
    
    except Exception:
        return 0    