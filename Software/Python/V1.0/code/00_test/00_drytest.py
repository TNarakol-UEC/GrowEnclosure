import time  # need time for sleep function
from diopinsetup import diopinset

while(1):
    diop = diopinset()
    s1, s2, s3, s4, s5, s6, b1, ths, sms = diop[0], diop[1], diop[2], diop[3], diop[4], diop[5], diop[6], diop[7], diop[8]

    print(b1.value)
    time.sleep(5)

##########

# import configparser

# config = configparser.ConfigParser()

# config.read("grobot_cfg.ini")
# settings = {
#     'sunrise': [int(x) for x in config['PLANTCFG']['sunrise'].split(",")],
#     'sunset': [int(x) for x in config['PLANTCFG']['sunset'].split(",")],
#     'checkTime': [int(x) for x in config['PLANTCFG']['checkTime'].split(",")],
#     'dryValue': int(config['PLANTCFG']['dryValue']),
#     'maxTemp': int(config['PLANTCFG']['maxTemp']),
#     'maxHumid': int(config['PLANTCFG']['maxHumid']),
#     'waterVol': int(config['PLANTCFG']['waterVol']),
#     'fanTime': int(config['PLANTCFG']['fanTime'])
# }
# print(settings)
# print(settings['sunset'][0])
# print(settings['dryValue'])

#################

# from datetime import datetime, time
# import time as time2
# import random

# while 1:
#     currminute = datetime.now().minute
#     print(datetime.now().time())

#     randomt = random.randint(0,70)
#     print(randomt)
#     time2.sleep(randomt)

#     currtickminute = datetime.now().minute

#     if currtickminute == currminute: #If we are still in the same minute as initial time check, sleep until minute change
#         currticksecond = datetime.now().second #get current second
#         tsleep = 61 - currticksecond #subtract current second from 61 to get seconds to sleep until next min
#         time2.sleep(tsleep)
#     elif currtickminute > currminute: #Immediately rerun loop if current tick is larger than initial time set during update
#         pass
#     else:
#         raise RuntimeError('TIME EXCEPTION') #Time anomaly