import socket
import threading
import pyaudio

# Client configuration
SERVER_HOST = 'your_server_ip'
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
    while True:
        data = stream.read(CHUNK)
        client_socket.sendall(data)

def receive_and_play(client_socket):
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True, frames_per_buffer=CHUNK)
    while True:
        try:
            data = client_socket.recv(1024)
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

    threading.Thread(target=record_and_send, args=(client_socket,)).start()
    receive_and_play(client_socket)

if __name__ == "__main__":
    start_client()
