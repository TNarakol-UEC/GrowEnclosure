#Growth Enclosure lcd output Python code
#Ulnooweg Education Centre - All rights reserved
#Contact: ulnoowegeducation.ca

#V0.7
#For Adrafruit 1110
########################################

#Import important modules
import board
import busio
import adafruit_character_lcd.character_lcd_rgb_i2c as character_lcd

#Define LCD
lcd_columns = 16
lcd_rows = 2
i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)  # Set I2C frequency to 100kHz
lcd = character_lcd.Character_LCD_RGB_I2C(i2c, lcd_columns, lcd_rows)
lcd.cursor = False

#This function recieve text1 and text2 input for line 1 and line 2 (16 char each) and colour as a text: r g or b
def lcddisplay(text1, text2, colour_text): #define lcddisplay function to display text1 and text2 as line 1 and 2
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
    