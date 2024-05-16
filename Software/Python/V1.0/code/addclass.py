#Ulnooweg Education Centre - ulnoowegeducation.ca
#Growth enclosure V1.0
#All rights reserved
#
#This is data file for use with main.py
#
########################################

class PlantDef:
    def __init__(self, name, dryValue, maxTemp, maxHumid, waterVol, checkTime, sunrise, sunset, fanTime):
        self.name       = name # string of plants name
        self.dryValue   = dryValue # dry threashold for autowatering to kick in
        self.maxTemp    = maxTemp # warm threashold for turning on the ventillation fan
        self.maxHumid   = maxHumid # RH threashold for turning on the ventillation fan
        self.waterVol   = waterVol # ammount of water added during autowatering [mL]
        self.checkTime  = checkTime # time that the soil moisture is checked (hh,mm)
        self.sunrise    = sunrise # time that the grow light turns on (hh,mm)
        self.sunset     = sunset # time that the grow light turns off (hh,mm)
        self.fanTime    = fanTime # time that the fan should be on (seconds)

#########################################################

Plant = PlantDef(
    name      = 'Default Plant',
    dryValue  = 800,
    maxTemp   = 30,
    maxHumid  = 90,
    waterVol  = 600, #water volume in mL
    checkTime = (9,30), # use 24h time!
    sunrise   = (7,00), #Cannot use 07 - leading zeroes not permitted in CheckTIme, sunrise, sunset
    sunset    = (17,00), #Note: All these are defined as tuple eg. (HH:MM) is a tuple of HH and MM
    fanTime   = 30
    )