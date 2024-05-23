##TEST FILE
from sensorfeed import feedread
#from lcddisplay import printlcd
#from watercontrol import autowater
#from fancontrol import fanon
#from lightcontrol import growlighton, growlightoff
from picamera import picam_capture
import time

import commentedconfigparser

config = commentedconfigparser.CommentedConfigParser()

#from dataout import excelout

feed  = feedread()

print(feed[0])
print(feed[1])
print(feed[2])

#grstatus1 = growlighton()
#print(grstatus1)
#atwtr = autowater(142.5)
#print(atwtr)
#atfan = fanon(5)
#print(atfan)
#time.sleep(10)
#grstatus2 = growlightoff()
#print(grstatus2)

#########################
#This block to write status to config file
config.read("grobot_cfg.ini")
config['PICAMERA']['CameraSet'] = '0'
with open('grobot_cfg.ini', 'w') as configfile:
    config.write(configfile)

#########################

pcamstatus = picam_capture()
print(pcamstatus)

#excelstatus = excelout(feed[0],feed[1],feed[2])
#print(excelstatus)

#printlcd('text' ,'line2','g')