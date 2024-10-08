#Ulnooweg Education Centre - All rights reserved
#Contact: ulnoowegeducation.ca
#Growth Enclosure 
#
#This function check if current time is between set time
#V1.1-DEV
#
#This functions execute with inputs start and end time (and an optional current time). It can also handle time that crosses midnight
#returns True on current time in range, False on out of range
#This code is posted by stackoverflow user https://stackoverflow.com/users/48837/joe-holloway
#https://stackoverflow.com/questions/10048249/how-do-i-determine-if-current-time-is-within-a-specified-range-using-pythons-da
#Note: The time input must be converted from tuple using time(hh,mm) first
#
########################################

#Module Imports
from datetime import datetime, time

##############################################

#Define a function to take in start and end time for comparison, and optional current time
def is_time_between(begin_time, end_time, check_time=None):
    # If check time is not given, default to current UTC time
    check_time = check_time or datetime.now().time() #.time() convert it to same time format as time(hh,mm)
    if begin_time < end_time:
        return check_time >= begin_time and check_time <= end_time
    else: # crosses midnight
        return check_time >= begin_time or check_time <= end_time