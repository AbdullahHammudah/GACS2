import socket
import threading
import queue
import pyaudio

# Client configuration
SERVER_HOST = '192.168.10.2'
SERVER_PORT = 5000

# Audio configuration
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

# Initialize PyAudio
p = pyaudio.PyAudio()

def send_command(command):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_HOST, SERVER_PORT))
    client_socket.sendall(command.encode())
    client_socket.close()

def send_voice():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_HOST, SERVER_PORT))

    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    print("Recording and sending...")
    while True:
        try:
            data = stream.read(CHUNK, exception_on_overflow=False)
            client_socket.sendall(data)
        except Exception as e:
            print(f"Error recording and sending data: {e}")
            break

def start_client():
    while True:
        command = input("Type 'SPEAK' to request to speak or 'FINISH' to finish speaking: ")
        send_command(command)
        if command == "SPEAK":
            response = input("Press Enter to start speaking: ")
            if response == "":
                threading.Thread(target=send_voice).start()  # Start voice communication thread
        elif command == "FINISH":
            break

if __name__ == "__main__":
    start_client()
