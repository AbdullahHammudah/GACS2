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
lock = threading.Lock()

control_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
control_socket.bind(ADDR_CONTROL)
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
                client.close()

def start_voice_channel(control_addr, voice_conn, voice_addr):
    if control_addr[0] == voice_addr[0]:
        while True:
            try:
                voice_data = voice_conn.recv(1024)
                if not voice_data:
                    break
                broadcast(voice_data, except_client=voice_conn)
            except Exception as e:
                print(f"Client finished speaking {voice_addr}: {e}")
                break
    voice_conn.close()

def handle_client(control_conn, control_addr, voice_conn, voice_addr):
    global speaking_client
    print(f"[CONTROL CONNECTION] Client {control_addr} has established Control Connection")
    print(f"[VOICE CONNECTION] Client {voice_addr} has established Voice Connection")

    try: 
        while True:
            try:
                control_msg = control_conn.recv(1024).decode(FORMAT)
                if not control_msg:
                    break
                print(f"[{control_addr}] {control_msg}")
                if control_msg == 'S':
                    with lock:
                        if speaking_client is None:
                            control_conn.send(b"Permission to speak granted")
                            speaking_client = control_conn
                            voice_thread = threading.Thread(target=start_voice_channel, args=(control_addr, voice_conn, voice_addr))
                            voice_thread.start()
                        else:
                            control_conn.send(b"Someone else is speaking")
                elif control_msg == 'F':
                    with lock:
                        if speaking_client == control_conn:
                            speaking_client = None
                            control_conn.send(b"Speaking is over")
                        control_conn.send(b"Voice connection has been closed")
            except ConnectionResetError:
                print(f"Connection lost with {control_addr}")
                break
            except Exception as e:
                print(f"Error in control channel with {control_addr}: {e}")
                break
    finally:
        control_conn.close()
        voice_conn.close()
        if voice_conn in clients:
            clients.remove(voice_conn)
        with lock:
            if speaking_client == control_conn:
                speaking_client = None
        print(f"Connection with {control_addr} and {voice_addr} closed")

def start():
    control_socket.listen()
    voice_socket.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        control_conn, control_addr = control_socket.accept()
        voice_conn, voice_addr = voice_socket.accept()
        clients.append(voice_conn)
        threading.Thread(target=handle_client, args=(control_conn, control_addr, voice_conn, voice_addr)).start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

print("[STARTING] server is starting...")
start()
