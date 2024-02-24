#include <TFT_eSPI.h>
#include <SD.h>
#include <TouchDrvCSTXXX.hpp>
#include "utilities.h"
#include "JpgFunction.h"
#include "bigFont.h"
#include "NotoSansBold15.h"

//CONSTRUCTORS::::::::::::::::::::::::::::::::
TFT_eSPI tft = TFT_eSPI();
TFT_eSprite spr = TFT_eSprite(&tft);

TouchDrvCSTXXX touch;
int16_t x[5], y[5];

//COLORS::::::::::::::::::::::::::::::::::::::
#define col1 0x0228
#define col_red 0xD000
#define col_green 0x0F60
#define blck TFT_BLACK

//VARIABLES:::::::::::::::::::::::::::::::::::
bool debounce=0;
String txt="";
int txt_color = TFT_WHITE;
char *filename = (char *)malloc(32); //"/1.jpg";
int xpos[3]={0,74,148};
int ypos[4]={184,258,332,406};

// Array that holds the id's of the 5 buttons to be displayed

#define NUM_BUTTONS 5
int button_id[5] = {1,2,3,4,5};
int button_color[5] = {0x0228,0x0228,0x0228,0x0228,0x0228};
bool button_name_revealed[5] = {false,false,false,false,false};

#define NUM_EMOJIS 37
String emoji_names[37] = {"Truck","Streetcar","Police Car","Snowman","Umbrella","Coffee","Keyboard","Sad","Heart","Anchor","Scissors","Gear","Snowflake","Airplane","Robot","Alien","Ghost","Zombie","Family","Eye","Tongue","Bone","Robot Arm","Footprints","Brain","Monkey","Dog","Fox","Raccoon","Cat","Lion","Tiger","Horse","Unicorn","Zebra","Cow","Pig"};

// number of buttons
int answer_button = 0;

// Height+width of the square buttons
#define BUTTON_SIZE 92
#define BUTTON_BUFF 4

#define EMOJI_SIZE 72
#define EMOJI_BUFF_X 6
#define EMOJI_BUFF_Y 9


void setBrightness(uint8_t value)
{
    static uint8_t level = 0;
    static uint8_t steps = 16;
    if (value == 0) {
        digitalWrite(BOARD_TFT_BL, 0);
        delay(3);
        level = 0;
        return;
    }
    if (level == 0) {
        digitalWrite(BOARD_TFT_BL, 1);
        level = steps;
        delayMicroseconds(30);
    }
    int from = steps - level;
    int to = steps - value;
    int num = (steps + to - from) % steps;
    for (int i = 0; i < num; i++) {
        digitalWrite(BOARD_TFT_BL, 0);
        digitalWrite(BOARD_TFT_BL, 1);
    }
    level = value;
}

static int jpegDrawCallback(JPEGDRAW *pDraw)
{   
  spr.pushImage(pDraw->x, pDraw->y,pDraw->iWidth,pDraw->iHeight,pDraw->pPixels);
  return 1;
}

bool initSD()
{
  
    SPI.begin(BOARD_SPI_SCK, BOARD_SPI_MISO, BOARD_SPI_MOSI);
    if (!SD.begin(BOARD_SD_CS)) {
        Serial.println("Card Mount Failed");
  
        return false;
    }
  
    return true;
}

// Checks if the number "num" already appears in the first "legnth" entries of array "array" 
// Used for sampling without replacement to create random choices
int isDuplicate(int num, int *array, int length) {
    for (int i = 0; i < length; ++i) {
        if (array[i] == num) {
            return 1; // Duplicate found
        }
    }
    return 0; // No duplicate found
}


void setup()
{
    // Initialize SD card for use
    initSD(); 

    // Initialize the display
    tft.init();
    tft.fillScreen(TFT_BLACK);
    
    // Rotate the screen into landscape mode
    tft.setRotation(1);

    // Initialize capacitive touch
    touch.setPins(BOARD_TOUCH_RST, BOARD_TOUCH_IRQ);
    touch.begin(Wire, CST226SE_SLAVE_ADDRESS, BOARD_I2C_SDA, BOARD_I2C_SCL);

    // Set the height/width of the whole screen
    // In landscape mode: 480 wide and 222 tall
    spr.createSprite(480,222);
    
    setBrightness(4);
    randomizeButtons();
    draw();
}

void randomizeButtons()
{


  int count = 0;
  int randomNumber = 0;
  while (count < NUM_BUTTONS) {
        randomNumber = rand() % NUM_EMOJIS; // Generate random number between 1 and N_MAX

        // Check if the generated number is already in the array
        if (!isDuplicate(randomNumber, button_id, count)) {
            button_id[count] = randomNumber;
            count++;
        }
    }
  
  //set the "answer" to one of the 5 buttons at random
  randomNumber = rand() % NUM_BUTTONS;
  answer_button = randomNumber;
  txt = emoji_names[button_id[answer_button]];
}

void draw()
  {
    spr.fillSprite(TFT_BLACK);
    spr.setTextColor(txt_color,blck);
    //spr.setTextColor(TFT_WHITE,blck);
    
    spr.loadFont(bigFont);

    spr.setTextDatum(4); //this centers it somehow?
    //
//TL_DATUM = 0 = Top left
//TC_DATUM = 1 = Top centre
//TR_DATUM = 2 = Top right
//ML_DATUM = 3 = Middle left
//MC_DATUM = 4 = Middle centre
//MR_DATUM = 5 = Middle right
//BL_DATUM = 6 = Bottom left
//BC_DATUM = 7 = Bottom centre
//BR_DATUM = 8 = Bottom right

    spr.drawString(txt,480/2,220/4,4); //I don't know what the 4 does here?
    spr.unloadFont();

    
    spr.setTextColor(TFT_WHITE,col1);
    
    // Loop over and draw all the buttons on the bottom row
    for(int i=0;i<NUM_BUTTONS;i++)
    {
      
    // Syntax: spr.fillRoundRect(x,y, size_x,size_y, corner_radius, color);
    spr.fillRoundRect((BUTTON_BUFF+BUTTON_SIZE)*i, 222 - BUTTON_SIZE, BUTTON_SIZE, BUTTON_SIZE, 3, button_color[i]);
    //filename =  "/1.jpg";
    sprintf(filename, "/%d.jpg", button_id[i] );
    jpegDraw( filename, jpegDrawCallback, true, (BUTTON_BUFF+BUTTON_SIZE)*i+EMOJI_BUFF_X, 222 - BUTTON_SIZE+EMOJI_BUFF_Y, EMOJI_SIZE, EMOJI_SIZE);
    if(button_name_revealed[i]){
    
              spr.loadFont(NotoSansBold15);

              spr.setTextDatum(7); //Bottom center datum
              spr.setTextColor(col_red);
              spr.drawString(emoji_names[button_id[i]],(BUTTON_BUFF+BUTTON_SIZE)*i+BUTTON_SIZE/2,220-BUTTON_SIZE,4); //I don't know what the 4 does here?
              spr.unloadFont();
    }
    }

    //for(int yy=0;yy<4;yy++)
    //for(int xx=0;xx<3;xx++)
    //{
    //spr.fillRoundRect(xpos[xx]+2, ypos[yy], 70, 70,5, col1);
    //spr.drawString(buttons[yy][xx],xpos[xx]+37,ypos[yy]+34,4);
    //}





    spr.pushSprite(0,0);
  }



void loop()
{
    uint8_t touched = touch.getPoint(x, y, touch.getSupportTouchPoint());
    //NOTE: The variables x[0],y[0] created in this way are in the original orientation (not the lanfscape mode)
    if (touched){
      if(debounce==0)
      {
      debounce=1;
      // Loop over and draw all the buttons on the bottom row
        for(int i=0;i<NUM_BUTTONS;i++)
        {
          // Syntax: spr.fillRoundRect(x,y, size_x,size_y, corner_radius, color);
          if( y[0] > (BUTTON_BUFF+BUTTON_SIZE)*i && y[0] < (BUTTON_BUFF+BUTTON_SIZE)*i+BUTTON_SIZE)
          {
          if( x[0] < BUTTON_SIZE )
          {
            // Button i is pressed!
            if (i == answer_button){
              //Correct answer!

              for (int j = 0; j < NUM_BUTTONS; j++) {
              button_id[j] = button_id[answer_button]; //change the picture of all buttons to the correct answer
              button_name_revealed[j] = false; //turn off name hints for all buttons
              button_color[j] = col_green;
              }
              
              txt = "! ! ! " + emoji_names[button_id[answer_button]] + " ! ! !" ;
              txt_color = col_green;
              draw();
              delay(2000);
              for (int j = 0; j < NUM_BUTTONS; j++) {
              button_color[j] = col1;
              }
              txt_color = TFT_WHITE;
              randomizeButtons();
            //txt = emoji_names[button_id[i]]; //one_to_five[i]; //emoji_names[button_id[i]]; // #one_to_five[i];
            }else{
              //Not the right answer!
              button_name_revealed[i] = true;
              button_color[i] = col_red;
              txt_color = col_red;
              txt = "X X X X " + emoji_names[button_id[answer_button]] + " X X X X" ;
              draw();
              delay(2000);
              txt_color = TFT_WHITE;
              txt = emoji_names[button_id[answer_button]];
              draw(); 
              
            }
          }
          }
        
          //spr.fillRoundRect(, 222 - BUTTON_SIZE, BUTTON_SIZE, BUTTON_SIZE, 5, col1);
        }
        //for(int yy=0;yy<4;yy++)
        //for(int xx=0;xx<3;xx++)
        //if(x[0]>xpos[xx] && x[0]<xpos[xx]+74 && y[0]>ypos[yy] && y[0]<ypos[yy]+74)
        //  {
        //  if(buttons[yy][xx]=="DEL")
        //  txt="";
        //  else if(buttons[yy][xx]=="<")
        //  txt=txt.substring(0,txt.length()-1);
        //  else
        //  txt=txt+buttons[yy][xx];
        //  }
      //}
    draw();
    }}
    else{debounce=0;}
  
}





