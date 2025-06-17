import serial
import socket
import struct

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

def float_from_bytes(byte_data):
    return struct.unpack('<f', byte_data)[0]  # little-endian float

def read_serial(port="/dev/ttyUSB0", baudrate=115200):
    ser = serial.Serial(port, baudrate, timeout=1)
    print("Listening on", port)

    accel_buffer = []
    gyro_buffer = []

    try:
        while True:
            if ser.in_waiting >= 5:
                prefix = ser.read(1)[0]
                if prefix > TEMP_PREFIX:
                    continue
                data_bytes = ser.read(4)

                if len(data_bytes) < 4:
                    continue  # Skip incomplete

                value = float_from_bytes(data_bytes)

                if prefix == ACCEL_PREFIX:
                    accel_buffer.append(value)
                    if len(accel_buffer) == 3:
                        payload = (
                            bytes([3]) +
                            float32_bytes(accel_buffer[0]) +
                            float32_bytes(accel_buffer[1]) +
                            float32_bytes(accel_buffer[2])
                        )
                        send_udp(payload)
                        print(f"Acceleration (g): x={accel_buffer[0]:.2f}, y={accel_buffer[1]:.2f}, z={accel_buffer[2]:.2f}")
                        accel_buffer.clear()

                elif prefix == GYRO_PREFIX:
                    gyro_buffer.append(value)
                    if len(gyro_buffer) == 3:
                        payload = (
                            bytes([2]) +
                            float32_bytes(gyro_buffer[0]) +
                            float32_bytes(gyro_buffer[1]) +
                            float32_bytes(gyro_buffer[2])
                        )
                        send_udp(payload)
                        print(f"Gyroscope (°/s): x={gyro_buffer[0]:.2f}, y={gyro_buffer[1]:.2f}, z={gyro_buffer[2]:.2f}")
                        gyro_buffer.clear()

                elif prefix == TEMP_PREFIX:
                    payload = bytes([1]) + float32_bytes(value)
                    send_udp(payload)
                    print(f"Temperature (°C): {value:.2f}")

                else:
                    print(f"Unknown prefix {prefix} with value {value:.2f}")

    except KeyboardInterrupt:
        print("\nStopped by user.")
    finally:
        ser.close()


read_serial()
