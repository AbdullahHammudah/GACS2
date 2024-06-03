import socket

# Client configuration
SERVER_HOST = '192.168.10.2'
SERVER_PORT = 5000

def start_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_HOST, SERVER_PORT))
    print("Connected to server.")

    while True:
        command = input("Type 'S' to request to speak or 'F' to finish speaking: ")
        client_socket.sendall(command.encode())
        response = client_socket.recv(1024).decode()
        if response == "WAIT":
            print("Another user is already speaking. Please wait.")
        elif response == "START_SPEAK":
            print("You can start speaking.")
        elif response == "END_SPEAK":
            print("You finished speaking.")
            break

    client_socket.close()

if __name__ == "__main__":
    start_client()
