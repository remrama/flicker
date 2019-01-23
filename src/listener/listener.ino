// Listen to sensor and send to serial.


// for bone conductor
#include <Audio.h>
AudioPlaySdWav         playWav;
AudioOutputAnalog      audioOutput;
// Here, 0 is for DAC0, and uncomment 1 for DAC1 (stereo)
AudioConnection        patchCord1(playWav,0,audioOutput,0);
// AudioConnection        patchCord2(playWav,1,audioOutput,1);


// variables
int SENS_PIN = A15; // sensor pin number
int BULB_PIN = 33;
// int ANALOG_READ_RESOLUTION = 13; // 13 bit analog to digital on teensy

// ?? this number "doesn't matter", bc teensy "always uses USB speeds"
int BAUD_RATE = 38400;


void setup() {
  // init comm with python
  Serial.begin(BAUD_RATE);

  pinMode(SENS_PIN,INPUT); // vs INPUT_PULLUP ??
  // pinMode(BULB_PIN,OUTPUT);

  // Audio connections require memory to work.
  AudioMemory(8);
  // make sure SD card is readable
  if (!(SD.begin(BUILTIN_SDCARD))) {
    // stop here, but print a message repetitively
    while (1) {
      Serial.println("Unable to access the SD card");
      delay(500);
    }
  }
}

int sensor_val;
char python_val;

// make function to play "audio" (ie, stimulator)
void playFile(const char *filename)
{
  // Serial.print("Playing file: ");
  // Serial.println(filename);

  // Start playing the file.
  playWav.play(filename);

  // A brief delay for the library read WAV info
  // delay(5);

  // Wait for the file to finish playing.
  // while (playWav.isPlaying()) {
  //   // wait here if you want
  // }
}


void loop() {

  while (!Serial.available()) {
    // read from sensor
    sensor_val = analogRead(SENS_PIN);
    Serial.println(sensor_val);
    // digitalWrite(BULB_PIN,LOW); // TEMP: turn off light
    delay(10);
  }

  while (Serial.available()) {
    // read from python
    python_val = Serial.read(); // gets one byte from serial buffer
    if (python_val=='1') {
        playFile("BACH.WAV");
        // digitalWrite(BULB_PIN,HIGH);
        // delay(500);
    }
  }
}
