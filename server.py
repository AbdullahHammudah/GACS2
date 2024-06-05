import socket
import threading

# Server configuration
SERVER = "192.168.10.2"
PORT_C = 5050
PORT_V = 5051
ADDR_CONTROL = (SERVER, PORT_C)
ADDR_VOICE = (SERVER, PORT_V)
FORMAT = "utf-8"

clients = []
speaking_client = None

control_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
control_server.bind(ADDR_CONTROL)
voice_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
voice_socket.bind(ADDR_VOICE)

def broadcast(data, except_client=None):
    for client in clients:
        if client != except_client:
            try:
                client.sendall(data)
            except Exception as e:
                print(f"Error sending data to client: {e}")
                clients.remove(client)

def start_voice_channel (control_addr, stop_event):
    while not stop_event.is_set():
        voice_conn, voice_addr = voice_socket.accept()
        if control_addr[0] == voice_addr[0]:
            voice_connection = True
            while voice_connection:
                voice_data = voice_conn.recv(1024)
                broadcast(voice_data, except_client=voice_conn)

def handle_client (control_conn, control_addr):
    global speaking_client
    print(f"[NEW CONNECTION] {control_addr} connected.")

    connected = True
    while connected:
        control_msg = control_conn.recv(1024).decode(FORMAT)
        print(f"[{control_addr}] {control_msg}")
        if control_msg == 'S' and speaking_client == None:
            control_conn.send(b"Permission to speak granted")
            speaking_client = control_conn
            stop_event = threading.Event()
            voice_thread = threading.Thread(target=start_voice_channel, args=(control_addr, stop_event))
            voice_thread.start()

        elif control_msg == 'F':
            control_conn.send(b"Speaking is Over")
            stop_event.set()
            voice_thread.join()
            control_conn.send(b"Voice connection has been closed")

def start():
    control_server.listen()
    voice_socket.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        control_conn, control_addr = control_server.accept()
        threading.Thread(target=handle_client, args=(control_conn, control_addr)).start()
        clients.append(control_conn)
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

print("[STARTING] server is starting...")
start()