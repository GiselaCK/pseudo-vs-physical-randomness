const int analogPin = A0;

void setup() {
  Serial.begin(115200);
  DIDR0 = 0x01; // desativa buffer digital do ADC0
}

void loop() {

  int v = analogRead(analogPin);

  int bit = v & 1;   // pega LSB

  Serial.println(bit);

}
