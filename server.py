import socket
import threading
import pyaudio

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024

def handle_audio(client_socket):
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    output=True,
                    frames_per_buffer=CHUNK)
    
    while True:
        try:
            data = client_socket.recv(CHUNK)
            if not data:
                break
            stream.write(data)
        except Exception as e:
            print("Error:", e)
            break
    
    stream.stop_stream()
    stream.close()
    p.terminate()

def handle_client(client_socket, client_address):
    global speaking_client
    audio_thread = threading.Thread(target=handle_audio, args=(client_socket,))
    audio_thread.start()
    
    while True:
        request = client_socket.recv(1024).decode().strip()
        if request == 'S':
            if speaking_client is None:
                speaking_client = client_socket
                client_socket.send("Permission granted. You can speak now.".encode())
            else:
                client_socket.send("Another client is speaking. Please wait.".encode())
        elif request == 'F':
            if speaking_client == client_socket:
                speaking_client = None
                client_socket.send("You finished speaking. Waiting for next speaker.".encode())
            else:
                client_socket.send("You are not the current speaker.".encode())
        else:
            client_socket.send("Invalid command.".encode())

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('0.0.0.0', 9999))
server.listen(5)

speaking_client = None

while True:
    client_socket, client_address = server.accept()
    client_handler = threading.Thread(target=handle_client, args=(client_socket, client_address))
    client_handler.start()
