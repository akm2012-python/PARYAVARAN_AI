/*
 * EcoSmart AI Bus Stand - Arduino Firmware
 * Board: Arduino UNO | Baud: 9600
 * Creator: Aditya Kumar Mohanani | PM SHRI JNV Burhanpur
 */

#include "DHT.h"

// Pin Assignments
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

// Constants
#define DUSTBIN_DEPTH_CM 20.0
#define DUSTBIN_MIN_CM 2.0

DHT dht(DHTPIN, DHTTYPE);

unsigned long previousMillis = 0;
const long interval = 1000; // Send telemetry every 1 second

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

  // Default Off States
  digitalWrite(RELAY_FAN_PIN, HIGH);  // LOW-trigger Relay (HIGH = OFF)
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

    // 1. Temperature & Humidity Sensing
    float tempC = dht.readTemperature();
    float humidity = dht.readHumidity();
    if (isnan(tempC)) tempC = 25.0;
    if (isnan(humidity)) humidity = 50.0;

    // 2. Ultrasonic Dustbin Level Sensing
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

    // 3. Passenger Detection (IR) & Day/Night (LDR)
    bool passengerDetected = (digitalRead(IR_PIN) == LOW);
    bool isNight = (digitalRead(LDR_PIN) == HIGH);

    // Actuate Street Light
    digitalWrite(STREET_LIGHT_PIN, isNight ? HIGH : LOW);

    // 4. Air Quality Monitoring (MQ135)
    int mqRaw = analogRead(MQ135_PIN);
    int approxPPM = (int)(mqRaw * 0.8 + 100);
    int airQualityPercent = map(mqRaw, 0, 1023, 100, 0);
    airQualityPercent = constrain(airQualityPercent, 0, 100);

    String airStatus = "Fresh";
    if (mqRaw > 600) airStatus = "Hazardous";
    else if (mqRaw > 400) airStatus = "Unhealthy";
    else if (mqRaw > 250) airStatus = "Moderate";

    // 5. Fan Control Logic
    bool fanState = false;
    if (tempC > 30.0 && passengerDetected) {
      digitalWrite(RELAY_FAN_PIN, LOW); // Relay ON
      fanState = true;
    } else {
      digitalWrite(RELAY_FAN_PIN, HIGH); // Relay OFF
      fanState = false;
    }

    // 6. TriLogic & Traffic LED Indication
    bool buzzerState = false;
    if (dustbinPercent >= 90) {
      digitalWrite(RED_LED_PIN, HIGH); digitalWrite(YELLOW_LED_PIN, LOW); digitalWrite(GREEN_LED_PIN, LOW);
      digitalWrite(BUZZER_PIN, HIGH); buzzerState = true;
    } else if (dustbinPercent > 80) {
      digitalWrite(RED_LED_PIN, HIGH); digitalWrite(YELLOW_LED_PIN, LOW); digitalWrite(GREEN_LED_PIN, LOW);
      digitalWrite(BUZZER_PIN, LOW);
    } else if (dustbinPercent >= 50) {
      digitalWrite(RED_LED_PIN, LOW); digitalWrite(YELLOW_LED_PIN, HIGH); digitalWrite(GREEN_LED_PIN, LOW);
      digitalWrite(BUZZER_PIN, LOW);
    } else {
      digitalWrite(RED_LED_PIN, LOW); digitalWrite(YELLOW_LED_PIN, LOW); digitalWrite(GREEN_LED_PIN, HIGH);
      digitalWrite(BUZZER_PIN, LOW);
    }

    // 7. Green AI Scoring
    int greenScore = 100;
    if (tempC > 30.0) greenScore -= 20;
    if (dustbinPercent > 80) greenScore -= 20;
    if (airStatus == "Unhealthy" || airStatus == "Hazardous") greenScore -= 15;
    if (isNight && !passengerDetected) greenScore -= 10;
    if (fanState && !passengerDetected) greenScore -= 10;
    greenScore = constrain(greenScore, 0, 100);

    String greenStatus = "Excellent";
    if (greenScore < 50) greenStatus = "Poor";
    else if (greenScore < 70) greenStatus = "Average";
    else if (greenScore < 90) greenStatus = "Good";

    // 8. Explainable AI Recommendations
    String recommendation = "Everything Normal";
    if (dustbinPercent >= 80) recommendation = "Dustbin almost full";
    else if (airStatus == "Unhealthy" || airStatus == "Hazardous") recommendation = "Poor Air Quality";
    else if (fanState && passengerDetected) recommendation = "Fan ON because passenger detected";
    else if (isNight && passengerDetected) recommendation = "Street Light ON";
    else if (!passengerDetected && !fanState && greenScore >= 90) recommendation = "Energy Saving Excellent";

    int highTempFlag = (tempC > 30.0) ? 1 : 0;

    // 9. Serial CSV Telemetry Output (15 comma-separated values)
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