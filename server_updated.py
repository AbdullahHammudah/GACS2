import socket
import threading

# Server configuration
HOST = '0.0.0.0'  # Listen on all interfaces
C_PORT = 5000
V_PORT = 5001

clients = []
speaking_client_lock = threading.Lock()
speaking_client = None

def broadcast(data, except_client=None):
    for client in clients:
        if client != except_client:
            try:
                client.sendall(data)
            except Exception as e:
                print(f"Error sending data to client: {e}")
                clients.remove(client)

def handle_voice(voice_connection):
    while True:
        try:
            data = voice_connection.recv(1024)
            if not data:
                break
            broadcast(data, except_client=voice_connection)
        except Exception as e:
            print(f"Error receiving voice data: {e}")
            break
    voice_connection.close()

def handle_control(control_connection, voice_connection):
    global speaking_client
    while True:
        try:
            request = control_connection.recv(1024).decode().strip()
            if request == 'S':
                with speaking_client_lock:
                    if speaking_client is None:
                        speaking_client = voice_connection
                        control_connection.send(b"Permission granted to speak")
                        handle_voice(voice_connection)
                    else:
                        control_connection.send(b"Please wait, voice channel is occupied")
            elif request == 'F':
                with speaking_client_lock:
                    if speaking_client == voice_connection:
                        speaking_client = None
                        control_connection.send(b"Speaking is over")
                        break
                    else:
                        control_connection.send(b"You are not the current speaker")
        except Exception as e:
            print(f"Error handling control command: {e}")
            break
    control_connection.close()
    voice_connection.close()

def start_server():
    control_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    control_socket.bind((HOST, C_PORT))
    control_socket.listen(5)
    print(f"Server listening on {HOST}:{C_PORT}")

    voice_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    voice_socket.bind((HOST, V_PORT))
    voice_socket.listen(5)
    print(f"Voice server listening on {HOST}:{V_PORT}")

    while True:
        control_connection, addr = control_socket.accept()
        voice_connection, addr = voice_socket.accept()
        print(f"Connection from {addr}")
        clients.append(control_connection)
        threading.Thread(target=handle_control, args=(control_connection, voice_connection)).start()

if __name__ == "__main__":
    start_server()
