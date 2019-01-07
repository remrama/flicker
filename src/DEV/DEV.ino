// Listen to a single sensor and send to serial.


// variables
int SENS_PIN = A15;
int BULB_PIN = 33;
int BAUD_RATE = 9600;

void setup() {
  // init comm with python
  Serial.begin(BAUD_RATE);

  pinMode(SENS_PIN,INPUT);
  pinMode(BULB_PIN,OUTPUT);
}

int sensvalu;
char pyvalu;

void loop() {
  
  // read from python
  while (!Serial.available()){
    // read from sensor
    sensvalu = analogRead(SENS_PIN);
    Serial.println(sensvalu);
    digitalWrite(BULB_PIN,LOW);
    delay(10);

  } // wait for data to arrive
  // serial read section
  while (Serial.available()){
    pyvalu = Serial.read();  //gets one byte from serial buffer
    // Serial.println(pyvalu);
    if (pyvalu=='1'){
        digitalWrite(BULB_PIN,HIGH);
        delay(2000);
    } else {
        digitalWrite(BULB_PIN,LOW);
    }
  }

}