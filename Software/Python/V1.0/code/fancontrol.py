#Ulnooweg Education Centre - ulnoowegeducation.ca
#Growth enclosure V1.0
#All rights reserved
#
#This function controls the right fan
#This functions execute with desired time to turn fan on
#returns 0 on failure, 1 on success
#
##############################################
#MODULE IMPORTS
import time #need time for sleep function
from diopinsetup import diopinset

##############################################
#Handle the pins definition and sensor definition
diop = diopinset()
s1, s2, s3, s4, s5, s6, b1, ths, sms = diop[0], diop[1], diop[2], diop[3], diop[4], diop[5], diop[6], diop[7], diop[8]

#Note, fan circuit usually s3

def fanon(t): #define function to turn on fan for t seconds as input
    try:
        s3.value = True #turns on fan
        time.sleep(t) #sleep for t seconds while fan is on
        s3.value = False #turns off fan
        return 1
    
    except:
        return 0    