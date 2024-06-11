import socket
import threading

# Server configuration
SERVER = "127.0.0.1"
PORT_C = 5050
PORT_V = 5051
ADDR_CONTROL = (SERVER, PORT_C)
ADDR_VOICE = (SERVER, PORT_V)
FORMAT = "utf-8"

clients = []
speaking_client = None
close_voice_connection = False

control_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
control_socket.bind(ADDR_CONTROL)
voice_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
voice_socket.bind(ADDR_VOICE)

def broadcast(data, except_client=None):
    for client in clients:
        if client != except_client:
            try:
                voice_socket.sendto(data, client)
            except Exception as e:
                print(f"Error sending data to client: {e}")
                clients.remove(client)

def start_voice_channel(control_addr):
    global close_voice_connection
    voice_connection = True
    while voice_connection:
        try:
            if close_voice_connection:
                break
            voice_data, client_addr = voice_socket.recvfrom(4096)
            if control_addr[0] == client_addr[0]:
                if not voice_data:
                    break
                broadcast(voice_data)
        except Exception as e:
            print(f"Error in Voice Channel: {e}")
            break


def handle_client (control_conn, control_addr):
    global close_voice_connection
    global speaking_client
    print(f"[CONTROL CONNECTION] Client {control_addr} has establised Contol Connection")

   
    try: 
        connected = True
        while connected:
            control_msg = control_conn.recv(1024).decode(FORMAT)
            print(f"[{control_addr}] {control_msg}")
            if control_msg == 'S' and speaking_client == None:
                control_conn.send(b"Permission to speak granted")
                speaking_client = control_conn
                close_voice_connection = False
                voice_thread = threading.Thread(target=start_voice_channel, args=(control_addr,))
                voice_thread.start()


            elif control_msg == 'F':
                speaking_client = None
                close_voice_connection = True
                voice_thread.join()
                control_conn.send(b"Voice connection has been closed")
    except Exception as e:
        print(f"Connection Problem {e}")


def start():
    control_socket.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        control_conn, control_addr = control_socket.accept()
        threading.Thread(target=handle_client, args=(control_conn, control_addr)).start()
        voice_addr = (control_addr[0], 9999)
        clients.append(voice_addr)
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

print("[STARTING] server is starting...")
start()