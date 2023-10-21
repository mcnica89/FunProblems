"""
Games for a toddler on the MacroPad
"""
from adafruit_MacroPad import MacroPad
import random, time

import board
import displayio
import adafruit_imageload

import terminalio
from adafruit_display_text import label
#from adafruit_bitmap_font import bitmap_font

BoardDisplay = board.DISPLAY
SpriteGroup = displayio.Group()
SpriteFlag = False #whether or not to show the sprite

###########################################
## Gloabl sprites used for the Word game
###########################################
#sprite sheet with all the emojis
Sprite_Sheet, Palette = adafruit_imageload.load("spritesheet_4.bmp",
                    bitmap=displayio.Bitmap,
                    palette=displayio.Palette)

EMOJI_WORDS = ["EGG","HOUSE","ROAD","MOON","HELICOPTER","TENT","GONDOLA","MILK","DOLPHIN","SQUIRREL","JEEP","APPLE","CARROT",
                "PLANE","DUCK","CHEESE","PIG","CAT","OCTOPUS","BANANAS","ROBOT","TURTLE","CAR","BEAVER","TRAIN","SUN","TRACTOR",
                "SNAIL","HAT","BIKE","POLICE","FISH","COW","FROG","CRAB","OWL"]
N_Emojis = len(EMOJI_WORDS)

# Create the sprite TileGrid
# this is an array of size 3 with the 3 symbols to show
Sprite = displayio.TileGrid(Sprite_Sheet, pixel_shader=Palette,
                    width = 3, #make it a 3x1 array
                    height = 1,
                    tile_width = 42, #width/height in pixels on the spritesheet
                    tile_height = 42,
                    default_tile = 0)

Sprite.y = 23 #set the y coordinate to be just below the text

#SpriteGroup = displayio.Group() #this group contains everything to display
SpriteGroup.append(Sprite)


max_word_len = max([len(word) for word in EMOJI_WORDS])
font = terminalio.FONT
#font = bitmap_font.load_font("Helvetica-Bold-16.bdf")
SpriteText = label.Label(font, text='-'*max_word_len, color=0xFFFFFF,scale=2) #add in the text S
SpriteText.anchor_point = (0.5, 0.0) #set the anchor to the top-middle of the text so it can be centered
SpriteText.anchored_position = (64, -6) #place the text in the top-middle of the screen
SpriteGroup.append(SpriteText) #add it to the displaygroup



###########################################
## Constants used for the games
###########################################

# List of colors to use for the pixels
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

KEYMAP = [7,8,9,4,5,6,1,2,3,-1,0,-2] #maps for the numpad
#Note: -1 is the blank key and -2 is the equals sign
COLOR_NAMES = RAW_COLORS[::2]
COLORS = RAW_COLORS[1::2]
N_COLORS = len(COLORS)
#
MUSIC_SCALE = [262, 294, 330, 350, 392, 440, 494, 523, 587, 659, 698, 784] #frequencies for a scale

############################################
## Important Global Variables
############################################
# The games works by modifying these global variables

MacroPad = MacroPad()
MacroPad.pixels.brightness = 0.1 #default brightness..can be changed in "settings menu" game
# See https://docs.circuitpython.org/projects/macropad/en/latest/api.html#adafruit_MacroPad.MacroPad.pixels
# for how to use the MacroPad package.

MacroPadTextLines = MacroPad.display_text(text_scale=4)   #this is the lines of text on the macropad

Display = "" #Will be the text shown on the display
Text_Scale = 4
KeyColor = [None for i in range(12)] #the color (as a RGB tupl) of each of the 12 key pixels
KeyState = [None for i in range(12)] #the state (as True/False) of each of the 12 key pixels
Volume = 0 #global volume for the game

############################################
## Each game is a class that has an __init__, a key_pressed, and a encoder_turned function
## Each game also has a "Name" variable which is used to display it in the menu
############################################



class Word_Game:
    Name = "WORDS"
    def __init__(self):
        global MacroPadTextLines, KeyColor, KeyState, Display,SpriteFlag,SpriteGroup

        KeyColor = [5,1,6]*4 #color the keys into columns
        KeyState = [True for i in range(12)]
        MacroPadTextLines = MacroPad.display_text(title="") #set the textscale for the game
        Display = ""
        MacroPadUpdate()

        #randomly deal out 3 emojis
        possible_emoji_list = list(range(N_Emojis)) #list of possible emojis to choose from
        for i in range(3):
            Sprite[i] = random.choice(possible_emoji_list)
            possible_emoji_list.remove(Sprite[i])

        self.emoji_answer_ix = random.choice([0,1,2]) #choose which one is correct randomly!
        SpriteText.text = EMOJI_WORDS[ Sprite[self.emoji_answer_ix] % len(EMOJI_WORDS) ]

        #Sprite[0] = 0 #set the indices according to the spritesheet
        #Sprite[1] = 1
        #Sprite[2] = 2

        SpriteFlag = True #whether or not to show the sprite





        #BoardDisplay.show(SpriteGroup) #display everything on screen!


        #time.sleep(5)

    def encoder_turned(self,EncoderState,EncoderDiff):
        #scroll through all the words that are there!
        #for i in range(3):
        #    Sprite[i] = (EncoderState+i) % len(EMOJI_WORDS)
        #SpriteText.text = EMOJI_WORDS[ Sprite[0] % len(EMOJI_WORDS) ]
        pass


    def key_pressed(self,KeyPressedIx):
        global MacroPadTextLines, KeyColor, KeyState, Display,SpriteFlag,SpriteGroup

        if KeyPressedIx % 3 == self.emoji_answer_ix :
            for i in range(4):
                KeyColor[3*i+self.emoji_answer_ix ] = 2 #set column of keys to Green
            MacroPadUpdate()
            for i in range(3):
                Sprite[i] = Sprite[self.emoji_answer_ix]
            BoardDisplay.show(SpriteGroup)
            MacroPadHappy(4,False)
            self.__init__()
        else:
            for i in range(4):
                KeyColor[3*i+KeyPressedIx] = 0 #set column of keys to Red
            MacroPadUpdate()
            BoardDisplay.show(SpriteGroup)
            MacroPadSad()
            KeyColor = [5,6,8]*4 #color the keys into columns #reset colors
            MacroPadUpdate()


class Settings_Game:
    #This game allows you to change the pixel brightness and set volume on
    Name = "SET UP"
    def __init__(self):
        global MacroPadTextLines, Display, KeyState, KeyColor
        #Set the title and font size
        MacroPadTextLines = MacroPad.display_text(title="Volume=",title_scale=2,text_scale=3,title_length=8) #set the textscale for the game

        if Volume == 0:
            Display = "MUTE"
        else:
            Display = "LOUD"
        KeyState = [True]*12
        KeyColor = [i % N_COLORS for i in range(12)]
        MacroPadUpdate()


    def encoder_turned(self, EncoderState,EncoderDiff):
        #Change brightness using the macropad
        global MacroPad
        MacroPad.pixels.brightness = 2 ** max(-7,EncoderState/2 - 4)
        MacroPadUpdate()

    def key_pressed(self, KeyPressedIx):
        #change the volume using = and blank key
        global Volume, Display
        if KeyPressedIx == 9:
            Volume = 0
            Display = "MUTE"
            MacroPadUpdate()
        if KeyPressedIx == 11 and Volume == 0:
            Volume = 1
            Display = "LOUD"
            MacroPadUpdate()
            MacroPadTone(250,0.25)


class Art_Game:
    #Game that lets you toggle lights on off and change color with the encoder
    Name = "ART"
    def __init__(self):
        global MacroPadTextLines, KeyColor, KeyState, Display
        #Set text size
        MacroPadTextLines = MacroPad.display_text(title="Color:",title_scale=2,text_scale=3,title_length=8) #set the textscale for the game

        #Which key we last pressed

        self.current_key = 0
        KeyColor = [ random.randrange(N_COLORS) for i in range(12)]
        KeyState = [True for i in range(12)]
        Display = COLOR_NAMES[KeyColor[self.current_key]]
        MacroPadUpdate()

    def encoder_turned(self,EncoderState,EncoderDiff):
        #Cycle through all the named colors on the current key
        global KeyColor,Display
        KeyState[self.current_key] = True
        KeyColor[self.current_key] = (KeyColor[self.current_key] + EncoderDiff) % N_COLORS
        Display = COLOR_NAMES[KeyColor[self.current_key]]
        MacroPadUpdate()
    def key_pressed(self,KeyPressedIx):
        #Toggle lights on/off and update which is the current key
        KeyState[KeyPressedIx] = not KeyState[KeyPressedIx]
        self.current_key = KeyPressedIx
        MacroPadUpdate()

class Find_Colors_Game:
    #You have to knock out all the colors of a given target color type
    #when all colors knocked out, you win!
    Name = "COLORS"
    def __init__(self, n_colors = 1):
        self.level = n_colors
        global MacroPadTextLines, KeyColor, KeyState, Display
        MacroPadTextLines = MacroPad.display_text(title="Target:",title_scale=2,text_scale=3,title_length=8) #set the textscale for the game

        #Deals out random colors in such a way that the number of each color is as balanced as possible
        self.available_colors = list(range(n_colors))
        for i in range(12):
            KeyColor[i] = random.choice(self.available_colors)
            self.available_colors.remove(KeyColor[i])
            if not self.available_colors:
                self.available_colors = list(range(n_colors))


        KeyState = [True for i in range(12)]

        #set a random target color
        self.target_color = random.choice(KeyColor)
        Display = COLOR_NAMES[self.target_color]
    def encoder_turned(self,EncoderState,EncoderDiff):
        pass

    def key_pressed(self, KeyPressedIx):
        global KeyColor, KeyState, Display

        # Toggle KeyState if you pressed something of the target_color
        if KeyColor[KeyPressedIx] == self.target_color:
           KeyState[KeyPressedIx] = not (KeyState[KeyPressedIx])
        MacroPadUpdate()

        #Check and see if you got all the lights of one color or all the lights
        self.current_colors = [KeyColor[i] for i in range(12) if KeyState[i]==True ]
        if not any(KeyState): # If all keys are out, then restart the game
            MacroPadHappy(4)
            self.__init__(min(self.level+1, N_COLORS)) #restart with one level higher
            MacroPadUpdate()
        elif not( self.target_color in self.current_colors ): #if we have eliminated all of TargetColor
            MacroPadHappy(2)
            self.target_color = random.choice(self.current_colors)
            Display = COLOR_NAMES[self.target_color]
            MacroPadUpdate()

class Count_Game:
    #Description:
    #A simple game where you count the number of lights that are on
    Name = "COUNT"
    def __init__(self, my_num_range = 1):
        global MacroPadTextLines, KeyColor, KeyState, Display
        MacroPadTextLines = MacroPad.display_text(title="How many?",title_scale=2,text_scale=3) #set the textscale for the game

        self.level = int(my_num_range) #the level sets the size of the possible random numbers
        # this makes it so we start with "easier" to count numbers before going larger
        min_num = max(1,3-self.level)
        max_num = min(9,3+self.level)
        self.count_to = random.randint(min_num,max_num) #choose a random number to count to

        KeyState = [True for i in range(12)]
        KeyColor = [3]*12  #set all to white
        #self.target_color = 3
        #while self.target_color != 3: #choose a random non-white color here
        #    self.target_color = random.randrange(N_COLORS)

        non_white_colors = list(range(N_COLORS))
        non_white_colors.remove(3)
        self.target_color = random.choice(non_white_colors) #choose a random non-white color

        #loop to sample which keys to turn on (random.sample is not implemented in circuitpython)
        self.available_keys = list(range(12))
        for i in range(self.count_to): #turn on self.count_to random keys
            key_to_turn_on = random.choice(self.available_keys)
            self.available_keys.remove(key_to_turn_on)
            KeyColor[key_to_turn_on] = self.target_color

        Display = COLOR_NAMES[self.target_color]
        MacroPadUpdate()

    def encoder_turned(self,EncoderState,EncoderDiff):
        pass

    def key_pressed(self, KeyPressedIx):
        global Display, KeyState

        #if you press right answer for the first time now
        if KEYMAP[KeyPressedIx] == self.count_to:
            MacroPadHappy()
            self.__init__(self.level+1)



class Math_Game:
    #Descritpion:
    #A simple game that shows equations like "1+1=" and then will accept only the correct answer
    #the "equals" sign must be pressed to move on to the next level (as per Ezra's request)
    Name = "PLUS"

    def __init__(self):
        global MacroPadTextLines, KeyColor, KeyState, Display
        MacroPadTextLines = MacroPad.display_text(text_scale=4) #set the textscale for the game

        self.correct_eqn_flag = -10 #this flag is set when the correct equation is inputed.
        # Set to -10 when no correct eqn, and set to the correct key when eqn is corret

        #all possible eqns and answers listed here
        self.eqn_list = ['1+1=','1+2=','1+3=','1+4=','1+5=','1+1=','3+1=','4+1=','5+1=','1-1=','2-2=']
        self.eqn_ans_list = [2,3,4,5,6,2,4,5,6,0,0]
        self.num_eqns = len(self.eqn_list)
        self.eqn_choice = random.randrange(self.num_eqns)

        Display = self.eqn_list[self.eqn_choice]
        self.eqn_answer = self.eqn_ans_list[self.eqn_choice]


        KeyColor = [3]*12  #set all pixels to white #[ random.randrange(N_COLORS) for i in range(12)]
        KeyState = [True for i in range(12)]

    def encoder_turned(self,EncoderState,EncoderDiff):
        pass

    def key_pressed(self, KeyPressedIx):
        global Display, KeyState

        #if you press right answer for the first time now
        if KEYMAP[KeyPressedIx] == self.eqn_answer and self.correct_eqn_flag == -10:
            Display = Display + str(self.eqn_answer)
            self.correct_eqn_flag = KeyPressedIx
            KeyColor[KeyPressedIx] = 2 #set current key to green
            KeyColor[11] = 2 #set = key to green
            MacroPadUpdate()

        #If you press the equals sign (this is KeyPressedIx == 11)
        # check and see if you got the right answer before via the eqn_flag
        if KeyPressedIx == 11 and self.correct_eqn_flag != -10 :

            KeyState = [False for i in range(12)]
            MacroPadUpdate()
            KeyState[self.correct_eqn_flag] = True
            KeyState[KeyPressedIx] = True


            for i in range(4): #version of Happy that dances colors and plays sound
                rand_n = random.randrange(N_COLORS)
                MacroPad.pixels[KeyPressedIx] = COLORS[rand_n]
                MacroPad.pixels[self.correct_eqn_flag] = COLORS[rand_n]
                MacroPadTone(300 + 150 * i, 0.15)
                MacroPadUpdate()

            self.__init__() #restart the game!
            MacroPadUpdate()

class Memory_Game:
    #Classic memory game but with "hints"
    Name = "MEMORY"

    #Play a sound and light up the key
    def play_key(k,sound_len=0.25,pause_len=0.1):
        MacroPad.pixels[k] = COLORS[k % N_COLORS]
        MacroPadTone(MUSIC_SCALE[k], sound_len)
        MacroPad.pixels[k] = (0,0,0)
        time.sleep(pause_len)

    #Add a random key to the memory sequence
    def make_random():
        return random.randrange(0,9)

    #Play the whole sequence
    def play_mem_seq(self,sound_len=0.25,pause_len=0.1):
        for k in self.mem_seq:
            Memory_Game.play_key(k,sound_len,pause_len)

    def __init__(self):
        global MacroPadTextLines, KeyColor, KeyState, Display
        MacroPadTextLines = MacroPad.display_text(title="Hints:",title_scale=2,text_scale=2,title_length=8) #set the textscale for the game

        #initialize with one key
        self.mem_seq = [Memory_Game.make_random()] #initialize memory sequence to one number
        self.mem_seq_remaining = self.mem_seq.copy() #what is remaining to be pressed in the sequence

        Display = "".join([str(KEYMAP[x]) for x in self.mem_seq]) #convert list to ints and join it
        MacroPadUpdate()
        self.play_mem_seq()

    def key_pressed(self, KeyPressedIx):
        global Display, KeyState
        Memory_Game.play_key(KeyPressedIx)

        if KeyPressedIx == self.mem_seq_remaining[0]: #if its correct
            self.mem_seq_remaining.pop(0) #remove from remaning list

            if not self.mem_seq_remaining: #check if its empty! if so next round!
                MacroPadHappy(2)
                if len(self.mem_seq) > 9: #if length is >9, then restart at 1
                    MacroPadHappy(4)
                    self.mem_seq = []

                self.mem_seq.append(Memory_Game.make_random()) #add another element
                Display = "".join([str(KEYMAP[x]) for x in self.mem_seq]) #set display
                MacroPadUpdate()
                self.mem_seq_remaining = self.mem_seq.copy()
                self.play_mem_seq()

        else: #if incorrect!
            MacroPadSad(2)
            self.mem_seq_remaining = self.mem_seq.copy() #start with nothing
            self.play_mem_seq() #replay the sequence


    def encoder_turned(self,_,__):
        self.play_mem_seq()




class Off_Game:
    # "Turns off" the macropad by putting it into an infinite loop
    Name = "OFF"
    def __init__(self):
        global MacroPadTextLines, KeyColor, KeyState, Display
        MacroPadTextLines = MacroPad.display_text(text_scale=3) #set the textscale for the game
        Display = "BYE BYE"
        MacroPadUpdate()
        time.sleep(2)
        Display = ""
        MacroPadUpdate()

        MacroPad.red_led = False
        self.is_on = False

    def encoder_turned(self,_,__):
        pass

    def key_pressed(self,KeyPressedIx):
        pass



#Function that updates the actual colors using the global variables
def MacroPadUpdate():
    MacroPadTextLines[0].text = Display
    MacroPadTextLines.show()
    for i in range(12):
        if KeyState[i]:
            MacroPad.pixels[i] = COLORS[KeyColor[i]]
        else:
            MacroPad.pixels[i] = (0, 0, 0)

#Play a tone (but check volume first!)
def MacroPadTone(freq_hz,time_s):
    if Volume > 0:
        MacroPad.play_tone(freq_hz, time_s)
    else:
        time.sleep(time_s)

#Play a happy tone and show a picture of a turtle
def MacroPadHappy(n_tones = 4,show_image=True):
    if show_image:
        MacroPad.display_image("happy_turtle.bmp")
    for i in range(n_tones):
        MacroPadTone(300 + 150 * i, 0.25)

#Play a happy tone and show a picture of a turtle
def MacroPadSad(n_tones = 3):
    #MacroPad.display_image("happy_turtle.bmp")
    for i in range(n_tones):
        MacroPadTone(450 - 150 * i, 0.25)

#################
## Main loop code
#################

#List of all the games, this is how the menu works
AllGames = [Word_Game, Count_Game, Memory_Game, Settings_Game, Math_Game, Art_Game, Find_Colors_Game, Off_Game]
MenuChoiceIx = 0

#Encoder positions stored so we can compare to them
LastEncoder = MacroPad.encoder
FirstEncoder = MacroPad.encoder


#this is used to flash the lights periodically in order to keep the battery from turning off automatically
#LightFlashLastTime = time.monotonic()
#LightFlashIntervalSec = 20 #number of seconds between light flashes

MacroPad.red_led = True

#Main loop
while True:
    #### GAME MODE ####
    Game = AllGames[MenuChoiceIx]() #initialize the game!
    FirstEncoder = MacroPad.encoder #position of encoder now (for comparison later)
    MacroPadUpdate()
    while True:
        #check and see if we pressed encoder button -> if so go to Menu code

        if SpriteFlag==True:
            BoardDisplay.show(SpriteGroup)
            #BoardDisplay.refresh()

        MacroPad.encoder_switch_debounced.update()
        if MacroPad.encoder_switch_debounced.pressed: #loop until encoder pressed (then go to Menu Mode):
            break

        #check for keypresses and send them to game
        key_event = MacroPad.keys.events.get()
        if key_event and key_event.pressed:
            Game.key_pressed(key_event.key_number)

        #check for encoder movement and send them to game
        if LastEncoder != MacroPad.encoder:
            Game.encoder_turned(MacroPad.encoder - FirstEncoder, MacroPad.encoder - LastEncoder)
            LastEncoder = MacroPad.encoder

        #this loop manual flashes all th elights every few seconds to keep the battery from turnin off
        #if time.monotonic() - LightFlashLastTime > LightFlashIntervalSec and MacroPad.red_led == True: #if still on do this!
        #    old_brightness = MacroPad.pixels.brightness
        #    MacroPad.pixels.brightness = 1.0
        #    for i in range(12):
        #        MacroPad.pixels[i] = (255, 255, 255)
        #    time.sleep(0.01)
        #    MacroPad.pixels.brightness = old_brightness
        #    MacroPadUpdate() #reset everything
        #    LightFlashLastTime = time.monotonic()




    #### MENU MODE #####

    #reset away from image based games
    SpriteFlag = False #turn off displaying the sprite

    MacroPadTextLines = MacroPad.display_text(title="Menu:",title_scale=2,text_scale=3,title_length=8)
    Display = AllGames[MenuChoiceIx].Name
    KeyState = [False]*12
    FirstEncoder = MacroPad.encoder
    MacroPadUpdate()

    while True: #Menu loop - loop until encoder pressed (then go to Game mode)
        if LastEncoder != MacroPad.encoder: #check for encoder movement
            #move menu choice according to encoder
            MenuChoiceIx = (MacroPad.encoder - FirstEncoder)  % len(AllGames)
            Display = AllGames[MenuChoiceIx].Name #set display to game name
            MacroPadUpdate()
            LastEncoder = MacroPad.encoder

        MacroPad.encoder_switch_debounced.update() #check for encoder pressed to go to playing game
        if MacroPad.encoder_switch_debounced.pressed:
            break









