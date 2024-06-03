import socket
import pyaudio

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

audio_stream = pyaudio.PyAudio().open(
    format=FORMAT,
    channels=CHANNELS,
    rate=RATE,
    input=True,
    frames_per_buffer=CHUNK
)

while True:
    command = input("Enter command (S/F): ").strip().upper()
    if command == 'S' or command == 'F':
        send_command(command)
    else:
        print("Invalid command. Please enter 'S' or 'F'.")

    if command == 'S':
        while True:
            data = audio_stream.read(CHUNK)
            client_socket.send(data)
