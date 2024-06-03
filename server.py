import socket
import threading
import queue

# Server configuration
HOST = '0.0.0.0'  # Listen on all interfaces
PORT = 5000

clients = []
speaking_client = None
speaking_lock = threading.Lock()
command_queue = queue.Queue()

def broadcast(data, except_client=None):
    for client in clients:
        if client != except_client:
            try:
                client.sendall(data)
            except Exception as e:
                print(f"Error sending data to client: {e}")
                clients.remove(client)

def handle_commands():
    global speaking_client
    while True:
        client_socket, command = command_queue.get()
        try:
            with speaking_lock:
                if command == "SPEAK" and (speaking_client is None or speaking_client == client_socket):
                    speaking_client = client_socket
                    broadcast("START_SPEAK".encode(), except_client=client_socket)
                elif command == "FINISH" and speaking_client == client_socket:
                    speaking_client = None
                    broadcast("END_SPEAK".encode())
                else:
                    client_socket.sendall(b'WAIT')  # Notify client to wait
        except Exception as e:
            print(f"Error handling command: {e}")
            break

def handle_voice(client_socket):
    try:
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            with speaking_lock:
                if speaking_client == client_socket:
                    broadcast(data, except_client=client_socket)
    except Exception as e:
        print(f"Error handling voice communication: {e}")

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    print(f"Server listening on {HOST}:{PORT}")

    threading.Thread(target=handle_commands).start()

    while True:
        client_socket, addr = server_socket.accept()
        print(f"Connection from {addr}")
        clients.append(client_socket)
        threading.Thread(target=handle_voice, args=(client_socket,)).start()

if __name__ == "__main__":
    start_server()
