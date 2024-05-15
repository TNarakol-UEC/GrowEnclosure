#Ulnooweg Education Centre - ulnoowegeducation.ca
#Growth enclosure V1.0
#All rights reserved
#
#This function is the main function
#This functions should call other submodules/functions and execute them as needed/scheduled
#This functions always run under grobot service
#
##############################################
#MODULE IMPORTS
import asyncio
import schedule

#Submodules import, these require files to be present in local dir
from sensorfeed import feedread
from watercontrol import autowater
from fancontrol import fanon
from lightcontrol import growlighton, growlightoff
from picamera import picam_capture
from dataout import excelout

#Import plant data used as a basis
from addclass import Plant #This import plant as a class

##############################################