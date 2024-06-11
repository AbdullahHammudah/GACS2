import socket
import threading

# Version 0.9 - Core Functionality

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

def start_voice_channel(control_addr, voice_conn, voice_addr):
    global close_voice_connection
    if control_addr[0] == voice_addr[0]:
        voice_connection = True
        while voice_connection:
            try:
                if close_voice_connection:
                    break
                voice_data = voice_conn.recv(1024)
                if not voice_data:
                    break
                broadcast(voice_data, except_client=voice_conn)
            except Exception as e:
                print(f"Client Finsihed Speaking {voice_addr}: {e}")
                break


def handle_client (control_conn, control_addr, voice_conn, voice_addr):
    global close_voice_connection
    global speaking_client
    print(f"[CONTROL CONNECTION] Client {control_addr} has establised Contol Connection")
    print(f"[VOICE CONNECTION] Client {voice_addr} has establised Voice Connection")

   
    try: 
        connected = True
        while connected:
            control_msg = control_conn.recv(1024).decode(FORMAT)
            print(f"[{control_addr}] {control_msg}")
            if control_msg == 'S' and speaking_client == None:
                control_conn.send(b"Permission to speak granted")
                speaking_client = control_conn
                close_voice_connection = False
                voice_thread = threading.Thread(target=start_voice_channel, args=(control_addr, voice_conn, voice_addr))
                voice_thread.start()
            elif control_msg == 'S' and speaking_client != None:
                control_conn.send(b"Channel Is Occupied, Someone is speaking, Listen Idiot!")


            elif control_msg == 'F':
                control_conn.send(b"Speaking is Over, ")
                speaking_client = None
                close_voice_connection = True
                voice_thread.join()
                control_conn.send(b"Voice connection has been closed")
    except Exception as e:
        print(f"Connection Problem {e}")


def start():
    control_socket.listen()
    voice_socket.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        control_conn, control_addr = control_socket.accept()
        voice_conn, voice_addr = voice_socket.accept()
        threading.Thread(target=handle_client, args=(control_conn, control_addr, voice_conn, voice_addr)).start()
        clients.append(voice_conn)
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

print("[STARTING] server is starting...")
start()