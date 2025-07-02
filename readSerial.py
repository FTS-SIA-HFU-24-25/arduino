import serial
import socket
import struct

# === Data Type Constants ===
ACCEL_X = 0x11
ACCEL_Y = 0x12
ACCEL_Z = 0x13

GYRO_X = 0x21
GYRO_Y = 0x22
GYRO_Z = 0x23

TEMP = 0x31
ECG = 0x04

HEADER = 0xAA

# === UDP Settings ===
UDP_IP = "192.168.178.135"
UDP_PORT = 3000

# === UDP Send Function ===
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


def send_udp(data):
    sock.sendto(data, (UDP_IP, UDP_PORT))


# === Helper Functions ===
def float32_bytes(value):
    return struct.pack('<f', value)


def float_from_bytes(byte_data):
    return struct.unpack('<f', byte_data)[0]


# === Serial Reading and Parsing ===
def read_serial(port="/dev/ttyUSB0", baudrate=115200):
    ser = serial.Serial(port, baudrate, timeout=1)
    print("Listening on", port)

    accel_buffer = {}
    gyro_buffer = {}

    try:
        while True:
            byte = ser.read(1)
            if not byte:
                continue

            if byte[0] != HEADER:
                continue  # Wait until header 0xAA

            type_byte = ser.read(1)
            if not type_byte:
                continue

            data_type = type_byte[0]

            # ECG has 2-byte payload
            if data_type == ECG:
                payload = ser.read(2)
                checksum_byte = ser.read(1)
                if len(payload) < 2 or len(checksum_byte) < 1:
                    continue

                checksum_calc = (HEADER + data_type + sum(payload)) & 0xFF
                if checksum_calc != checksum_byte[0]:
                    print("ECG checksum mismatch!")
                    continue

                value = (payload[0] << 8) | payload[1]
                send_udp(bytes([0]) + payload)
                # print(f"ECG Value: {value}")

            # Other types (float-based)
            elif data_type in [
                ACCEL_X, ACCEL_Y, ACCEL_Z,
                GYRO_X, GYRO_Y, GYRO_Z,
                TEMP
            ]:
                payload = ser.read(4)
                checksum_byte = ser.read(1)
                if len(payload) < 4 or len(checksum_byte) < 1:
                    continue

                checksum_calc = (HEADER + data_type + sum(payload)) & 0xFF
                if checksum_calc != checksum_byte[0]:
                    print(f"Checksum mismatch on type {hex(data_type)}")
                    continue

                value = float_from_bytes(payload)

                # === Accelerometer ===
                if data_type in [ACCEL_X, ACCEL_Y, ACCEL_Z]:
                    axis = {ACCEL_X: 'x', ACCEL_Y: 'y', ACCEL_Z: 'z'}[data_type]
                    accel_buffer[axis] = value

                    if len(accel_buffer) == 3:
                        payload_out = (
                            bytes([3]) +  # Label for Accel
                            float32_bytes(accel_buffer['x']) +
                            float32_bytes(accel_buffer['y']) +
                            float32_bytes(accel_buffer['z'])
                        )
                        send_udp(payload_out)
                        print(
                            f"Accel (g): x={accel_buffer['x']:.2f}, "
                            f"y={accel_buffer['y']:.2f}, z={accel_buffer['z']:.2f}"
                        )
                        accel_buffer.clear()

                # === Gyroscope ===
                elif data_type in [GYRO_X, GYRO_Y, GYRO_Z]:
                    axis = {GYRO_X: 'x', GYRO_Y: 'y', GYRO_Z: 'z'}[data_type]
                    gyro_buffer[axis] = value

                    if len(gyro_buffer) == 3:
                        payload_out = (
                            bytes([2]) +  # Label for Gyro
                            float32_bytes(gyro_buffer['x']) +
                            float32_bytes(gyro_buffer['y']) +
                            float32_bytes(gyro_buffer['z'])
                        )
                        send_udp(payload_out)
                        print(
                            f"Gyro (dps): x={gyro_buffer['x']:.2f}, "
                            f"y={gyro_buffer['y']:.2f}, z={gyro_buffer['z']:.2f}"
                        )
                        gyro_buffer.clear()

                # === Temperature ===
                elif data_type == TEMP:
                    payload_out = bytes([1]) + float32_bytes(value)
                    send_udp(payload_out)
                    print(f"Temperature (°C): {value:.2f}")

            else:
                print(f"Unknown data type: {hex(data_type)}")

    except KeyboardInterrupt:
        print("\nStopped by user.")
    finally:
        ser.close()


if __name__ == "__main__":
    read_serial()

