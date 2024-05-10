from sensorfeed import feedread
#from lcddisplay import printlcd
from watercontrol import autowater
from fancontrol import fanon
from lightcontrol import growlighton, growlightoff
import time

feed  = feedread()

print(feed[0])
print(feed[1])
print(feed[2])

atwtr = autowater(142.5)
print(atwtr)
atfan = fanon(5)
print(atfan)
grstatus1 = growlighton()
print(grstatus1)
time.sleep(10)
grstatus2 = growlightoff()
print(grstatus2)

#printlcd('text' ,'line2','g')