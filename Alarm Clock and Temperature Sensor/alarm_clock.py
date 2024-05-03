# -*- coding: utf-8 -*-
"""
This Python script uses pyFirmata to communicate with an Arduino.
Along with the relevant circuit setup, it creates a clock on an 
LCD display, and also measures and displays temperature.

The alarm is stopped by holding a button until the music stops, at which point 
the user is greeted by a text to speech message which includes what day it is.
If this button is pressed outside of the alarm time, music is played depending on
the ambient temperature. If the temperature is considered warm, upbeat music is played.
If the temperature is cool, calming music is played. 

@author: Joel Beckles
"""

import pyfirmata
import time
from datetime import datetime
import winsound
# import os
from win32com.client import Dispatch

# Note: this will work on Windows.
# Another audio player may need to be used for other operating systems.

weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

def play_sound(filename, file_duration):
    """ Play sound specified by filename. Song duration must be specified
    """
    #os.system("cinematic-music-sketches-11-cinematic-percussion-sketch-116186.mp3")
    winsound.PlaySound(filename, winsound.SND_FILENAME|winsound.SND_ASYNC)
    time.sleep(file_duration)
    
#play_alarm("cinematic-music-sketches-11.wav", 32)

def get_celsius(sensor_val):
    """ Converts Arduino sensor values to temperature in degrees Celsius
    """
    
    # convert sensor value to actual voltage
    voltage = sensor_val*5
    
    # convert voltage to celsius based on manual and return temperature
    return (voltage-0.5)*100

# function adapted from code at https://gist.github.com/varlen/91170e7cdd61032107e833fce6b7106a 
def lcd_print(board, text):
    """ Print message on lcd
    """
    if text:
        board.send_sysex(pyfirmata.STRING_DATA, pyfirmata.util.str_to_two_byte_iter(text))

def check_alarm(alarm_hour, alarm_min, board, button, sensor_tmp):
    """ Checks whether the alarm time has been reached and plays alarm 
        if time has been reached
    """
    button_not_pressed = button.read()
    now = datetime.now().time()
    
    if now.hour == alarm_hour and now.minute == alarm_min:
        button_not_pressed = True
        
        # loop alarm sound until button is pressed
        while button_not_pressed:
            play_sound("alarm_music.wav", 32)
            button_not_pressed = button.read()
        Dispatch("SAPI.SpVoice").Speak(f"Good day! Enjoy your {weekdays[datetime.today().weekday()]}.")
        time.sleep(60 - 32)
    
    # play calming music if button is pressed outside of alarm time
    
    # play calming music for cool temperature
    elif button_not_pressed == False and sensor_tmp<24:
        Dispatch("SAPI.SpVoice").Speak("Take a moment to relax.")
        lcd_print(board, "Relax...")
        lcd_print(board, " ")
        play_sound("calming_music.wav", 82)
        time.sleep(2)
        
    # play upbeat music for warm temperature
    elif button_not_pressed == False and sensor_tmp>=24:
        Dispatch("SAPI.SpVoice").Speak("Let's have some fun!")
        lcd_print(board, "Have fun!")
        lcd_print(board, " ")
        play_sound("upbeat_music.wav", 158)
        time.sleep(2)

if __name__ == '__main__':
    
    board = pyfirmata.Arduino('COM3') # enter COM port e.g. "COM3"
    print("Arduino communication successfully initiated")
    
    # Start iterator to receive input data
    iterator = pyfirmata.util.Iterator(board)
    iterator.start()
    
    # initialise temperature sesnor and button pins
    tmp_sensor = board.get_pin("a:0:o")
    tmp_sensor.mode = pyfirmata.INPUT
    button = board.digital[7]
    button.mode = pyfirmata.INPUT
    
    time.sleep(3)
    
    ideal_sample_rate = 1       # 1 Hz (note that this does not necessarily correspond 
                                # to real-time sample rate)
    duration = 300              # total during which samples are collected (300 s)
    
    end_time = time.time() + duration
    
    # collect temperature readings
    while time.time() < end_time:
        # run loop at frequency set by sample rate
        time.sleep(1/ideal_sample_rate)
        
        # Get temperature sensor output value
        sensor_val = tmp_sensor.read()
        sensor_tmp = round(get_celsius(sensor_val), 1)
        lcd_print(board, datetime.now().strftime('%d-%m-%Y %H:%M:%S'))
        lcd_print(board, str(sensor_tmp) + " C" )
        check_alarm(17, 12, board, button, sensor_tmp) # set alarm time (24-hour time)
    
    # exit Arduino communication
    lcd_print(board, "Inactive")
    board.exit()
    print("Arduino communication successfully ended")
