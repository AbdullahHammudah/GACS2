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

def start_voice():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_HOST, SERVER_PORT))

    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    print("Recording and sending...")
    while True:
        try:
            data = stream.read(CHUNK)
            client_socket.sendall(data)
        except Exception as e:
            print(f"Error recording and sending data: {e}")
            break

    stream.stop_stream()
    stream.close()
    client_socket.close()

def start_client():
    threading.Thread(target=start_voice).start()

if __name__ == "__main__":
    start_client()
