#
#Code for adafruit macropad games
#
from adafruit_macropad import MacroPad
#import math

macropad = MacroPad()
# See https://docs.circuitpython.org/projects/macropad/en/latest/api.html#adafruit_macropad.MacroPad.pixels
# for how to use the MacroPad package.

text_lines = macropad.display_text(text_scale=3) #title="MacroPad Info")

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
print(COLORS)

#for i in range(12):
#    macropad.pixels[i] = (255,32+10*i,0)
    
#while True:
#    pass
key_brightness = [0.5 for i in range(12)]
key_state = [False for i in range(12)]

log2_brightness = 0

display = ""

while True:
    key_event = macropad.keys.events.get()
    if key_event and key_event.pressed:
        key_num = key_event.key_number
        key_state[key_num] = not(key_state[key_num])
        display = COLOR_NAMES[key_num]
        text_lines[0].text = display #"Br:{}".format(log2_brightness)
        #text_lines[2].text = "Encoder switch: {}".format(macropad.encoder_switch)
        text_lines.show()
        for key_num in range(len(COLORS)):
            if key_state[key_num]:
                macropad.pixels[key_num] = COLORS[key_num]
            else:
                macropad.pixels[key_num] = (0,0,0) 
    

    
    
     
    #text_lines[0].text = "{}".format(COLOR_NAMES[key_num])
    log2_brightness = macropad.encoder - 2
    macropad.pixels.brightness = 2**log2_brightness
    
