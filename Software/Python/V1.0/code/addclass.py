#Ulnooweg Education Centre - ulnoowegeducation.ca
#Growth enclosure V1.0
#All rights reserved
#
#This is data file for use with main.py
#
########################################

import json

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

    def save_to_file(self, filename="plant_settings.json"):
        data = {
            "name": self.name,
            "dryValue": self.dryValue,
            "maxTemp": self.maxTemp,
            "maxHumid": self.maxHumid,
            "waterVol": self.waterVol,
            "checkTime": self.checkTime,
            "sunrise": self.sunrise,
            "sunset": self.sunset,
            "fanTime": self.fanTime
        }
        with open(filename, "w") as f:
            json.dump(data, f)

    @staticmethod
    def load_from_file(filename="plant_settings.json"):
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
                waterVol=600, #water volume in mL
                checkTime=(9,30), # use 24h time!
                sunrise=(7,00), #Cannot use 07 - leading zeroes not permitted in CheckTIme, sunrise, sunset
                sunset=(17,00), #Note: All these are defined as tuple eg. (HH:MM) is a tuple of HH and MM
                fanTime=30
            )

# Initialize Plant object from file
Plant = PlantDef.load_from_file()
