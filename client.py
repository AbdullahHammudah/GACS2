import socket
import threading
import pyaudio
import time

# Client configuration
SERVER_HOST = '192.168.10.2'
CONTROL_PORT = 5050
VOICE_PORT = 5051
S_FORMAT = 'utf-8'

# Audio configuration
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

# Initialize PyAudio
p = pyaudio.PyAudio()

def record_and_send(voice_socket):
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    print("Recording and sending...")
    while True:
        try:
            data = stream.read(CHUNK, exception_on_overflow=False)
            voice_socket.sendto(data, (SERVER_HOST, VOICE_PORT))
        except (OSError, ConnectionAbortedError):
            break
    stream.close()

def receive_and_play(voice_socket):
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True, frames_per_buffer=CHUNK)
    print("Receiving and playing...")
    while True:
        try:
            data, _ = voice_socket.recvfrom(CHUNK * 2)  # Adjust buffer size if necessary
            if not data:
                break
            stream.write(data)
        except (OSError, ConnectionAbortedError):
            break
    stream.close()

def control_speaking(control_socket, voice_socket):
    while True:
        control_command = input("Enter command (S/F): ").strip().upper()
        if control_command == "S":
            encoded_control_command = control_command.encode(S_FORMAT)
            control_socket.send(encoded_control_command)
            time.sleep(0.2)
            response = control_socket.recv(1024).decode(S_FORMAT)
            print(response)
            if response == "Permission to speak granted":
                threading.Thread(target=record_and_send, args=(voice_socket,)).start()
        elif control_command == "F":
            encoded_control_command = control_command.encode(S_FORMAT)
            control_socket.send(encoded_control_command)
            time.sleep(0.2)
            response = control_socket.recv(1024).decode(S_FORMAT)
            print(response)

            # voice_socket.close()
            # new_voice_socket = start_voice_connection()
            # control_speaking(control_socket, new_voice_socket)

def start_voice_connection():
    voice_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print(f"[VOICE CONNECTION] Voice Channel Ready to send to {SERVER_HOST, VOICE_PORT}.")

    threading.Thread(target=receive_and_play, args=(voice_socket,)).start()
    print(f"[VOICE CONNECTION] Listening for incoming voice communications...")

    return voice_socket

def start_server_connection():
    control_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    control_socket.connect((SERVER_HOST, CONTROL_PORT))
    print(f"[CONTROL CONNECTION] Control Channel Connected to {SERVER_HOST, CONTROL_PORT}.")

    voice_socket = start_voice_connection()
    control_speaking(control_socket, voice_socket)

start_server_connection()
