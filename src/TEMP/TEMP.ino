// this makes teensy compatible with
// rewire-keyboard script (via pygame)

// not sure if we need both of these includes (check?)
#include <algorithm>
#include <math.h>

// set up analog input and output parameters
int ANALOG_READ_RESOLUTION = 13; // 13 bit analog to digital on teensy
int MAX_ANALOG_IN = 8192;
int MAX_ANALOG_OUT = 1023;

// set up internal variables
int inputPin = A14; // select the input pin for EMG
int rawInput;
float convertedFloatInput;
int outputValue;

void setup() {
  // initialize the pin as an input
  pinMode(inputPin, INPUT_PULLUP);
}

void loop() {
  analogReadResolution(ANALOG_READ_RESOLUTION);
  rawInput = analogRead(inputPin);

  convertedFloatInput = MAX_ANALOG_OUT*(float)rawInput/float(MAX_ANALOG_IN);
  outputValue = (int)max(0,min(convertedFloatInput,MAX_ANALOG_OUT));
  Joystick.X(outputValue);
}