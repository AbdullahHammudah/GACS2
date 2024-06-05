import socket
import threading
import pyaudio

# Client configuration
SERVER_HOST = '192.168.10.2'  # Change to your server's IP address
CONTROL_PORT = 5000
VOICE_PORT = 5001

# Audio configuration
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

# Initialize PyAudio
p = pyaudio.PyAudio()

# Flag to control the recording thread
is_recording = threading.Event()

def control(control_socket, voice_socket):
    global is_recording
    while True:
        command = input("Enter command (S/F): ").strip().upper()
        if command == 'S' or command == 'F':
            control_socket.send(command.encode())
            response = control_socket.recv(1024).decode()
            print(response)
            if response == "Permission granted to speak":
                is_recording.set()  # Set the event to start recording
                threading.Thread(target=record_and_send, args=(voice_socket,)).start()
            elif command == 'F':
                is_recording.clear()  # Clear the event to stop recording
        else:
            print("Invalid command. Please enter 'S' or 'F'.")

def record_and_send(voice_socket):
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    print("Recording and sending...")
    while is_recording.is_set():
        try:
            data = stream.read(CHUNK, exception_on_overflow=False)
            voice_socket.sendall(data)
        except Exception as e:
            print(f"Error recording and sending data: {e}")
            break
    stream.stop_stream()
    stream.close()
    print("Recording stopped.")

def receive_and_play(voice_socket):
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True, frames_per_buffer=CHUNK)
    print("Receiving and playing...")
    while True:
        try:
            data = voice_socket.recv(CHUNK)
            if not data:
                break
            stream.write(data)
        except Exception as e:
            print(f"Error receiving data: {e}")
            break
    stream.stop_stream()
    stream.close()

def start_client():
    voice_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    voice_socket.connect((SERVER_HOST, VOICE_PORT))
    print("Connected to voice server.")

    control_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    control_socket.connect((SERVER_HOST, CONTROL_PORT))
    print("Connected to control server.")

    receive_thread = threading.Thread(target=receive_and_play, args=(voice_socket,))
    receive_thread.start()
    control(control_socket, voice_socket)
    receive_thread.join()

if __name__ == "__main__":
    start_client()
