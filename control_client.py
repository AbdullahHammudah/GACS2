import socket

SERVER = "192.168.10.2"
PORT = 5050
ADDR = (SERVER, PORT)
FORMAT = "utf-8"

control_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
control_client.connect(ADDR)

def send_command():
    while True:
        control_command = input("Enter command (S/F): ").strip().upper()
        response = control_client.send(control_command).encode(FORMAT)
        print(response)
