"""
Simple game to press all the keys on the MacroPad
"""
from adafruit_macropad import MacroPad
import random, time

#
RAW_COLORS = [
    "RED",
    (255, 0, 0),
    "BLUE",
    (0, 32, 255),
    "GREEN",
    (0, 255, 0),
    "WHITE",
    (255, 255, 255),
    "YELLOW",
    (255, 200, 0),
    "PINK",
    (255, 16, 128),
    "ORANGE",
    (255, 64, 0),
    "PURPLE",
    (64, 0, 255),
    "TEAL", #This is actually "CYAN" but kids know TEAL more
    (0,255,255),
]

COLOR_NAMES = RAW_COLORS[::2]
COLORS = RAW_COLORS[1::2]
N_COLORS = len(COLORS)
#
macropad = MacroPad()
# See https://docs.circuitpython.org/projects/macropad/en/latest/api.html#adafruit_macropad.MacroPad.pixels
# for how to use the MacroPad package.
text_lines = macropad.display_text(text_scale=3)   # title="MacroPad Info")
#
#

Display = ""
KeyColor = [None for i in range(12)]
KeyState = [None for i in range(12)]
TargetColor = None
Volume = 1
Level = 1

def initialize(n_colors = N_COLORS):
    global KeyColor, KeyState, Display, TargetColor
    Display = ""
    cols = [i % n_colors for i in range(12)]
    print(cols)

    #KeyColor = [random.randrange(n_colors) for i in range(12)]

    #Deals out random colors in such a way that the number of each color is as balanced as possible
    available_colors = list(range(n_colors))
    for i in range(12):
        KeyColor[i] = random.choice(available_colors)
        available_colors.remove(KeyColor[i])
        if not available_colors:
            available_colors = list(range(n_colors))


    KeyState = [True for i in range(12)]
    TargetColor = random.choice(KeyColor)
    Display = COLOR_NAMES[TargetColor]

def update():
    text_lines[0].text = Display
    text_lines.show()
    for i in range(12):
        if KeyState[i]:
            macropad.pixels[i] = COLORS[KeyColor[i]]
        else:
            macropad.pixels[i] = (0, 0, 0)


def play_happy(n_tones = 4):
    macropad.display_image("happy_turtle.bmp")
    if Volume > 0 :
        for i in range(n_tones):
            macropad.play_tone(300 + 150 * i, 0.25)
    else:
        time.sleep(2)


# text_lines[2].text = "Encoder switch: {}".format(macropad.encoder_switch)


initialize(Level)
update()
LastEncoder = macropad.encoder
LastKeyPressed = 0
MAX_LEVEL = 5
while True:

    #Allows us to use the rotary encoder to set the led brightness
    #Log2Brightness = max(-6,macropad.encoder - 4)
    #macropad.pixels.brightness = 2 ** Log2Brightness
    
    #This lets you change the color of the LastKeyPressed using the rotary encoder
    if LastEncoder != macropad.encoder:
        KeyState[LastKeyPressed] = True
        new_color = (KeyColor[LastKeyPressed] + macropad.encoder - LastEncoder) % N_COLORS
        KeyColor[LastKeyPressed] = new_color
        Display = COLOR_NAMES[new_color]
        TargetColor = new_color
        LastEncoder = macropad.encoder
        update()
    

    key_event = macropad.keys.events.get()

    if key_event and key_event.pressed:
        LastKeyPressed = key_event.key_number
        
        
        # Toggle KeyState and set display to the key color
        if KeyColor[LastKeyPressed] == TargetColor:
           KeyState[LastKeyPressed] = not (KeyState[LastKeyPressed])


        # Update all the keys
        update()


        #Check if we've elimated all of the target or everything
        
        CurrentColors = [KeyColor[i] for i in range(12) if KeyState[i]==True ]
        if not any(KeyState): # If all keys are out, then restart the game
            play_happy(4)
            Level = min(Level+1, MAX_LEVEL)
            initialize(Level)
            update()
        elif not( TargetColor in CurrentColors ): #if we have eliminated all of TargetColor
            play_happy(2)
            TargetColor = random.choice(CurrentColors)
            Display = COLOR_NAMES[TargetColor]
            update()


