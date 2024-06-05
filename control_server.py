import socket
import threading

SERVER = "192.168.10.2"
PORT = 5050
ADDR = (SERVER, PORT)
FORMAT = "utf-8"

control_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
control_server.bind(ADDR)

def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connrcted.")
    
    connected = True
    while connected:
        control_msg = conn.recv(1024).decode(FORMAT)
        print(f"[{addr}] {control_msg}")
        if control_msg == 'S':
            conn.send("Permission to speak granted").encode(FORMAT)
        elif control_msg == 'F':
            conn.send("Speaking is Over").encode(FORMAT)
            

def start():
    control_server.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        conn, addr = control_server.accept()
        threading.Thread(target=handle_client, args=(conn, addr)).start()
        print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")


print("[STARTING] server is starting...")
start()