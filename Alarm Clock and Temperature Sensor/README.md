# Project Summary

This Python script uses pyFirmata to communicate with an Arduino.
Along with the relevant circuit setup, it creates a clock on an 
LCD display, and also measures and displays temperature.

The alarm is stopped by holding a button until the music stops, at which point 
the user is greeted by a text to speech message which includes what day it is.
If this button is pressed outside of the alarm time, music is played depending on
the ambient temperature. If the temperature is considered warm, upbeat music is played.
If the temperature is cool, calming music is played. Screen brightness is controlled by a rotational variable resistor.

Note that, for simplicity, laptop speakers are used for audio output here. The exact music files used for this project are included here for completeness.

## Circuit Setup
Non-Trivial Components Required:
- Rotational Variable Resistor
- 16x2 LCD Arduino Screen (comes in standard Arduino starter kit)
![Alarm Clock Setup](https://github.com/JoelANB/Arduino-Projects/assets/60829930/fd6a4604-1d16-4fc0-a90f-fe7460f2f65b)

## Music Credit
- Calming music credits:
Aqua Euphoria (with Lucentia) (432 Hz) by Spheriá | https://soundcloud.com/spheriamusic
Music promoted by https://www.chosic.com/free-music/all/
Creative Commons CC BY-SA 3.0
https://creativecommons.org/licenses/by-sa/3.0/

- Upbeat msuic credits:
Feel Good by MusicbyAden | https://soundcloud.com/musicbyaden
Music promoted by https://www.chosic.com/free-music/all/
Creative Commons CC BY-SA 3.0
https://creativecommons.org/licenses/by-sa/3.0/

- Alarm music credits:
Pixabay user GregorQuendel, taken from https://pixabay.com/sound-effects/cinematic-music-sketches-11-cinematic-percussion-sketch-116186/ 
