#Ulnooweg Education Centre - ulnoowegeducation.ca
#Growth enclosure V1.0
#All rights reserved
#
#This function takes picture using pi camera
#This functions execute without input and export timestamped image to external drive, if not fallback to code/pictures
#returns 0 on failure, 1 on success, 2 onfallback
#code borrowed from cameracode.py in V0.7
#
##############################################
#MODULE IMPORTS
import subprocess
import datetime
import os

#define function to take picture
#Note that we are using subprocess to allow python code to run command line command
def picam_capture():
    try:
        #This part takes an image    
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") #get current date and time
        humantimestamp = datetime.datetime.now().strftime("%H:%M %d/%B/%Y") #Timestamp for image

        #Now this part will determine what directory to use
        directory = "/mnt/grobotextdat/pictures" #This is the main external directory associated with USB
        if os.path.isdir(directory) == True: #check if exist
            returnvar = 1 #set variable to return = 1
            pass #if it is pass
        else: #if not set directory to alternative directory
            returnvar = 2 #set variable to return = 2
            directory = "/home/grobot/code/pictures"  # specify your directory here

        filename = f"{directory}/camera-image-{timestamp}.jpeg" #construct filename structure using f-string
        subprocess.run(['rpicam-still', '-o', filename]) #capture to filename which already have directory specified using libcamera command line tool

        #Now this part adds the timestamp text
        fontsize = '150' #Set timestamp font size in points
        fontcolour = '#DEC305' #Set font colour
        XYpos = '+100+2500' #Set text XY position from top left corner
        #Not put it all together in a convert command
        #Note The command is 'convert filename -pointsize 150 -fill "#DEC035" -annotate +100+2500 'TIMESTAMP' filename'
        subprocess.run(['convert', filename, '-pointsize', fontsize, '-fill', fontcolour, '-annotate', XYpos, humantimestamp, filename])

        return returnvar #return success or failure variables
    except Exception:
        return 0