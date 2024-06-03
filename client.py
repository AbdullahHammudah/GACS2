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

def start_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_HOST, SERVER_PORT))
    print("Connected to server.")

    def send_request():
        while True:
            command = input("Type 'SPEAK' to request to speak or 'FINISH' to finish speaking: ")
            try:
                client_socket.sendall(command.encode())
                if command == "SPEAK":
                    response = client_socket.recv(1024)
                    if response.decode() == "WAIT":
                        print("Waiting for turn to speak...")
                    elif response.decode() == "START_SPEAK":
                        print("You can start speaking.")
                        record_and_send(client_socket)
                elif command == "FINISH":
                    print("You finished speaking.")
            except Exception as e:
                print(f"Error sending request: {e}")
                break

    def record_and_send(client_socket):
        stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
        print("Recording and sending...")
        while True:
            try:
                data = stream.read(CHUNK, exception_on_overflow=False)
                client_socket.sendall(data)
            except Exception as e:
                print(f"Error recording and sending data: {e}")
                break

    threading.Thread(target=send_request).start()

if __name__ == "__main__":
    start_client()
