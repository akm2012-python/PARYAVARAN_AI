/*
 * Paryavaran AI - Firmware (Arduino UNO)
 * Author: Aditya Kumar Mohanani
 * Hardware: Arduino UNO, DHT11, HC-SR04, MQ135, IR Sensor, LDR Module, 
 *           Traffic Light Module, Relay Module, DC Fan, Active Buzzer.
 */

#include "DHT.h"

#define DHTPIN 2
#define DHTTYPE DHT11
#define IR_PIN 3
#define LDR_PIN 4

#define RED_LED_PIN 5
#define YELLOW_LED_PIN 6
#define GREEN_LED_PIN 7

#define TRIG_PIN 8
#define ECHO_PIN 9

#define RELAY_FAN_PIN 10
#define BUZZER_PIN 12
#define STREET_LIGHT_PIN 13
#define MQ135_PIN A0

#define DUSTBIN_DEPTH_CM 20.0
#define DUSTBIN_MIN_CM 2.0

DHT dht(DHTPIN, DHTTYPE);
unsigned long previousMillis = 0;
const long interval = 1000;

void setup() {
  Serial.begin(9600);
  dht.begin();

  pinMode(IR_PIN, INPUT);
  pinMode(LDR_PIN, INPUT);

  pinMode(RED_LED_PIN, OUTPUT);
  pinMode(YELLOW_LED_PIN, OUTPUT);
  pinMode(GREEN_LED_PIN, OUTPUT);

  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);

  pinMode(RELAY_FAN_PIN, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(STREET_LIGHT_PIN, OUTPUT);

  digitalWrite(RELAY_FAN_PIN, HIGH); // OFF for Active-LOW Relay
  digitalWrite(RED_LED_PIN, LOW);
  digitalWrite(YELLOW_LED_PIN, LOW);
  digitalWrite(GREEN_LED_PIN, LOW);
  digitalWrite(BUZZER_PIN, LOW);
  digitalWrite(STREET_LIGHT_PIN, LOW);
}

void loop() {
  unsigned long currentMillis = millis();

  if (currentMillis - previousMillis >= interval) {
    previousMillis = currentMillis;

    // 1. Environmental Sensors
    float tempC = dht.readTemperature();
    float humidity = dht.readHumidity();
    if (isnan(tempC)) tempC = 25.0;
    if (isnan(humidity)) humidity = 50.0;

    // 2. Ultrasonic Dustbin Sensor
    digitalWrite(TRIG_PIN, LOW);
    delayMicroseconds(2);
    digitalWrite(TRIG_PIN, HIGH);
    delayMicroseconds(10);
    digitalWrite(TRIG_PIN, LOW);

    long duration = pulseIn(ECHO_PIN, HIGH, 30000);
    float distanceCm = (duration == 0) ? DUSTBIN_DEPTH_CM : (duration * 0.0343 / 2.0);
    if (distanceCm > DUSTBIN_DEPTH_CM) distanceCm = DUSTBIN_DEPTH_CM;
    if (distanceCm < DUSTBIN_MIN_CM) distanceCm = DUSTBIN_MIN_CM;

    int dustbinPercent = (int)(((DUSTBIN_DEPTH_CM - distanceCm) / (DUSTBIN_DEPTH_CM - DUSTBIN_MIN_CM)) * 100.0);
    dustbinPercent = constrain(dustbinPercent, 0, 100);

    // 3. Occupancy & Light Sensors
    bool passengerDetected = (digitalRead(IR_PIN) == LOW);
    bool isNight = (digitalRead(LDR_PIN) == HIGH);
    digitalWrite(STREET_LIGHT_PIN, isNight ? HIGH : LOW);

    // 4. MQ135 Air Quality Sensor
    int mqRaw = analogRead(MQ135_PIN);
    int approxPPM = (int)(mqRaw * 0.8 + 100);
    int airQualityPercent = map(mqRaw, 0, 1023, 100, 0);
    airQualityPercent = constrain(airQualityPercent, 0, 100);

    String airStatus = "Fresh";
    if (mqRaw > 600) airStatus = "Hazardous";
    else if (mqRaw > 400) airStatus = "Unhealthy";
    else if (mqRaw > 250) airStatus = "Moderate";

    // 5. Smart Actuation Logic
    bool fanState = (tempC > 30.0 && passengerDetected);
    digitalWrite(RELAY_FAN_PIN, fanState ? LOW : HIGH); // Active-LOW Relay

    // 6. TriLogic Decision Framework (-1: ALERT, 0: BALANCED, +1: ECO)
    int triLogicState = 1; 
    if (dustbinPercent >= 80 || mqRaw > 500 || tempC > 38.0) {
      triLogicState = -1; // ALERT Mode
    } else if (dustbinPercent >= 50 || mqRaw > 300 || tempC > 30.0) {
      triLogicState = 0;  // BALANCED Mode
    } else {
      triLogicState = 1;  // ECO Mode
    }

    // Physical Feedback via Traffic Light & Buzzer
    bool buzzerState = (dustbinPercent >= 90);
    digitalWrite(BUZZER_PIN, buzzerState ? HIGH : LOW);

    if (triLogicState == -1) {
      digitalWrite(RED_LED_PIN, HIGH);
      digitalWrite(YELLOW_LED_PIN, LOW);
      digitalWrite(GREEN_LED_PIN, LOW);
    } else if (triLogicState == 0) {
      digitalWrite(RED_LED_PIN, LOW);
      digitalWrite(YELLOW_LED_PIN, HIGH);
      digitalWrite(GREEN_LED_PIN, LOW);
    } else {
      digitalWrite(RED_LED_PIN, LOW);
      digitalWrite(YELLOW_LED_PIN, LOW);
      digitalWrite(GREEN_LED_PIN, HIGH);
    }

    // 7. Dynamic Green AI Score
    int greenScore = 100;
    if (tempC > 30.0) greenScore -= 15;
    if (dustbinPercent > 80) greenScore -= 20;
    if (airStatus != "Fresh") greenScore -= 15;
    if (isNight && !passengerDetected) greenScore -= 10;
    if (fanState && !passengerDetected) greenScore -= 15;
    greenScore = constrain(greenScore, 0, 100);

    String greenStatus = (greenScore >= 85) ? "Excellent" : ((greenScore >= 65) ? "Good" : "Poor");

    // Recommendations
    String recommendation = "System Optimal";
    if (dustbinPercent >= 80) recommendation = "Waste Pickup Needed";
    else if (airStatus != "Fresh") recommendation = "Air Filtration Active";
    else if (fanState) recommendation = "Passenger Cooling Active";

    int highTempFlag = (tempC > 30.0) ? 1 : 0;

    // Transmit Serial Data Frame (Preserving exact existing schema)
    Serial.print(tempC, 1); Serial.print(",");
    Serial.print(humidity, 1); Serial.print(",");
    Serial.print(dustbinPercent); Serial.print(",");
    Serial.print(passengerDetected ? "Detected" : "None"); Serial.print(",");
    Serial.print(isNight ? "Night" : "Day"); Serial.print(",");
    Serial.print(fanState ? "ON" : "OFF"); Serial.print(",");
    Serial.print(greenScore); Serial.print(",");
    Serial.print(greenStatus); Serial.print(",");
    Serial.print(approxPPM); Serial.print(",");
    Serial.print(airStatus); Serial.print(",");
    Serial.print(recommendation); Serial.print(",");
    Serial.print(buzzerState ? "ON" : "OFF"); Serial.print(",");
    Serial.print(highTempFlag); Serial.print(",");
    Serial.print(mqRaw); Serial.print(",");
    Serial.println(airQualityPercent);
  }
}