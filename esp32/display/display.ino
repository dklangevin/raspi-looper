    /*
  Example animated analogue meters using a ILI9341 TFT LCD screen

  Needs Font 2 (also Font 4 if using large scale label)

  Make sure all the display driver and pin comnenctions are correct by
  editting the User_Setup.h file in the TFT_eSPI library folder.

  #########################################################################
  ###### DON'T FORGET TO UPDATE THE User_Setup.h FILE IN THE LIBRARY ######
  #########################################################################
*/

#include <TFT_eSPI.h> // Hardware-specific library
#include <SPI.h>
#include "AiEsp32RotaryEncoder.h"

TFT_eSPI tft = TFT_eSPI();       // Invoke custom library

#define TFT_GREY 0x5AEB

#define LOOP_PERIOD 38000 // Display updates every 35 ms

#define WIDTH 320
#define HEIGHT 240

#define PLAY_C 'p'
#define RECORD_C 'r'

#define ROTARY_ENCODER_0_A_PIN 36
#define ROTARY_ENCODER_0_B_PIN 39
#define ROTARY_ENCODER_0_BUTTON_PIN 32
#define ROTARY_ENCODER_1_A_PIN 35
#define ROTARY_ENCODER_1_B_PIN 34
#define ROTARY_ENCODER_1_BUTTON_PIN 33
#define ROTARY_ENCODER_STEPS 4

float ltx = 0;    // Saved x coord of bottom of needle
uint16_t osx = 120, osy = 120; // Saved x & y coords
uint32_t update_time = 0;       // time for next update

int old_analog =  -999; // Value last displayed
int old_digital = -999; // Value last displayed

int value[6] = {0, 0, 0, 0, 0, 0};
int old_value[6] = { -1, -1, -1, -1, -1, -1};
int d = 0;
int bar_percent = 0;

bool play = false;
bool record = false;
char input;
char cstr[1];

uint8_t beats = 3;
uint8_t bpm = 107;
int loop_period;

bool led_on = false;
int encoder_0_val = 0;
int encoder_1_val = 0;
int pot_val;
int bpm_digits;

// Rotary encoder
AiEsp32RotaryEncoder rotaryEncoder0 = AiEsp32RotaryEncoder(ROTARY_ENCODER_0_A_PIN, ROTARY_ENCODER_0_B_PIN, ROTARY_ENCODER_0_BUTTON_PIN, -1, ROTARY_ENCODER_STEPS);
AiEsp32RotaryEncoder rotaryEncoder1 = AiEsp32RotaryEncoder(ROTARY_ENCODER_1_A_PIN, ROTARY_ENCODER_1_B_PIN, ROTARY_ENCODER_1_BUTTON_PIN, -1, ROTARY_ENCODER_STEPS);

void IRAM_ATTR readEncoderISR()
{
    rotaryEncoder0.readEncoder_ISR();
    rotaryEncoder1.readEncoder_ISR();
}

int read_time = millis();
void IRAM_ATTR buttonISR() {
  if(millis()-read_time > 200){
    play = !play;
    read_time = millis();
  }
}

void analogWrite(uint8_t channel, uint32_t value, uint32_t valueMax = 255) {
  // calculate duty, 4095 from 2 ^ 12 - 1
  uint32_t duty = (4095 / valueMax) * min(value, valueMax);

  // write duty to LEDC
  ledcWrite(channel, duty);
}

void setup(void) {
  tft.init();
  tft.setRotation(3);
  Serial.begin(57600); // For debug
  tft.fillScreen(TFT_BLACK);

  // Draw bar outline
  tft.drawLine(20, 65, WIDTH-20, 65, TFT_WHITE);
  tft.drawLine(20, 85, WIDTH-20, 85, TFT_WHITE);
  tft.drawLine(20, 66, 20, 84, TFT_WHITE);
  tft.drawLine(WIDTH-20, 66, WIDTH-20, 84, TFT_WHITE);

  // Draw ticks
  for(int i=0; i<=beats; i++){
    tft.drawLine(20+((WIDTH-40)*i/beats), 86, 20+((WIDTH-40)*i/beats), 96, TFT_WHITE);
  }

  // Draw text
  tft.drawString(String(bpm), 20, 14, 6);
  tft.setTextColor(TFT_GREY);
  tft.drawString("BPM", 105, 30, 4);
  tft.setTextColor(TFT_WHITE);
  tft.drawRightString("0", WIDTH-20, 14, 6);

  // Draw menu
  tft.fillTriangle(13, 125, 13, 135, 18, 130, TFT_WHITE);
  tft.drawString("BACKING TRACK", 25, 120, 4);
  tft.drawString("MODES", 25, 150, 4);
  tft.drawString("SETTINGS", 25, 180, 4);
  
//  tft.drawString("BPM", 40, 60, 5);
  
//  tft.fillRect(20, 20, WIDTH-40, 20, TFT_WHITE);

  update_time = micros(); // Next update time
  
  tft.setTextColor(TFT_WHITE, TFT_BLACK);

  loop_period = (600000*beats)/bpm;

  //ledcSetup(0, 5000, 12);
  //ledcAttachPin(32, 0);
  //analogWrite(0, 255);

  // Rotary encoder 0
  rotaryEncoder0.begin();
  rotaryEncoder0.setup(readEncoderISR);
  rotaryEncoder0.setBoundaries(1, 200, false); //minValue, maxValue, circleValues true|false (when max go to min and vice versa)
  rotaryEncoder0.setAcceleration(250);
  rotaryEncoder0.setEncoderValue(bpm);

  // Rotary encoder 1
  rotaryEncoder1.begin();
  rotaryEncoder1.setup(readEncoderISR);
  rotaryEncoder1.setBoundaries(0, 2, false); //minValue, maxValue, circleValues true|false (when max go to min and vice versa)
  rotaryEncoder1.setAcceleration(250);
  rotaryEncoder1.setEncoderValue(0);

  // Button
  pinMode(33, INPUT_PULLUP);
  attachInterrupt(33, buttonISR, FALLING);
}

void loop() {

  // Recorded loop period
  // T (ms/period) = 35ms/loop * 100loops/period

  // min/beat * sec/min * us/sec * beat/period (ms/period) = us/loop * loops/period (ms/period)
  // 1/BPM * 60 * 1000000 * beats_per_measure = t * 100
  // 1/BPM * 600000 * beats_per_measure = t
  
  // t = 1000 * beats_per_measure * 600/BPM = 600,000 * beats_per_measure/BPM
  // BPM = (beats_per_measure * 1000 * 600) / t
  
  if (update_time <= micros()) {
    update_time = micros() + loop_period;

    input = Serial.read();
    if(input == PLAY_C) play = !play;
    else if(input == RECORD_C) record = !record;

    if(play){
      
      bar_percent += 1;
    
      if(bar_percent >= 100){
        bar_percent = 0;
        tft.fillRect(21, 66, WIDTH-42, 19, TFT_BLACK);
      }
      else {
        tft.fillRect(21, 66, bar_percent*(WIDTH-42)/100, 19, record ? TFT_RED : TFT_WHITE);
      }
  
      itoa((bar_percent/(100.0/beats)) + 1, cstr, 10);
      tft.setTextColor(TFT_WHITE, TFT_BLACK);
      tft.drawRightString(cstr, WIDTH-20, 14, 6);
//
//      analogWrite(0, bar_percent*255/100);
    }

//    Serial.println(analogRead(36));

//    led_on = !led_on;
//    if(led_on) {
//      Serial.println("on");
//      analogWrite(0, 255);
//      }
//    else analogWrite(0, 0);
  }

  if (rotaryEncoder0.encoderChanged())
  {
      encoder_0_val = rotaryEncoder0.readEncoder();
//      Serial.println(encoder_0_val);
      bpm = encoder_0_val;
      bpm_digits = (bpm/100) ? 3 : (bpm/10) ? 2 : 1;
      tft.fillRect(20, 14, 140, 45, TFT_BLACK);
      tft.drawString(String(bpm), 20, 14, 6);
      tft.setTextColor(TFT_GREY);
      tft.drawString("BPM", 20+29*bpm_digits, 30, 4);
      tft.setTextColor(TFT_WHITE);
      loop_period = (600000*beats)/bpm;
  }
  if (rotaryEncoder1.encoderChanged())
  {
      encoder_1_val = rotaryEncoder1.readEncoder();
      Serial.println(encoder_1_val);
      // 120 150 180
      // Clear previous triangle
      for(int i=0; i<3; i++){
        tft.fillTriangle(13, 125+i*30, 13, 135+i*30, 18, 130+i*30, TFT_BLACK);
      }
      tft.fillTriangle(13, 125+encoder_1_val*30, 13, 135+encoder_1_val*30, 18, 130+encoder_1_val*30, TFT_WHITE);
  }

//  pot_val = analogRead(34);
//  analogWrite(0, 255*(pot_val/4096.0));
  
}
