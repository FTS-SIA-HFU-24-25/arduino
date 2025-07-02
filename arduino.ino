#include "MPU6500_WE.hpp"
#include <Wire.h>
#include "Protocentral_MAX30205.h"

// === Pin Definitions ===
const int csPin = 10;
const int mosiPin = 11;
const int misoPin = 12;
const int sckPin = 13;
const int ecgPin = A0;

// === Sensor Objects ===
MPU6500_WE myMPU6500 = MPU6500_WE(&SPI, csPin, mosiPin, misoPin, sckPin, true);
MAX30205 tempSensor;

// === Timer for Misc Data ===
unsigned long previousMillis = 0;
const unsigned long interval = 5000; // every 3 seconds

void setup() {
  Serial.begin(115200);
  Wire.begin();
  delay(1000);
  if(!myMPU6500.init()){
    Serial.println("MPU9250 does not respond");
  }
  else{
    Serial.println("MPU9250 is connected");
  }

  // === MPU6500 Setup ===
  myMPU6500.enableGyrDLPF();
  //myMPU9250.disableGyrDLPF(MPU9250_BW_WO_DLPF_8800); // bandwdith without DLPF
  myMPU6500.setGyrDLPF(MPU9250_DLPF_6);
  myMPU6500.setSampleRateDivider(5);
  myMPU6500.setGyrRange(MPU9250_GYRO_RANGE_250);
  myMPU6500.setAccRange(MPU9250_ACC_RANGE_2G);
  myMPU6500.enableAccDLPF(true);
  myMPU6500.setAccDLPF(MPU9250_DLPF_6);

  // === Temperature Sensor Setup ===
  while (!tempSensor.scanAvailableSensors()) {
    delay(30000); // Wait until sensor is available
  }
  tempSensor.begin();
}

void loop() {
  // === Read ECG and Send ===
  int ecgValue = analogRead(ecgPin);
  sendECG(ecgValue);

  // === Send Misc Data Periodically ===
  unsigned long currentMillis = millis();
  if (currentMillis - previousMillis >= interval) {
    previousMillis = currentMillis;
    sendMiscData();
  }

  delay(10); // ECG sampling every 10ms
}

// =======================================
// === Data Sending Functions ===
// =======================================

// Send Float with Frame
void sendFloat(byte type, float value) {
  byte* bytePtr = (byte*) &value;
  byte checksum = 0xAA + type;
  
  Serial.write(0xAA);  // Start frame
  Serial.write(type);  // Data type

  for (int i = 0; i < 4; i++) {
    Serial.write(bytePtr[i]);
    checksum += bytePtr[i];
  }

  Serial.write(checksum); // Checksum
}

// Send ECG as 2-byte data
void sendECG(int value) {
  byte msb = (value >> 8) & 0x03;
  byte lsb = value & 0xFF;
  byte checksum = 0xAA + 0x04 + msb + lsb;

  Serial.write(0xAA);    // Start frame
  Serial.write(0x04);    // ECG data type
  Serial.write(msb);
  Serial.write(lsb);
  Serial.write(checksum); // Checksum
}

// Send Miscellaneous Data: Accel, Gyro, Temp
void sendMiscData() {
  xyzFloat gyr = myMPU6500.getAngles();
  xyzFloat gValue = myMPU6500.getGValues();
  float temp = tempSensor.getTemperature() * -1 + 7;

  // Acceleration X/Y/Z
  sendFloat(0x11, gValue.x);
  sendFloat(0x12, gValue.y);
  sendFloat(0x13, gValue.z);

  // Gyroscope X/Y/Z
  sendFloat(0x21, gyr.x);
  sendFloat(0x22, gyr.y);
  sendFloat(0x23, gyr.z);

  // Temperature
  sendFloat(0x31, temp);
}
