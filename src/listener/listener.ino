// Listen to a single sensor and send to serial.


// variables
int SENS_PIN = A15; // the pin number (on teensy) of the sensor
int BULB_PIN = 33;
// int ANALOG_READ_RESOLUTION = 13; // 13 bit analog to digital on teensy

// ?? this number "doesn't matter", bc teensy "always uses USB speeds"
int BAUD_RATE = 38400;


void setup() {
  // init comm with python
  Serial.begin(BAUD_RATE);

  pinMode(SENS_PIN,INPUT); // vs INPUT_PULLUP ??
  pinMode(BULB_PIN,OUTPUT);
}

int sensor_val;
char python_val;

void loop() {

  while (!Serial.available()) {
    // read from sensor
    sensor_val = analogRead(SENS_PIN);
    Serial.println(sensor_val);
    digitalWrite(BULB_PIN,LOW); // TEMP: turn off light
    delay(10);
  }

  while (Serial.available()) {
    // read from python
    python_val = Serial.read(); // gets one byte from serial buffer
    if (python_val=='1') {
        digitalWrite(BULB_PIN,HIGH);
        delay(500);
    }
  }
}