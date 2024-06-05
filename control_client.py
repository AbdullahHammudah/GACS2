import socket
import time

SERVER = "192.168.10.2"
PORT = 5050
ADDR = (SERVER, PORT)
FORMAT = "utf-8"

control_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
control_client.connect(ADDR)

def send_command():
    while True:
        control_command = input("Enter command (S/F): ").strip().upper()
        encoded_control_command = control_command.encode(FORMAT)
        control_client.send(encoded_control_command)
        time.sleep(0.2)
        response = control_client.recv(1024).decode(FORMAT)
        print(response)

send_command()