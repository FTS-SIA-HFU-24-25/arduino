import socket
import struct
import random
import time

# === UDP Settings ===
UDP_IP = "192.168.178.135"
UDP_PORT = 3000

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# === Payload Labels ===
LABEL_ECG = 0
LABEL_TEMP = 1
LABEL_GYRO = 2
LABEL_ACCEL = 3


# === Helper Functions ===
def float32_bytes(value):
    return struct.pack('<f', value)


def send_udp(payload):
    sock.sendto(payload, (UDP_IP, UDP_PORT))


# === Random Data Generator ===
def generate_and_send_data():
    while True:
        # === Simulate ECG (2 samples of 10-bit ECG data) ===
        ecg1 = random.randint(0, 1023)
        ecg2 = random.randint(0, 1023)

        payload_ecg = (
            bytes([LABEL_ECG]) +
            bytes([(ecg1 >> 8) & 0x03, ecg1 & 0xFF]) +
            bytes([(ecg2 >> 8) & 0x03, ecg2 & 0xFF])
        )
        send_udp(payload_ecg)
        print(f"ECG: {ecg1}, {ecg2}")

        # === Simulate Temperature ===
        temp = round(random.uniform(25.0, 37.0), 2)
        payload_temp = bytes([LABEL_TEMP]) + float32_bytes(temp)
        send_udp(payload_temp)
        print(f"Temperature: {temp:.2f} °C")

        # === Simulate Accelerometer (X, Y, Z in g) ===
        accel_x = round(random.uniform(-2.0, 2.0), 2)
        accel_y = round(random.uniform(-2.0, 2.0), 2)
        accel_z = round(random.uniform(-2.0, 2.0), 2)

        payload_accel = (
            bytes([LABEL_ACCEL]) +
            float32_bytes(accel_x) +
            float32_bytes(accel_y) +
            float32_bytes(accel_z)
        )
        send_udp(payload_accel)
        print(f"Accel (g): x={accel_x}, y={accel_y}, z={accel_z}")

        # === Simulate Gyroscope (X, Y, Z in deg/s) ===
        gyro_x = round(random.uniform(-250.0, 250.0), 2)
        gyro_y = round(random.uniform(-250.0, 250.0), 2)
        gyro_z = round(random.uniform(-250.0, 250.0), 2)

        payload_gyro = (
            bytes([LABEL_GYRO]) +
            float32_bytes(gyro_x) +
            float32_bytes(gyro_y) +
            float32_bytes(gyro_z)
        )
        send_udp(payload_gyro)
        print(f"Gyro (dps): x={gyro_x}, y={gyro_y}, z={gyro_z}")

        print("-" * 50)

        time.sleep(1)  # Send new data every 1 second


if __name__ == "__main__":
    generate_and_send_data()

