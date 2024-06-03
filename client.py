import socket
import threading

# Client configuration
SERVER_HOST = '192.168.10.2'
SERVER_PORT = 5000

def start_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_HOST, SERVER_PORT))
    print("Connected to server.")

    def send_request():
        while True:
            command = input("Type 'SPEAK' to request to speak or 'FINISH' to finish speaking: ")
            try:
                client_socket.sendall(command.encode())
                if command == "SPEAK":
                    response = client_socket.recv(1024)
                    if response.decode() == "WAIT":
                        print("Waiting for turn to speak...")
                    elif response.decode() == "START_SPEAK":
                        print("You can start speaking.")
                elif command == "FINISH":
                    print("You finished speaking.")
            except Exception as e:
                print(f"Error sending request: {e}")
                break

    threading.Thread(target=send_request).start()

if __name__ == "__main__":
    start_client()
