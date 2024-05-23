import board
import time
from datetime import datetime
from adafruit_character_lcd.character_lcd_rgb_i2c import Character_LCD_RGB_I2C
from addclass import Plant  # Ensure this import statement matches your setup

from watercontrol import autowater
from fancontrol import fanon
from lightcontrol import growlighton, growlightoff
from picamera import picam_capture

import commentedconfigparser

config = commentedconfigparser.CommentedConfigParser()

i2c = board.I2C()  # uses board.SCL and board.SDA
lcd = Character_LCD_RGB_I2C(i2c, 16, 2)

def set_lcd_color(status):
    """Set LCD color based on status."""
    if status == "normal":
        lcd.color = [0, 100, 0]  # Green
    elif status == "in_progress":
        lcd.color = [0, 0, 100]  # Blue
    elif status == "error":
        lcd.color = [100, 0, 0]  # Red

def debounce(button):
    """ Debounce a button property """
    button_state = button()  # Initial state
    last_change_time = time.monotonic()
    while True:
        current_time = time.monotonic()
        if button() != button_state:
            last_change_time = current_time
        button_state = button()
        if current_time - last_change_time > 0.1:  # Wait for stable state for 100ms
            break
    return button_state

def adjust_parameter(parameter_name, step, min_val, max_val):
    """General function to adjust a numerical parameter."""
    value = getattr(Plant, parameter_name)
    message = f"{parameter_name}: {value}  "
    lcd.message = message
    while True:
        update = False
        if lcd.up_button:
            debounce(lambda: lcd.up_button)
            value = min(value + step, max_val)
            update = True
        elif lcd.down_button:
            debounce(lambda: lcd.down_button)
            value = max(value - step, min_val)
            update = True
        if update:
            message = f"{parameter_name}: {value}  "
            lcd.message = message
        elif lcd.select_button:
            debounce(lambda: lcd.select_button)
            setattr(Plant, parameter_name, value)
            Plant.save_to_file()  # Save the settings
            message = f"Set to {value}    "
            lcd.message = message
            time.sleep(1)  # Show the set message
            break
        time.sleep(0.2)  # Reduce refresh rate to minimize jitter

def adjust_time_parameter(parameter_name):
    """Function to adjust time parameters (HH:MM)."""
    value = getattr(Plant, parameter_name)
    hours, minutes = value
    message = f"{parameter_name}: {hours:02d}:{minutes:02d}  "
    lcd.message = message
    while True:
        update = False
        if lcd.up_button:
            debounce(lambda: lcd.up_button)
            hours = (hours + 1) % 24
            update = True
        elif lcd.down_button:
            debounce(lambda: lcd.down_button)
            hours = (hours - 1) % 24
            update = True
        elif lcd.right_button:
            debounce(lambda: lcd.right_button)
            minutes = (minutes + 1) % 60
            update = True
        elif lcd.left_button:
            debounce(lambda: lcd.left_button)
            minutes = (minutes - 1) % 60
            update = True
        if update:
            message = f"{parameter_name}: {hours:02d}:{minutes:02d}  "
            lcd.message = message
        elif lcd.select_button:
            debounce(lambda: lcd.select_button)
            setattr(Plant, parameter_name, (hours, minutes))
            Plant.save_to_file()  # Save the settings
            message = f"Set to {hours:02d}:{minutes:02d}  "
            lcd.message = message
            time.sleep(1)  # Show the set message
            break
        time.sleep(0.2)  # Reduce refresh rate to minimize jitter

def display_menu(options, index):
    """Helper function to display menu options with the current selection on the bottom line."""
    lcd.clear()
    lcd.message = f"Select Option:\n{options[index][:16]}"

def edit_settings_menu():
    """Function to navigate and edit settings."""
    options = ['System Time', 'Sunrise Time', 'Sunset Time', 'Irrigation', 'Temp Setpoint', 'Humidity Setpoint', 'Camera Yes/No', 'Back']
    index = 0
    display_menu(options, index)
    while True:
        update = False
        if lcd.up_button:
            debounce(lambda: lcd.up_button)
            index = (index - 1) % len(options)
            update = True
        elif lcd.down_button:
            debounce(lambda: lcd.down_button)
            index = (index + 1) % len(options)
            update = True
        if update:
            display_menu(options, index)
        elif lcd.select_button:
            debounce(lambda: lcd.select_button)
            if options[index] == 'System Time':
                adjust_time_parameter('checkTime')  # Adjust time
            elif options[index] == 'Sunrise Time':
                adjust_time_parameter('sunrise')  # Adjust time
            elif options[index] == 'Sunset Time':
                adjust_time_parameter('sunset')  # Adjust time
            elif options[index] == 'Irrigation':
                irrigation_menu()
            elif options[index] == 'Temp Setpoint':
                adjust_parameter('maxTemp', 1, 0, 50)
            elif options[index] == 'Humidity Setpoint':
                adjust_parameter('maxHumid', 5, 0, 100)
            elif options[index] == 'Camera Yes/No':
                ##########################
                ## NEEDS ERROR HANDLING ##
                ##########################
                config.read("grobot_cfg.ini") #Read the config file
                match config['PICAMERA']['CameraSet']: #Match the config case to toggle between 0 or 1
                    case '0':
                        config['PICAMERA']['CameraSet'] = '1'
                    case '1':
                        config['PICAMERA']['CameraSet'] = '0'
                with open('grobot_cfg.ini', 'w') as configfile: #Write the settings back to config
                    config.write(configfile)
                pass
            elif options[index] == 'Back':
                break
            display_menu(options, index)
            time.sleep(0.5)  # Pause before returning to menu

def irrigation_menu():
    """Function to navigate and edit irrigation settings."""
    options = ['Soil Moist Thresh', 'Water Vol', 'Watering Time', 'Back']
    index = 0
    display_menu(options, index)
    while True:
        update = False
        if lcd.up_button:
            debounce(lambda: lcd.up_button)
            index = (index - 1) % len(options)
            update = True
        elif lcd.down_button:
            debounce(lambda: lcd.down_button)
            index = (index + 1) % len(options)
            update = True
        if update:
            display_menu(options, index)
        elif lcd.select_button:
            debounce(lambda: lcd.select_button)
            if options[index] == 'Soil Moist Thresh':
                adjust_parameter('dryValue', 10, 0, 1000)
            elif options[index] == 'Water Vol':
                adjust_parameter('waterVol', 10, 0, 1000)
            elif options[index] == 'Watering Time':
                adjust_time_parameter('checkTime')  # Adjust time
            elif options[index] == 'Back':
                break
            display_menu(options, index)
            time.sleep(0.5)  # Pause before returning to menu

def manual_control_menu():
    """Function to handle manual controls."""
    options = ['Take Picture Now', 'Water Now', 'Light On Now', 'Fan On Now', 'Back']
    index = 0
    display_menu(options, index)
    while True:
        update = False
        if lcd.up_button:
            debounce(lambda: lcd.up_button)
            index = (index - 1) % len(options)
            update = True
        elif lcd.down_button:
            debounce(lambda: lcd.down_button)
            index = (index + 1) % len(options)
            update = True
        if update:
            display_menu(options, index)
        elif lcd.select_button:
            debounce(lambda: lcd.select_button)
            if options[index] == 'Take Picture Now':
                ##########################
                ## NEEDS ERROR HANDLING ##
                ##########################
                pcamstatus = picam_capture()
                pass
            elif options[index] == 'Water Now':
                ##########################
                ## NEEDS ERROR HANDLING ##
                ##########################
                wtrstatus = autowater(Plant.waterVol)
                pass
            elif options[index] == 'Light On Now':
                ##########################
                ## NEEDS ERROR HANDLING ##
                ##########################
                grstatus = growlighton()
                pass
            elif options[index] == 'Fan On Now':
                ##########################
                ## NEEDS ERROR HANDLING ##
                ##########################
                fanstatus = fanon(Plant.fanTime)
                pass
            elif options[index] == 'Back':
                break
            display_menu(options, index)
            time.sleep(0.5)  # Pause before returning to menu

def main_menu():
    """Function to navigate between different settings."""
    options = ['Edit Settings', 'Manual Control']
    index = 0
    display_menu(options, index)
    while True:
        update = False
        if lcd.up_button:
            debounce(lambda: lcd.up_button)
            index = (index - 1) % len(options)
            update = True
        elif lcd.down_button:
            debounce(lambda: lcd.down_button)
            index = (index + 1) % len(options)
            update = True
        if update:
            display_menu(options, index)
        elif lcd.select_button:
            debounce(lambda: lcd.select_button)
            if options[index] == 'Edit Settings':
                edit_settings_menu()
            elif options[index] == 'Manual Control':
                manual_control_menu()
            display_menu(options, index)
            time.sleep(0.5)  # Pause before returning to menu

def lcd_menu_thread():
    lcd.clear()
    while True:
        current_time = datetime.now().strftime("%H:%M:%S")
        lcd.message = f"{current_time}\nPress Select to start"
        if lcd.select_button:
            debounce(lambda: lcd.select_button)
            main_menu()
            lcd.clear()
        time.sleep(1)  # Refresh the time every second
