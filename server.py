import socket
import threading

# Server configuration
HOST = '0.0.0.0'  # Listen on all interfaces
PORT = 5000

clients = []
speaking_client = None
speaking_lock = threading.Lock()

def broadcast(data, except_client=None):
    for client in clients:
        if client != except_client:
            try:
                client.sendall(data)
            except Exception as e:
                print(f"Error sending data to client: {e}")
                clients.remove(client)

def handle_commands(client_socket):
    global speaking_client
    while True:
        try:
            command = client_socket.recv(1024).decode().strip()
            if not command:
                break

            if command == "S" and (speaking_client is None or speaking_client == client_socket):
                speaking_client = client_socket
                broadcast("START_SPEAK".encode(), except_client=client_socket)
            elif command == "F" and speaking_client == client_socket:
                speaking_client = None
                broadcast("END_SPEAK".encode())
            else:
                client_socket.sendall(b'WAIT')  # Notify client to wait
        except Exception as e:
            print(f"Error handling command: {e}")
            break

    if speaking_client == client_socket:
        speaking_client = None

    client_socket.close()
    clients.remove(client_socket)

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    print(f"Server listening on {HOST}:{PORT}")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"Connection from {addr}")
        clients.append(client_socket)
        threading.Thread(target=handle_commands, args=(client_socket,)).start()

if __name__ == "__main__":
    start_server()
