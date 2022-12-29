# SPDX-FileCopyrightText: Copyright (c) 2021 Kattni Rembor for Adafruit Industries
#
# SPDX-License-Identifier: Unlicense
"""
Simpletest demo for MacroPad. Displays the key pressed, the relative position of the rotary
encoder, and the state of the rotary encoder switch to the built-in display. Note that the key
pressed line does not appear until a key is pressed.
"""
from adafruit_macropad import MacroPad
import random
#
RAW_COLORS = [
'WHITE', (255,255,255),
'RED', (255,0,0),
'GREEN', (0,255,0),
'BLUE', (0,32,255),
'YELLOW', (255,200,0),
'PINK', (255,16,128),
'ORANGE', (255,64,0),
'PURPLE', (64,0,255)]

COLOR_NAMES = RAW_COLORS[::2]
COLORS = RAW_COLORS[1::2]
N_COLORS = len(COLORS)
#
macropad = MacroPad()
# See https://docs.circuitpython.org/projects/macropad/en/latest/api.html#adafruit_macropad.MacroPad.pixels
# for how to use the MacroPad package.
text_lines = macropad.display_text(text_scale=3) #title="MacroPad Info")
#
KeyColor = [random.randrange(N_COLORS) for i in range(12)]
KeyState = [True for i in range(12)]
#

Display = ""

def update():
    text_lines[0].text = Display 
    text_lines.show()
    for i in range(12):
        if KeyState[i]:
            macropad.pixels[i] = COLORS[KeyColor[i]]
        else:
            macropad.pixels[i] = (0,0,0) 

log2_brightness = -4 #macropad.encoder - 2
macropad.pixels.brightness = 2**log2_brightness
#text_lines[2].text = "Encoder switch: {}".format(macropad.encoder_switch)
        


update()
while True:
    key_event = macropad.keys.events.get()
    if key_event and key_event.pressed:
        n = key_event.key_number
        KeyState[n] = not(KeyState[n])
        Display = COLOR_NAMES[KeyColor[n]]
        update()
        
    
