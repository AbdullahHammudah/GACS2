import socket
import pyaudio
import threading

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024

def send_command(command):
    client_socket.send(command.encode())
    response = client_socket.recv(1024).decode()
    print(response)

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('192.168.10.2', 9999))

audio = pyaudio.PyAudio()

input_stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
output_stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True, frames_per_buffer=CHUNK)

def receive_audio():
    while True:
        try:
            data = client_socket.recv(CHUNK)
            if data:
                output_stream.write(data)
        except Exception as e:
            print("Audio receive error:", e)
            break

audio_thread = threading.Thread(target=receive_audio)
audio_thread.start()

while True:
    command = input("Enter command (S/F): ").strip().upper()
    if command in ['S', 'F']:
        send_command(command)
        if command == 'S':
            while True:
                data = input_stream.read(CHUNK)
                client_socket.sendall(data)
    else:
        print("Invalid command. Please enter 'S' or 'F'.")
