/*
 * PARYAVARAN AI - ULTIMATE EMBEDDED FIRMWARE
 * Includes: LED array with resistors, non-blocking timing, floating-pin protection
 */

#include <DHT.h>

// --- PIN DEFINITIONS ---
#define DHTPIN       2
#define DHTTYPE      DHT11
#define TRIGPIN      3
#define ECHOPIN      4
#define IRPIN        5
#define MQ135PIN     A0
#define LDRPIN       A1

// Visual Indicators (Each LED connected in series with a 220 Ohm resistor)
#define RED_LED      8
#define YEL_LED      9
#define GRN_LED      10

// Actuators
#define FAN_RELAY    11
#define BUZZER       12

DHT dht(DHTPIN, DHTTYPE);

// Non-blocking timer variables (Prevents delay lag)
unsigned long previousMillis = 0;
const long interval = 1000; // 1-second interval

// Smooth Analog Reader (Averages 10 samples to eliminate pin floating/noise)
int readSmoothedAnalog(int pin) {
  long sum = 0;
  for (int i = 0; i < 10; i++) {
    sum += analogRead(pin);
    delayMicroseconds(50);
  }
  return (int)(sum / 10);
}

void setup() {
  Serial.begin(9600);
  dht.begin();
  
  pinMode(TRIGPIN, OUTPUT);
  pinMode(ECHOPIN, INPUT);
  pinMode(IRPIN, INPUT_PULLUP); // Prevents random readings when unhooked
  
  // LED Output Pins
  pinMode(RED_LED, OUTPUT);
  pinMode(YEL_LED, OUTPUT);
  pinMode(GRN_LED, OUTPUT);
  
  // Actuator Output Pins
  pinMode(FAN_RELAY, OUTPUT);
  pinMode(BUZZER, OUTPUT);
  
  // Initial Hardware State
  digitalWrite(FAN_RELAY, HIGH); // Relay De-asserted (Active LOW)
  digitalWrite(BUZZER, LOW);
  
  // Initial LED State: Eco Mode Active
  digitalWrite(RED_LED, LOW);
  digitalWrite(YEL_LED, LOW);
  digitalWrite(GRN_LED, HIGH);
}

void loop() {
  unsigned long currentMillis = millis();

  // Non-blocking 1-second telemetry loop
  if (currentMillis - previousMillis >= interval) {
    previousMillis = currentMillis;

    // 1. Read DHT11 Temperature & Humidity
    float temp = dht.readTemperature();
    float hum = dht.readHumidity();
    if (isnan(temp) || temp <= 0) temp = 25.0; // Fallback if sensor unhooked
    if (isnan(hum) || hum <= 0) hum = 50.0;

    // 2. Ultrasonic Dustbin Distance Calculation
    digitalWrite(TRIGPIN, LOW);
    delayMicroseconds(2);
    digitalWrite(TRIGPIN, HIGH);
    delayMicroseconds(10);
    digitalWrite(TRIGPIN, LOW);
    long duration = pulseIn(ECHOPIN, HIGH, 25000); // 25ms timeout
    
    int binPercent = 0;
    if (duration > 0) {
      float distanceCm = duration * 0.034 / 2.0;
      binPercent = map(constrain((int)distanceCm, 5, 30), 5, 30, 100, 0);
    }

    // 3. Noise-Filtered Analog Sensor Readings
    int rawGas = readSmoothedAnalog(MQ135PIN);
    int rawLDR = readSmoothedAnalog(LDRPIN);
    int irState = (digitalRead(IRPIN) == LOW) ? 1 : 0;

    // 4. TriLogic Ternary State Engine Computation
    int triState = 1; // Default: Eco Mode (+1)
    if (temp > 35.0 || rawGas > 400 || binPercent > 85) {
      triState = -1; // Alert Mode
    } else if (temp > 30.0 || rawGas > 250 || binPercent > 70) {
      triState = 0;  // Balanced Mode
    }

    // 5. LED Array State Control
    if (triState == -1) {
      digitalWrite(RED_LED, HIGH); // Red LED ON (Alert)
      digitalWrite(YEL_LED, LOW);
      digitalWrite(GRN_LED, LOW);
    } else if (triState == 0) {
      digitalWrite(RED_LED, LOW);
      digitalWrite(YEL_LED, HIGH); // Yellow LED ON (Balanced)
      digitalWrite(GRN_LED, LOW);
    } else {
      digitalWrite(RED_LED, LOW);
      digitalWrite(YEL_LED, LOW);
      digitalWrite(GRN_LED, HIGH); // Green LED ON (Eco)
    }

    // 6. Actuator Outputs
    digitalWrite(BUZZER, (triState == -1) ? HIGH : LOW);
    digitalWrite(FAN_RELAY, (temp > 30.0) ? LOW : HIGH); // Active LOW relay cooling

    // 7. Stream Telemetry payload to Serial Line
    // Format: TEMP,HUM,GAS,LDR,BIN,IR,TRISTATE
    Serial.print(temp, 1);     Serial.print(",");
    Serial.print(hum, 1);      Serial.print(",");
    Serial.print(rawGas);      Serial.print(",");
    Serial.print(rawLDR);      Serial.print(",");
    Serial.print(binPercent);  Serial.print(",");
    Serial.print(irState);     Serial.print(",");
    Serial.println(triState);
  }
}