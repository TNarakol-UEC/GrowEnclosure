#Growth Enclosure pi camera python code
#Ulnooweg Education Centre - All rights reserved
#Contact: ulnoowegeducation.ca

#V0.7
########################################

#import important libraries
import subprocess
import datetime
import schedule
import time

#define function to take picture
#Note that we are using subprocess to allow python code to run command line command
def picam_capture():
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") #get current date and time
    directory = "/home/grobot/code/picture"  # specify your directory here
    filename = f"{directory}/camera-image-{timestamp}.jpeg" #construct filename structure using f-string
    subprocess.run(['libcamera-still', '-o', filename]) #capture to filename which already have directory specified using libcamera command line tool

# Schedule the task
schedule.every().hour.at(":00").do(picam_capture)

#Infinite while loop to run the taks
while True:
    schedule.run_pending() #run pending jobs
    time.sleep(1) #sleep for 1 s to ensure while loop do not repeat too much
