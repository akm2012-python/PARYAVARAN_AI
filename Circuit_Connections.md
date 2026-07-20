# EcoSmart AI Bus Stand - Circuit Connections & Wiring Guide

This document outlines the complete pin assignment and wiring schema for the **EcoSmart AI Bus Stand** project based on an **Arduino UNO** microcontroller.

---

## 📌 Master Pin Assignment Table

| Component Name | Arduino UNO Pin | Type | Power Supply | Notes / Description |
|---|---|---|---|---|
| **DHT11 Sensor** | `D2` | Digital I/O | 5V / GND | Temperature & Humidity Sensor |
| **IR Obstacle Sensor** | `D3` | Digital Input | 5V / GND | Passenger Detection (LOW = Detected) |
| **LDR Module** | `D4` | Digital Input | 5V / GND | Day/Night Ambient Light Detection |
| **Red LED** | `D5` | Digital Output | Resistor + GND | Traffic Light Module (Bin Full Warning) |
| **Yellow LED** | `D6` | Digital Output | Resistor + GND | Traffic Light Module (Bin Medium Warning) |
| **Green LED** | `D7` | Digital Output | Resistor + GND | Traffic Light Module (Bin Normal Indicator) |
| **HC-SR04 Trigger** | `D8` | Digital Output | 5V / GND | Ultrasonic Sensor Trigger Pin |
| **HC-SR04 Echo** | `D9` | Digital Input | 5V / GND | Ultrasonic Sensor Echo Pin |
| **Relay Module (Fan)** | `D10` | Digital Output | 5V / GND | **LOW Trigger** (LOW = ON, HIGH = OFF) |
| **Reserved** | `D11` | N/A | N/A | Reserved for expansion |
| **Active Buzzer** | `D12` | Digital Output | GND | Sounder for High Bin Alert (>=90%) |
| **Street Light LED** | `D13` | Digital Output | 220Ω + GND | Automatic Night Street Illumination |
| **MQ135 Gas Sensor** | `A0` | Analog Input | 5V / GND | Air Quality & Hazardous Gas Monitoring |

---

## ⚡ Power Supply & Common Ground

1. **VCC Power Rail (5V):** Connect the Arduino 5V output pin to the red power rail on the breadboard.
2. **Ground Rail (GND):** Connect the Arduino GND pin to the blue ground rail on the breadboard.
3. **Common Ground:** Ensure all sensors, LEDs, relays, and modules share a common ground connection.