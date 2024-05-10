#Ulnooweg Education Centre - ulnoowegeducation.ca
#Growth enclosure V1.0
#All rights reserved
#
#This function display texts on lcd screen (Adafruit 1110)
#This functions execute with text_line1, text_line2, and colour input
#It display error message on screen on failure and returns 0
#
##############################################
#MODULE IMPORTS
#BLINKA
import board
import busio

#ADDITIONAL BLINKA
import adafruit_character_lcd.character_lcd_rgb_i2c as character_lcd

##############################################

#Define LCD
lcd_columns = 16
lcd_rows = 2
i2c = busio.I2C(board.SCL, board.SDA)
lcd = character_lcd.Character_LCD_RGB_I2C(i2c, lcd_columns, lcd_rows)
lcd.cursor = False

#This function recieve text1 and text2 input for line 1 and line 2 (16 char each) and colour as a text: r g or b
def printlcd(text1, text2, colour_text): #define lcddisplay function to display text1 and text2 as line 1 and 2
    try:
        #Set colour based on incoming text
        if colour_text == 'r':
            lcd.color = [100, 0, 0]
        elif colour_text == 'g':
            lcd.color = [0,100,0]
        elif colour_text == 'b':
            lcd.color = [0,0,100]
        else:
            lcd.color = [100, 0, 0]
            lcd.cursor_position(0,0)
            lcd.message = "ERROR:"
            lcd.cursor_position(0,1)
            lcd.message = "LCD COLOUR FAIL"
            raise RuntimeError('LCD_COLOUR_ERROR')
        
        #Display output to lcd
        lcd.clear()
        lcd.cursor_position(0,0)
        lcd.message = text1
        lcd.cursor_position(0,1)
        lcd.message = text2
        return
    except Exception:
        return 0