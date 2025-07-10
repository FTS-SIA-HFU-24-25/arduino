import socket
import struct
import random
import time

# === UDP Settings ===
UDP_IP = "195.201.226.164"
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


# === ECG Sender ===
def send_ecg_data():
    ecg1 = random.randint(0, 1023)
    ecg2 = random.randint(0, 1023)

    payload = (
        bytes([LABEL_ECG]) +
        bytes([(ecg1 >> 8) & 0x03, ecg1 & 0xFF]) +
        bytes([(ecg2 >> 8) & 0x03, ecg2 & 0xFF])
    )
    send_udp(payload)
    print(f"ECG: {ecg1}, {ecg2}")


# === Other Sensor Sender ===
def send_other_sensors():
    # Temperature
    temp = round(random.uniform(25.0, 37.0), 2)
    payload_temp = bytes([LABEL_TEMP]) + float32_bytes(temp)
    send_udp(payload_temp)
    print(f"Temperature: {temp:.2f} °C")

    # Accelerometer
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

    # Gyroscope
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


# === Main Loop ===
def main():
    last_other_send = time.time()

    while True:
        start = time.time()

        # Send ECG at 200Hz
        send_ecg_data()

        # Check if 3 seconds have passed for other sensors
        if time.time() - last_other_send >= 3:
            send_other_sensors()
            last_other_send = time.time()

        # Wait for remainder of 5ms cycle
        elapsed = time.time() - start
        sleep_time = max(0, 0.005 - elapsed)
        time.sleep(sleep_time)


if __name__ == "__main__":
    main()

