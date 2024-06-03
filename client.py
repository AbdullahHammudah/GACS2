import socket
import threading
import pyaudio
import time
import numpy as np

# Client configuration
SERVER_HOST = '192.168.10.2'
SERVER_PORT = 5000

# Audio configuration
CHUNK = 512
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
THRESHOLD = 500  # Noise gate threshold

# Initialize PyAudio
p = pyaudio.PyAudio()

def noise_gate(data, threshold):
    audio_data = np.frombuffer(data, dtype=np.int16)
    audio_data = np.where(np.abs(audio_data) < threshold, 0, audio_data)
    return audio_data.tobytes()

def record_and_send(client_socket):
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    while True:
        try:
            data = stream.read(CHUNK, exception_on_overflow=False)
            client_socket.sendall(data)
        except Exception as e:
            print(f"Error recording and sending data: {e}")
            break

def receive_and_play(client_socket):
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True, frames_per_buffer=CHUNK)
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

    threading.Thread(target=record_and_send, args=(client_socket,)).start()
    receive_and_play(client_socket)

if __name__ == "__main__":
    start_client()
