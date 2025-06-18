import socket
import struct
import random
import time

# Prefix constants
ACCEL_PREFIX = 0x01
GYRO_PREFIX = 0x03
TEMP_PREFIX = 0x04

UDP_IP = "127.0.0.1"
UDP_PORT = 3000

def send_udp(data):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(data, (UDP_IP, UDP_PORT))

def float32_bytes(value):
    return struct.pack('<f', value)  # little-endian float32

def simulate_data():
    try:
        while True:
            # Simulate accelerometer data
            accel_x = random.uniform(-2, 2)
            accel_y = random.uniform(-2, 2)
            accel_z = random.uniform(-2, 2)
            accel_payload = (
                bytes([3]) +
                float32_bytes(accel_x) +
                float32_bytes(accel_y) +
                float32_bytes(accel_z)
            )
            send_udp(accel_payload)
            print(f"Acceleration (g): x={accel_x:.2f}, y={accel_y:.2f}, z={accel_z:.2f}")

            # Simulate gyroscope data
            gyro_x = random.uniform(-90, 90)
            gyro_y = random.uniform(-90, 90)
            gyro_z = random.uniform(-90, 90)
            gyro_payload = (
                bytes([2]) +
                float32_bytes(gyro_x) +
                float32_bytes(gyro_y) +
                float32_bytes(gyro_z)
            )
            send_udp(gyro_payload)
            print(f"Gyroscope (°/s): x={gyro_x:.2f}, y={gyro_y:.2f}, z={gyro_z:.2f}")

            # Simulate temperature data
            temp = random.uniform(20.0, 40.0)
            temp_payload = bytes([1]) + float32_bytes(temp)
            send_udp(temp_payload)
            print(f"Temperature (°C): {temp:.2f}")

            time.sleep(1)  # wait 1 second before next set

    except KeyboardInterrupt:
        print("\nSimulation stopped by user.")

simulate_data()

