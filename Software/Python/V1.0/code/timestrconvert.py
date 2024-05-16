#Ulnooweg Education Centre - ulnoowegeducation.ca
#Growth enclosure V1.0
#All rights reserved
#
#This function takes touple in format of (xx,yy) that are integers and convert them to string format HH:mm
#This functions execute with touple input
#Failure not tracked
#
##############################################

def timestr(input):
    if input[0] < 10:
        strsettime1 = '0'+str(input[0])
    else:
        strsettime1 = str(input[0])
    if input[1] < 10:
        strsettime2 = '0'+str(input[1])
    else:
        strsettime2 = str(input[1])
    strsettime = strsettime1+':'+strsettime2
    return strsettime