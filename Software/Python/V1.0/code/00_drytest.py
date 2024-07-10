from datetime import datetime, time
import time as time2
import random

while 1:
    currminute = datetime.now().minute
    print(datetime.now().time())

    randomt = random.randint(0,70)
    print(randomt)
    time2.sleep(randomt)

    currtickminute = datetime.now().minute

    if currtickminute == currminute: #If we are still in the same minute as initial time check, sleep until minute change
        currticksecond = datetime.now().second #get current second
        tsleep = 61 - currticksecond #subtract current second from 61 to get seconds to sleep until next min
        time2.sleep(tsleep)
    elif currtickminute > currminute: #Immediately rerun loop if current tick is larger than initial time set during update
        pass
    else:
        raise RuntimeError('TIME EXCEPTION') #Time anomaly