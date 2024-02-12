#This is a file to test some programs

import json
import time

#Open file with 'with' statement as json_file. This autoclose file. Load data as a dict into extdata
with open('C:\Storage\VSCode-Git\GrowEnclosure\Software\Python\datastore.json') as json_file:
    extdata = json.load(json_file)
    print(extdata["Adafruit_IO"][0]["AIO_USERNAME"])

print('this is good')
time.sleep(2)
print('10 sec')
raise RuntimeError('ADA_IO_ERROR')