#Growth Enclosure main Python code
#Ulnooweg Education Centre - All rights reserved
#Contact: ulnoowegeducation.ca

#NOTE: THIS VERSION IS USING IMPORTED BLINKA LIBRARIES. NATIVE LIBRARIES WILL BE USED IN NEXT REFACTOR.
########################################

#import important library


#Configure global parameters for various options in the code
rateLimit = 30 # Adafruit IO updates per minute
plant = plants.testPlant # which plant are we growing

#Setup pinouts for hardware used
#Current: Raspberry Pi 3 A+ with BCRobotics Irrigation Hat V2
pins = {
    'S1' : board.GP2,
    'S2' : board.GP3,
    'S3' : board.GP4,
    'S4' : board.GP5,
    'S5' : board.GP6,
    'B1' : board.GP11,
    'B2' : board.GP12,
    'B3' : board.GP13,
    'B4' : board.GP14,
    'B5' : board.GP15,
    'QWIIC_SCL' : board.GP17,
    'QWIIC_SDA' : board.GP16
    }