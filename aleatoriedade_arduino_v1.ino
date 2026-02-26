// Coleta de ruído físico com Arduino
// Conectar nada ao pino A0 (flutuante)

const int analogPin = A0;
const unsigned long sampleDelay = 2; // ms

void setup() {
  Serial.begin(115200);
}

void loop() {
  int raw = analogRead(analogPin); // 0–1023
  
  // Extrai bit menos significativo
  int bit = raw & 1;
  
  Serial.println(bit);
  
  delay(sampleDelay);
}
