/*
 * EcoSmart AI Bus Stand - Arduino Firmware
 * Target Board: Arduino UNO
 * 
 * Theme: Green Energy, Artificial Intelligence, Smart City, IoT
 * Event: National Science Exhibition
 * 
 * Pin Assignments:
 * D2  - DHT11 Data Pin
 * D3  - IR Obstacle Sensor (Active LOW / LOW when passenger detected)
 * D4  - LDR Module Digital Output (HIGH = Night/Dark, LOW = Day/Light)
 * D5  - Red LED (Traffic Light)
 * D6  - Yellow LED (Traffic Light)
 * D7  - Green LED (Traffic Light)
 * D8  - HC-SR04 Trigger Pin
 * D9  - HC-SR04 Echo Pin
 * D10 - Relay Module (Fan Control, LOW Trigger: LOW = ON, HIGH = OFF)
 * D11 - Reserved
 * D12 - Active Buzzer
 * D13 - Street Light LED (+ 220 Ohm Resistor)
 * A0  - MQ135 Gas Sensor Analog Input
 *
 * CSV Serial Output Format:
 * temperature,humidity,dustbin,person,daynight,fan,score,status,airquality,airstatus,recommendation,buzzer,hightemp,mqraw,airqualitypercent
 */

#include "DHT.h"

// Pin Definitions
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
#define DUSTBIN_DEPTH_CM 20.0       // Maximum depth of dustbin in cm (empty bin distance)
#define DUSTBIN_MIN_CM 2.0          // Distance when bin is 100% full

// Global Sensor Objects
DHT dht(DHTPIN, DHTTYPE);

// Timing variables for non-blocking millis execution
unsigned long previousMillis = 0;
const long interval = 1000; // Sample and transmit data every 1000ms (1s)

void setup() {
  // Initialize Serial Interface
  Serial.begin(9600);

  // Initialize Sensors & Pins
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

  // Initial Pin States
  digitalWrite(RELAY_FAN_PIN, HIGH);  // OFF for LOW trigger relay
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

    // 1. Read DHT11 Sensor
    float tempC = dht.readTemperature();
    float humidity = dht.readHumidity();

    if (isnan(tempC)) tempC = 25.0; // Fallback value if sensor misreads
    if (isnan(humidity)) humidity = 50.0;

    // 2. Read HC-SR04 Ultrasonic Sensor (Dustbin level)
    digitalWrite(TRIG_PIN, LOW);
    delayMicroseconds(2);
    digitalWrite(TRIG_PIN, HIGH);
    delayMicroseconds(10);
    digitalWrite(TRIG_PIN, LOW);

    long duration = pulseIn(ECHO_PIN, HIGH, 30000); // 30ms timeout
    float distanceCm = 0.0;
    if (duration == 0) {
      distanceCm = DUSTBIN_DEPTH_CM;
    } else {
      distanceCm = duration * 0.0343 / 2.0;
    }

    if (distanceCm > DUSTBIN_DEPTH_CM) distanceCm = DUSTBIN_DEPTH_CM;
    if (distanceCm < DUSTBIN_MIN_CM) distanceCm = DUSTBIN_MIN_CM;

    int dustbinPercent = (int)(((DUSTBIN_DEPTH_CM - distanceCm) / (DUSTBIN_DEPTH_CM - DUSTBIN_MIN_CM)) * 100.0);
    if (dustbinPercent < 0) dustbinPercent = 0;
    if (dustbinPercent > 100) dustbinPercent = 100;

    // 3. Read IR Sensor (Passenger Detection)
    // IR Obstacle sensors read LOW when obstacle is detected
    int irVal = digitalRead(IR_PIN);
    bool passengerDetected = (irVal == LOW);

    // 4. Read LDR Sensor (Day/Night Detection)
    // Standard digital LDR modules output HIGH in low light (Night), LOW in bright light (Day)
    int ldrVal = digitalRead(LDR_PIN);
    bool isNight = (ldrVal == HIGH);

    // Street Light Control Logic
    if (isNight) {
      digitalWrite(STREET_LIGHT_PIN, HIGH);
    } else {
      digitalWrite(STREET_LIGHT_PIN, LOW);
    }

    // 5. Read MQ135 Gas Sensor
    int mqRaw = analogRead(MQ135_PIN);
    float mqVoltage = mqRaw * (5.0 / 1023.0);
    
    // Approximate PPM calculation for environmental monitoring
    int approxPPM = (int)(mqRaw * 0.8 + 100); 

    int airQualityPercent = map(mqRaw, 0, 1023, 100, 0); // 100% = Fresh, 0% = Severe
    if (airQualityPercent < 0) airQualityPercent = 0;
    if (airQualityPercent > 100) airQualityPercent = 100;

    String airStatus = "Fresh";
    if (mqRaw > 600) {
      airStatus = "Hazardous";
    } else if (mqRaw > 400) {
      airStatus = "Unhealthy";
    } else if (mqRaw > 250) {
      airStatus = "Moderate";
    } else {
      airStatus = "Fresh";
    }

    // 6. Fan Logic
    bool fanState = false;
    if (tempC > 30.0 && passengerDetected) {
      digitalWrite(RELAY_FAN_PIN, LOW); // LOW Trigger Relay ON
      fanState = true;
    } else {
      digitalWrite(RELAY_FAN_PIN, HIGH); // Relay OFF
      fanState = false;
    }

    // 7. Traffic Light & Buzzer Logic based on Dustbin Level
    bool buzzerState = false;
    if (dustbinPercent >= 90) {
      digitalWrite(RED_LED_PIN, HIGH);
      digitalWrite(YELLOW_LED_PIN, LOW);
      digitalWrite(GREEN_LED_PIN, LOW);
      digitalWrite(BUZZER_PIN, HIGH);
      buzzerState = true;
    } else if (dustbinPercent > 80) {
      digitalWrite(RED_LED_PIN, HIGH);
      digitalWrite(YELLOW_LED_PIN, LOW);
      digitalWrite(GREEN_LED_PIN, LOW);
      digitalWrite(BUZZER_PIN, LOW);
      buzzerState = false;
    } else if (dustbinPercent >= 50) {
      digitalWrite(RED_LED_PIN, LOW);
      digitalWrite(YELLOW_LED_PIN, HIGH);
      digitalWrite(GREEN_LED_PIN, LOW);
      digitalWrite(BUZZER_PIN, LOW);
      buzzerState = false;
    } else {
      digitalWrite(RED_LED_PIN, LOW);
      digitalWrite(YELLOW_LED_PIN, LOW);
      digitalWrite(GREEN_LED_PIN, HIGH);
      digitalWrite(BUZZER_PIN, LOW);
      buzzerState = false;
    }

    // 8. Green AI Score Calculation
    int greenScore = 100;

    if (tempC > 30.0) greenScore -= 20;
    if (dustbinPercent > 80) greenScore -= 20;
    if (airStatus == "Unhealthy" || airStatus == "Hazardous") greenScore -= 15;
    if (isNight && !passengerDetected) greenScore -= 10;
    if (fanState && !passengerDetected) greenScore -= 10;
    
    if (greenScore < 0) greenScore = 0;
    if (greenScore > 100) greenScore = 100;

    // Green AI Status Category
    String greenStatus = "Excellent";
    if (greenScore >= 90) {
      greenStatus = "Excellent";
    } else if (greenScore >= 70) {
      greenStatus = "Good";
    } else if (greenScore >= 50) {
      greenStatus = "Average";
    } else {
      greenStatus = "Poor";
    }

    // 9. Intelligent Recommendations Generation
    String recommendation = "Everything Normal";

    if (dustbinPercent >= 80) {
      recommendation = "Dustbin almost full";
    } else if (airStatus == "Unhealthy" || airStatus == "Hazardous") {
      recommendation = "Poor Air Quality";
    } else if (fanState && passengerDetected) {
      recommendation = "Fan ON because passenger detected";
    } else if (isNight && passengerDetected) {
      recommendation = "Street Light ON";
    } else if (!passengerDetected && !fanState && greenScore >= 90) {
      recommendation = "Energy Saving Excellent";
    } else if (!passengerDetected && fanState) {
      recommendation = "No passenger Fan OFF";
    }

    // High Temp flag for Python backend
    int highTempFlag = (tempC > 30.0) ? 1 : 0;

    // 10. Serial CSV Data Output
    // Format: temperature,humidity,dustbin,person,daynight,fan,score,status,airquality,airstatus,recommendation,buzzer,hightemp,mqraw,airqualitypercent
    Serial.print(tempC, 1);
    Serial.print(",");
    Serial.print(humidity, 1);
    Serial.print(",");
    Serial.print(dustbinPercent);
    Serial.print(",");
    Serial.print(passengerDetected ? "Detected" : "None");
    Serial.print(",");
    Serial.print(isNight ? "Night" : "Day");
    Serial.print(",");
    Serial.print(fanState ? "ON" : "OFF");
    Serial.print(",");
    Serial.print(greenScore);
    Serial.print(",");
    Serial.print(greenStatus);
    Serial.print(",");
    Serial.print(approxPPM);
    Serial.print(",");
    Serial.print(airStatus);
    Serial.print(",");
    Serial.print(recommendation);
    Serial.print(",");
    Serial.print(buzzerState ? "ON" : "OFF");
    Serial.print(",");
    Serial.print(highTempFlag);
    Serial.print(",");
    Serial.print(mqRaw);
    Serial.print(",");
    Serial.println(airQualityPercent);
  }
}