import socket
import threading

# test version

# Server configuration
HOST = '0.0.0.0'  # Listen on all interfaces
C_PORT = 5000
V_PORT = 5001

clients = []

def broadcast(data, except_client=None):
    for client in clients:
        if client != except_client:
            try:
                client.sendall(data)
            except Exception as e:
                print(f"Error sending data to client: {e}")
                clients.remove(client)

def start_voice_connection(voice_connection):
    while True:
        data = voice_connection.recv(1024)
        broadcast(data, except_client=speaking_client)

def end_voice_connection(voice_connection):
    voice_connection.close()

def permission_control(control_connection,voice_connection):
    global speaking_client
    request = control_connection.recv(1024).decode().strip()
    if request == 'S':
        if speaking_client is None:
            speaking_client = voice_connection
            control_connection.send(b"Permission granited to speak")
            start_voice_connection(voice_connection)

    elif request == 'F':
        if speaking_client == voice_connection:
            speaking_client = None
            control_connection.send(b"Speaking is Over")
            end_voice_connection()


    elif speaking_client is not None:
        control_connection.send(b"Please wait, voice channel is occupied")

speaking_client = None

def start_server():
    control_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    control_socket.bind((HOST, C_PORT))
    control_socket.listen(5)
    print(f"Server listening on {HOST}:{C_PORT}")
    voice_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    voice_socket.bind((HOST, V_PORT))
    voice_socket.listen(5)



    while True:
        control_connection, addr = control_socket.accept()
        voice_connection, addr = voice_socket.accept()
        print(f"Connection from {addr}")
        clients.append(control_connection) 
        threading.Thread(target=permission_control, args=(control_connection, voice_connection)).start()

if __name__ == "__main__":
    start_server()