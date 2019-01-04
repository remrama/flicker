// Listen to a single sensor and send to serial.


// variables
int INPUT_PIN = A14; // the pin number (on teensy) of the sensor
// int ANALOG_READ_RESOLUTION = 13; // 13 bit analog to digital on teensy

// ?? this number "doesn't matter", bc teensy "always uses USB speeds"
int BAUD_RATE = 38400;


void setup() {
  Serial.begin(BAUD_RATE); // initialize communication
  // initialize the pin as an input
  pinMode(INPUT_PIN,INPUT); // vs INPUT_PULLUP ??
}

int val;

void loop() {
  val = analogRead(INPUT_PIN);
  Serial.println(val);
  delay(10);
}