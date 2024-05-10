#Ulnooweg Education Centre - ulnoowegeducation.ca
#Growth enclosure V1.0
#All rights reserved
#
#These functions controls the light
#These functions take no arguments
#returns 0 on failure, 1 on success
#
##############################################
#MODULE IMPORTS
from diopinsetup import diopinset

##############################################
#Handle the pins definition and sensor definition
diop = diopinset()
s1, s2, s3, s4, s5, s6, ths, sms = diop[0], diop[1], diop[2], diop[3], diop[4], diop[5], diop[6], diop[7]

#Note, light circuit usually s2

def growlighton(): #define function to turn on growlight
    try:
        s2.value = True #turns on fan
        return 1
    
    except Exception:
        return 0    

def growlightoff(): #define function to turn off growlight
    try:
        s2.value = False #turns on fan
        return 1
    
    except Exception:
        return 0    