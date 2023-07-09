"""
Simple game to press all the keys on the MacroPad
"""
from adafruit_MacroPad import MacroPad
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

###########################################
## Constants used for the games
###########################################
KEYMAP = [7,8,9,4,5,6,1,2,3,-1,0,-2] #maps for the numpad 
#Note: -1 is the blank key and -2 is the equals sign
COLOR_NAMES = RAW_COLORS[::2]
COLORS = RAW_COLORS[1::2]
N_COLORS = len(COLORS)
#

############################################
## Important Global Variables
############################################

MacroPad = MacroPad()
# See https://docs.circuitpython.org/projects/macropad/en/latest/api.html#adafruit_MacroPad.MacroPad.pixels
# for how to use the MacroPad package.

MacroPadTextLines = MacroPad.display_text(text_scale=4)   #this is the lines of text on the macropad

Display = "" #Will be the text shown on the display
KeyColor = [None for i in range(12)] #the color (as a RGB tupl) of each of the 12 key pixels
KeyState = [None for i in range(12)] #the state (as True/False) of each of the 12 key pixels
Volume = 0 #global volume for the game
PixelBrightness = 0.1

class Math_Game:
    #Descritpion:
    #A simple game that shows equations like "1+1=" and then will accept only the correct answer
    #the "equals" sign must be pressed to move on to the next level (as per Ezra's request)
    
    def __init__(self):
        
        self.Name = "Math Game"
        
        global KeyColor, KeyState, Display

        self.correct_eqn_flag = -10 #this flag is set when the correct equation is inputed. 
        # Set to -10 when no correct eqn, and set to the correct key when eqn is corret
        
        self.eqn_list = ['1+1=','1+2=','1+3=','1+4=','1+5=','1+1=','3+1=','4+1=','5+1=','1-1=','2-2=']
        self.eqn_ans_list = [2,3,4,5,6,2,4,5,6,0,0]
        self.num_eqns = len(self.eqn_list)
        self.eqn_choice = random.randrange(self.num_eqns)

        Display = self.eqn_list[self.eqn_choice]
        self.eqn_answer = self.eqn_ans_list[self.eqn_choice]
    
        
        KeyColor = [3]*12  #set all pixels to white #[ random.randrange(N_COLORS) for i in range(12)]
        KeyState = [True for i in range(12)]

        #Deals out random colors in such a way that the number of each color is as balanced as possible
        #available_colors = list(range(n_colors))
        #for i in range(12):
        #    KeyColor[i] = random.choice(available_colors)
        #    available_colors.remove(KeyColor[i])
        #    if not available_colors:
        #        available_colors = list(range(n_colors))


        #KeyState = [True for i in range(12)]
        #TargetColor = random.choice(KeyColor)
        #Display = COLOR_NAMES[TargetColor]
    def key_pressed(self, KeyPressedIx):
        global Display
        if KEYMAP[KeyPressedIx] == self.eqn_answer and self.correct_eqn_flag == -10:
            Display = Display + str(self.eqn_answer)
            self.correct_eqn_flag = KeyPressedIx
            MacroPadUpdate()
        
        #If you press the equals sign (this is KeyPressedIx == 11)
        if KeyPressedIx == 11 and self.correct_eqn_flag != -10 :

            KeyState[self.correct_eqn_flag] = True
            KeyState[KeyPressedIx] = True
            MacroPadUpdate()

            
            for i in range(4):
                rand_n = random.randrange(N_COLORS)
                MacroPad.pixels[KeyPressedIx] = COLORS[rand_n]
                MacroPad.pixels[self.correct_eqn_flag] = COLORS[rand_n]
                if Volume > 0:
                    MacroPad.play_tone(300 + 150 * i, 0.25)
                else:
                    time.sleep(0.25)
                #MacroPadUpdate()
            

                #play_happy(4)
            self.__init__() #Level)
            MacroPadUpdate()


def MacroPadUpdate():
    MacroPadTextLines[0].text = Display
    MacroPadTextLines.show()
    MacroPad.pixels.brightness = PixelBrightness
    for i in range(12):
        if KeyState[i]:
            MacroPad.pixels[i] = COLORS[KeyColor[i]]
        else:
            MacroPad.pixels[i] = (0, 0, 0)


def play_happy(n_tones = 4):
    MacroPad.display_image("happy_turtle.bmp")
    if Volume > 0 :
        for i in range(n_tones):
            MacroPad.play_tone(300 + 150 * i, 0.25)
    else:
        time.sleep(2)


# MacroPadTextLines[2].text = "Encoder switch: {}".format(MacroPad.encoder_switch)

Game = Math_Game()
MacroPadUpdate()
LastEncoder = MacroPad.encoder
KeyPressedIx = 0
MAX_LEVEL = 5
while True:
    
    #if MacroPad.encoder_switch:
    #    print("woo")

    #Allows us to use the rotary encoder to set the led eqn_ans_list
    #Log2Brightness = max(-6,MacroPad.encoder - 4)
    #MacroPad.pixels.initialize = 2 ** Log2Brightness

    #This lets you change the color of the KeyPressedIx using the rotary encoder
    #if LastEncoder != MacroPad.encoder:
    #    KeyState[KeyPressedIx] = True
    #    new_color = (KeyColor[KeyPressedIx] + MacroPad.encoder - LastEncoder) % N_COLORS
    #    KeyColor[KeyPressedIx] = new_color
    #    Display = COLOR_NAMES[new_color]
    #    TargetColor = new_color
    #    LastEncoder = MacroPad.encoder
    #    MacroPadUpdate()


    key_event = MacroPad.keys.events.get()

    if key_event and key_event.pressed:
        
        #KeyPressedIx = key_event.key_number
        Game.key_pressed(key_event.key_number)
        MacroPadUpdate()
        

        # Toggle KeyState and set display to the key color
        #if KeyColor[KeyPressedIx] == TargetColor:
        #   KeyState[KeyPressedIx] = not (KeyState[KeyPressedIx])


        # Update all the keys
        #MacroPadUpdate()


        #Check if we've elimated all of the target or everything

        #CurrentColors = [KeyColor[i] for i in range(12) if KeyState[i]==True ]
        #if not any(KeyState): # If all keys are out, then restart the game
        #    play_happy(4)
        #    Level = min(Level+1, MAX_LEVEL)
        #    eqn_ans_list(Level)
        #    MacroPadUpdate()
        #elif not( TargetColor in CurrentColors ): #if we have eliminated all of TargetColor
        #    play_happy(2)
        #    TargetColor = random.choice(CurrentColors)
        #    Display = COLOR_NAMES[TargetColor]
        #    update()


