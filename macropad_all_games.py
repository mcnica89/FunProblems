"""
Games for a toddler on the MacroPad
"""
from adafruit_MacroPad import MacroPad
import random, time


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
MacroPad.pixels.brightness = 0.1 #default brightness..can be changed in settings menu
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


class Math_Game:
    #Descritpion:
    #A simple game that shows equations like "1+1=" and then will accept only the correct answer
    #the "equals" sign must be pressed to move on to the next level (as per Ezra's request)
    Name = "MATH"
    
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
def MacroPadHappy(n_tones = 4):
    MacroPad.display_image("happy_turtle.bmp")
    for i in range(n_tones):
        MacroPadTone(300 + 150 * i, 0.25)
   
#Play a happy tone and show a picture of a turtle
def MacroPadSad(n_tones = 4):
    #MacroPad.display_image("happy_turtle.bmp")
    for i in range(n_tones):
        MacroPadTone(400 - 150 * i, 0.25)
   
#################
## Main loop code
#################

#List of all the games, this is how the menu works
AllGames = [Memory_Game, Settings_Game, Math_Game, Art_Game, Find_Colors_Game, Off_Game]
MenuChoiceIx = 0

#Encoder positions stored so we can compare to them
LastEncoder = MacroPad.encoder
FirstEncoder = MacroPad.encoder

#Main loop
while True:
    #### GAME MODE ####
    Game = AllGames[MenuChoiceIx]() #initialize the game!
    FirstEncoder = MacroPad.encoder #position of encoder now (for comparison later)
    MacroPadUpdate()
    while True:
        #check and see if we pressed encoder button -> if so go to Menu code
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
    
    #### MENU MODE #####
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
        
        
    
    
        
        

       

