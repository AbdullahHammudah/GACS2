import socket
import threading
import pyaudio

# Client configuration
SERVER_HOST = '192.168.10.2'
CONTROL_PORT = 5000
VOICE_PORT = 5001

# Audio configuration
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

# Initialize PyAudio
p = pyaudio.PyAudio()

def control (control_socket, voice_socket):
    while True:
        command = input("Enter command (S/F): ").strip().upper()
        if command == 'S' or command == 'F':
            control_socket.send(command.encode())
            response = control_socket.recv(1024).decode()
            print(response)
            if response == "Permission granited to speak":
                threading.Thread(target=record_and_send, args=(voice_socket,)).start()
        else:
            print("Invalid command. Please enter 'S' or 'F'.")


def record_and_send(voice_socket):
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    print("Recording and sending...")
    while True:
        try:
            data = stream.read(CHUNK, exception_on_overflow=False)
            voice_socket.sendall(data)
        except Exception as e:
            print(f"Error recording and sending data: {e}")
            break


def receive_and_play(voice_socket):
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True, frames_per_buffer=CHUNK)
    print("Receiving and playing...")
    while True:
        try:
            data = voice_socket.recv(CHUNK)
            if not data:
                break
            print("Playing data...")
            stream.write(data)
        except Exception as e:
            print(f"Error receiving data: {e}")
            break

    stream.close()

def start_client():
    voice_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    voice_socket.connect((SERVER_HOST, VOICE_PORT))
    print("Connected to server.")

    control_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    control_socket.connect((SERVER_HOST, CONTROL_PORT))

    control (control_socket, voice_socket)

    receive_and_play(voice_socket)

if __name__ == "__main__":
    start_client()
