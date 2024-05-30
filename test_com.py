from vidstream import AudioSender, AudioReceiver
import threading
import time

class AudioChat:
    def __init__(self, send_ip, send_port, receive_ip, receive_port):
        self.sender = AudioSender(send_ip, send_port)
        self.receiver = AudioReceiver(receive_ip, receive_port)
        self.mode = 'receive'  # Start in receive mode
        self.mode_lock = threading.Lock()

    def start_receiving(self):
        with self.mode_lock:
            if self.mode == 'receive':
                print("Receiving audio...")
                self.receiver.start_server()
                # Sleep or wait for a signal to switch mode
                time.sleep(15)  # This should be replaced with actual condition
                self.mode = 'send'
                print("Switching to send mode...")

    def start_sending(self):
        with self.mode_lock:
            if self.mode == 'send':
                print("Sending audio...")
                self.sender.start_stream()
                # Sleep or wait for a signal to switch mode
                time.sleep(15)  # This should be replaced with actual condition
                self.mode = 'receive'
                print("Switching to receive mode...")

    def run(self):
        while True:
            if self.mode == 'receive':
                receive_thread = threading.Thread(target=self.start_receiving)
                receive_thread.start()
                time.sleep(15)  # This should be replaced with actual condition
                # receive_thread.join()  # Wait for receiving to finish
            elif self.mode == 'send':
                send_thread = threading.Thread(target=self.start_sending)
                send_thread.start()
                time.sleep(15)  # This should be replaced with actual condition
                # send_thread.join()  # Wait for sending to finish

if __name__ == "__main__":
    # Replace these with your actual IP addresses and ports
    send_ip = '192.168.0.172'
    send_port = 5555
    receive_ip = '192.168.0.207'
    receive_port = 9999

    chat = AudioChat(send_ip, send_port, receive_ip, receive_port)
    chat.run()
