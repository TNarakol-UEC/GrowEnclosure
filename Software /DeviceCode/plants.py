# Plant Growth Enclosure Controller - Rapsberry Pi Pico W
# Chris Seymour, 2023
#########################################################

class Plant:
    def __init__(self, name, dryValue, maxTemp, maxHumid, waterVol, checkTime, sunrise, sunset):
        self.name       = name # string of plants name
        self.dryValue   = dryValue # dry threashold for autowatering to kick in
        self.maxTemp    = maxTemp # warm threashold for turning on the ventillation fan
        self.maxHumid   = maxHumid # RH threashold for turning on the ventillation fan
        self.waterVol   = waterVol # ammount of water added during autowatering [mL]
        self.checkTime  = checkTime # time that the soil moisture is checked (hh,mm)
        self.sunrise    = sunrise # time that the grow light turns on (hh,mm)
        self.sunset     = sunset # time that the grow light turns off (hh,mm

#########################################################

testPlant = Plant(
    name      = 'testPlant',
    dryValue  = 512,
    maxTemp   = 30,
    maxHumid  = 90,
    waterVol  = 600,
    checkTime = (12,00),
    sunrise   = (09,30),
    sunset    = (16,30)
    )

