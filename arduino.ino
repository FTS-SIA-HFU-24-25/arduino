#include "MPU6500_WE.hpp"
#include <Wire.h>
#include "Protocentral_MAX30205.h"

const int csPin = 10;  // Chip Select Pin
const int mosiPin = 11;  // "MOSI" Pin
const int misoPin = 12;  // "MISO" Pin
const int sckPin = 13;  // SCK Pin
bool useSPI = true;    // SPI use flag

MPU6500_WE myMPU6500 = MPU6500_WE(&SPI, csPin, mosiPin, misoPin, sckPin, useSPI);
MAX30205 tempSensor;

void setup() {
  Serial.begin(115200);
  Wire.begin();
  if(!myMPU6500.init()){
    Serial.println("MPU6500 does not respond");
  }
  else{
    Serial.println("MPU6500 is connected");
  }

  Serial.println("Position you MPU6500 flat and don't move it - calibrating...");
  delay(1000);
  myMPU6500.autoOffsets();
  Serial.println("Done!");

  myMPU6500.enableGyrDLPF();
  myMPU6500.setGyrDLPF(MPU6500_DLPF_6);
  myMPU6500.setSampleRateDivider(5);
  myMPU6500.setGyrRange(MPU6500_GYRO_RANGE_250);
  myMPU6500.setAccRange(MPU6500_ACC_RANGE_2G);
  myMPU6500.enableAccDLPF(true);
  myMPU6500.setAccDLPF(MPU6500_DLPF_6);

  while(!tempSensor.scanAvailableSensors()){
    Serial.println("Couldn't find the temperature sensor, please connect the sensor." );
    delay(30000);
  }

  tempSensor.begin();
}

void loop() {
  xyzFloat gValue = myMPU6500.getGValues();
  xyzFloat gyr = myMPU6500.getAngles();
  float resultantG = myMPU6500.getResultantG(gValue);
  float temp = tempSensor.getTemperature() * -1 + 7;

  // Send acceleration
  sendFloat(0x01, gValue.x);
  sendFloat(0x01, gValue.y);
  sendFloat(0x01, gValue.z);

  delay(1000);

  // Send gyroscope data
  sendFloat(0x03, gyr.x);
  sendFloat(0x03, gyr.y);
  sendFloat(0x03, gyr.z);

  delay(1000);

  // Send temperature
  sendFloat(0x04, temp);

  delay(1000);
}

void sendFloat(byte prefix, float value) {
  byte* bytePtr = (byte*) &value;
  Serial.write(prefix);
  for (int i = 0; i < 4; i++) {
    Serial.write(bytePtr[i]);
  }
}


