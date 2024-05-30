from vidstream import AudioSender, AudioReceiver
import threading
import time

class GACS2:
    def __init__(self, send_ip, send_port, receive_ip, receive_port):
        self.sender = AudioSender(send_ip, send_port)
        self.receiver = AudioReceiver(receive_ip, receive_port)
        self.mode = 'receive'  # Start in receive mode
        self.mode_lock = threading.Lock()
        self.condition = threading.Condition()
        self.running = True

    def start_receiving(self):
        with self.condition:
            while self.mode == 'receive' and self.running:
                print("Receiving audio...")
                self.receiver.start_server()
                self.condition.wait()  # Wait until notified to switch mode
                self.receiver.stop_server()
                if self.running:
                    self.mode = 'send'
                    self.condition.notify_all()

    def start_sending(self):
        with self.condition:
            while self.mode == 'send' and self.running:
                print("Sending audio...")
                self.sender.start_stream()
                self.condition.wait()  # Wait until notified to switch mode
                self.sender.stop_stream()
                if self.running:
                    self.mode = 'receive'
                    self.condition.notify_all()

    def run(self):
        receive_thread = threading.Thread(target=self.start_receiving)
        send_thread = threading.Thread(target=self.start_sending)

        receive_thread.start()
        send_thread.start()

        try:
            while self.running:
                with self.condition:
                    # Simulate switching every 15 seconds for testing purposes
                    time.sleep(15)
                    self.condition.notify_all()  # Notify to switch mode
        except KeyboardInterrupt:
            self.stop()

        receive_thread.join()
        send_thread.join()

    def stop(self):
        with self.condition:
            self.running = False
            self.condition.notify_all()
        print("Stopping audio chat...")

if __name__ == "__main__":
    # Replace these with your actual IP addresses and ports
    send_ip = '192.168.10.3'
    send_port = 5555
    receive_ip = '192.168.10.2'
    receive_port = 9999

    chat = AudioChat(send_ip, send_port, receive_ip, receive_port)
    chat.run()
