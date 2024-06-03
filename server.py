import socket
import threading

# Server configuration
HOST = '0.0.0.0'  # Listen on all interfaces
PORT = 5000

clients = ['192.168.10.4', '192.168.10.3']
speaking_client = None

def broadcast(data, except_client=None):
    for client in clients:
        if client != except_client:
            try:
                client.sendall(data)
            except Exception as e:
                print(f"Error sending data to client: {e}")
                clients.remove(client)

def handle_client(client_socket):
    global speaking_client
    while True:
        try:
            data = client_socket.recv(512)
            if not data:
                break
            if speaking_client is None or speaking_client == client_socket:
                speaking_client = client_socket
                broadcast(data, except_client=client_socket)
            else:
                client_socket.sendall(b"Wait for the other user to finish speaking.")
        except Exception as e:
            print(f"Client connection error: {e}")
            break

    client_socket.close()
    clients.remove(client_socket)
    if speaking_client == client_socket:
        speaking_client = None

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    print(f"Server listening on {HOST}:{PORT}")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"Connection from {addr}")
        clients.append(client_socket)
        threading.Thread(target=handle_client, args=(client_socket,)).start()

if __name__ == "__main__":
    start_server()
