import socket
import threading

SERVER = "192.168.10.2"
PORT = 5050
ADDR = (SERVER, PORT)
FORMAT = "utf-8"

control_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
control_server.bind(ADDR)

def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")
    
    connected = True
    while connected:
        control_msg = conn.recv(1024).decode(FORMAT)
        print(f"[{addr}] {control_msg}")
        if control_msg == 'S':
            conn.send(b"Permission to speak granted")
        elif control_msg == 'F':
            conn.send(b"Speaking is Over")
            

def start():
    control_server.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        conn, addr = control_server.accept()
        threading.Thread(target=handle_client, args=(conn, addr)).start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")


print("[STARTING] server is starting...")
start()