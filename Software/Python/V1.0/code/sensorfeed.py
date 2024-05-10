#Ulnooweg Education Centre - ulnoowegeducation.ca
#Growth enclosure V1.0
#All rights reserved
#
#This function read sensor feeds
#This functions execute without input and return Temp, %RH, and soilRH to main in raw form
#returns text "ERR" on failure
#
##############################################
#MODULE IMPORTS
from diopinsetup import diopinset

##############################################
#Handle the pins definition and sensor definition
diop = diopinset()
s1, s2, s3, s4, s5, s6, b1, ths, sms = diop[0], diop[1], diop[2], diop[3], diop[4], diop[5], diop[6], diop[7], diop[8]

def feedread(): #define feedread function
    try:
        T = ths.temperature
        RH = ths.relative_humidity
        SRH = sms.moisture_read()

        return T, RH, SRH #return tuple of all value
    except Exception:
        return "ERR"