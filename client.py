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
        data = stream.read(CHUNK, exception_on_overflow=False)
        voice_socket.sendall(data)

def receive_and_play(voice_socket):
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True, frames_per_buffer=CHUNK)
    print("Receiving and playing...")
    while True:
        data = voice_socket.recv(CHUNK)
        if not data:
            break
        print("Playing data...")
        stream.write(data)


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
            voice_socket.close()
            voice_socket = start_voice_connection()
            control_speaking(control_socket, voice_socket)


def start_voice_connection():
    voice_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    voice_socket.connect((SERVER_HOST, VOICE_PORT))
    print(f"[VOICE CONNECTION] Voice Channel Connected to {SERVER_HOST, VOICE_PORT}.")

    threading.Thread(target=receive_and_play, args=(voice_socket,)).start()
    print(f"[VOICE CONNECTION] Listening for incoming voice communications...")

    return voice_socket

def start_server_connection():
    control_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    control_socket.connect((SERVER_HOST,CONTROL_PORT))
    print(f"[CONTROL CONNECTION] Control Channel Connected to {SERVER_HOST, CONTROL_PORT}.")

    voice_socket = start_voice_connection()
    print("before")
    control_speaking(control_socket, voice_socket)
    print("after")


start_server_connection()