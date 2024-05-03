# -*- coding: utf-8 -*-
"""
Created on Mon Jul 10 22:46:57 2023

@author: Joel Beckles

This Script is designed to be run with an Arduino. Its aim is to provide a simple test for 
environments which may ptentially be dangerous to those who may experience epileptic seizures
due to flashing lights. A phototransistor was used for the circuit tested, but is expected that
a photoresistor would work equally well if not better. If the code deems an epiletic seizure possible,
a warning message is printed to that effect.
"""

import pyfirmata
import time
import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq
from scipy.signal import find_peaks

def problematic_freq(freq, min_freq, max_freq):
    """ Returns true if and only if detected signal frequencies lie in problematic range
    """
    if freq >= min_freq and freq <= max_freq:
        return True
    else:
        return False
 
if __name__ == '__main__':
    board = pyfirmata.Arduino('COM3') # enter COM port e.g. "COM3"
    print("Arduino communication successfully initiated")
    ldr = board.get_pin("a:0:o")
    ldr.enable_reporting()
    
    
    # Start iterator to receive input data
    it = pyfirmata.util.Iterator(board)
    it.start()
    
    
    ldr.mode = pyfirmata.INPUT
    
    sample_rate = 100           # 100 Hz
    duration = 10               # total during which samples are collected (10 s)
    N = sample_rate*duration    # number of iterations
    
    ldr_vals = []
    
    # collect ldr readings of light intensity
    for i in range(N):
        # Run loop at frequency set by sample rate
        time.sleep(1/sample_rate)
        
        # Get ldr output value
        ldr_state = ldr.read()
        #print(ldr_state)
        ldr_vals.append(ldr_state)
        
    board.exit()
    print("Arduino communication successfully ended")
    
    times = np.linspace(0, duration, N)
    
    # replace None values with mean value of phototransistor readings
    ldr_vals_mean = np.array([val for val in ldr_vals if val is not None]).mean()
    ldr_vals = np.array([ldr_vals_mean if val is None else val for val in ldr_vals])
    
    # subtract signal mean to get better data for fourier transform
    ldr_vals = ldr_vals - ldr_vals.mean()
    
    # use fourier transform to find component frequencies of signal
    yf = fft(np.array(ldr_vals))
    
    # keep frequencies >= 0
    # adapted from https://docs.scipy.org/doc/scipy/tutorial/fft.html
    xf = fftfreq(N, d=1/sample_rate)[0:N//2] 
                                    
    # plot detected light signal and fourier transorm
    fig, ax = plt.subplots(2, 1, figsize = (7,5))
    
    ax[0].set_ylabel("Light Intensity\n(arbitrary units)")
    ax[0].set_xlabel("Time (s)")
    
    ax[1].set_ylabel("Fourier Transform\nof Light Intensity Signal")
    ax[1].set_xlabel("Frequency (Hz)")
    
    fig.tight_layout()
    
    ax[0].plot(times, ldr_vals)
    ax[1].plot(xf, 2.0/N * np.abs(yf[0:N//2]))
    
    
    
    # find main component frequencies
    fft_signal = np.abs(yf[0:N//2]) # useful data from fft of signal
    peak_indices, properties = find_peaks(fft_signal, 
                                          height=0.5*np.max(fft_signal),
                                          distance=2)
    
    main_freqs = xf[peak_indices]
    print("Peak Frequencies (in Hz): ", main_freqs)


    for freq in main_freqs:
        # Checking for flashing lights in the frequency range of 3 Hz to 30 Hz
        if problematic_freq(freq, 3, 30):
            print("Problematic Frequency detected! Epilepsy seizures possible")
            break
        print("No hazardous flashing detected within specified testing time")