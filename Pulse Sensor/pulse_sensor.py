# -*- coding: utf-8 -*-
"""
@author: Joel Beckles

This script works with an Arduino UNO to read a person's pulse rate (primarily at the finger).
It then flashes an LED to mimic the pulse data just received. Finally, heart rate is collected 
from the obtained data and message about whether the pulse rate is within normal resting range is
both printed and played on audio using text to speech

"""

import pyfirmata
import time
import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq
from scipy.signal import find_peaks
import serial
import ctypes
import winsound
import win32com
from win32com.client import Dispatch
# See more about wincom32 at https://github.com/mhammond/pywin32
# and about text to speech at https://learn.microsoft.com/en-us/previous-versions/windows/desktop/ms723627(v=vs.85)

if __name__ == '__main__':
    board = pyfirmata.Arduino('COM3') # enter COM port e.g. "COM3"
    time.sleep(3)
    print("Arduino communication successfully initiated")
    pulse_sensor = board.get_pin("a:0:o")
    
    led = board.digital[6]
    led.mode = pyfirmata.OUTPUT
    led.mode = pyfirmata.PWM
    pulse_sensor.enable_reporting()
    
      
    # Start iterator to receive input data
    iterator = pyfirmata.util.Iterator(board)
    iterator.start()
    
    pulse_sensor.mode = pyfirmata.INPUT
    
    sample_rate = 1000          # 1000 Hz (note that this does not necessarily correspond 
                                # to real-time sample rate)
    duration = 10               # total during which samples are collected (10 s)
    
    pulse_sensor_vals = []
    end_time = time.time() + duration
    # collect pulse sensor readings
    while time.time() < end_time:
        # Run loop at frequency set by sample rate
        time.sleep(1/sample_rate)
        
        # Get pulse sensor output value
        pulse_sensor_vals.append(pulse_sensor.read())
        
    
    # replace None values with mean value of pulse sensor readings
    led_vals_mean = np.array([val for val in pulse_sensor_vals if val is not None]).mean()
    led_vals = [led_vals_mean if val is None else val for val in pulse_sensor_vals]
    
    # beep to indicate end of pulse monitoring
    winsound.Beep(440, 500)
    
    # rescale pulse sensor values for better display
    low_val = np.mean(led_vals) - np.std(led_vals)
    high_val = np.mean(led_vals) + np.std(led_vals)
    led_vals = [(val - low_val)/(high_val - low_val) for val in led_vals]
    led_vals = np.clip(led_vals, 0, 1)
    
    # flash LED to mimic pulse monitored
    for val in led_vals:
        time.sleep(0.001)
        led.write(val)
    led.write(0)
    board.exit()
    print("Arduino communication successfully ended")
    
    # plot main graph of pulse rate
    times = np.linspace(0, duration, len(pulse_sensor_vals))
    plt.plot(times, pulse_sensor_vals)
    
    # replace None values with mean value of phototransistor readings
    pulse_sensor_vals_mean = np.array([val for val in pulse_sensor_vals if val is not None]).mean()
    pulse_sensor_vals = np.array([pulse_sensor_vals_mean if val is None else val for val in pulse_sensor_vals])
    
    # calculate heart rate
    peak_indices, properties = find_peaks(pulse_sensor_vals, 
                                          prominence = np.std(pulse_sensor_vals),
                                          # space peaks by about 1/5 of samples per second
                                          distance = (1/5)*len(pulse_sensor_vals)/duration
                                          )
    heart_rate = len(peak_indices)*60/duration # heart rate in bpm
    
    # add plot labels and peaks for heart beats
    plt.title("Photoplethysmograph (PPG) showing Blood Pulses")
    plt.xlabel("Times (s)")
    plt.ylabel("Light Intensity\n(arbitraryy units)")
    plt.plot(times[peak_indices], pulse_sensor_vals[peak_indices], "x", label = "Heart Beat Peaks")
    plt.legend()
    
    # print health message about pulse rate and use text to speech
    print(f"Your heart rate is {heart_rate} BPM")
    Dispatch("SAPI.SpVoice").Speak(f"Your heart rate is {heart_rate} BPM")
    if heart_rate>=60 and heart_rate<=100:
        print("This heart rate is within the normal resting range.")
        Dispatch("SAPI.SpVoice").Speak("This heart rate is within the normal resting range.")
    else:
        print("This heart rate is outside of the normal resting range.")
        Dispatch("SAPI.SpVoice").Speak("This heart rate is outside of the normal resting range.")

    