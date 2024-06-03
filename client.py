import socket
import threading
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

def record_and_send(client_socket):
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    print("Recording and sending...")
    while True:
        try:
            data = stream.read(CHUNK, exception_on_overflow=False)
            client_socket.sendall(data)
            response = client_socket.recv(4)
            if response == b'WAIT':
                print("Waiting for turn to speak...")
                while True:
                    response = client_socket.recv(4)
                    if response != b'WAIT':
                        break
        except Exception as e:
            print(f"Error recording and sending data: {e}")
            break

def receive_and_play(client_socket):
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True, frames_per_buffer=CHUNK)
    print("Receiving and playing...")
    while True:
        try:
            data = client_socket.recv(CHUNK)
            if not data:
                break
            stream.write(data)
        except Exception as e:
            print(f"Error receiving data: {e}")
            break

    stream.close()

def start_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_HOST, SERVER_PORT))
    print("Connected to server.")

    threading.Thread(target=record_and_send, args=(client_socket,)).start()
    receive_and_play(client_socket)

if __name__ == "__main__":
    start_client()
