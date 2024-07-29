import socket
import threading

class ChatClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.nickname = input("Enter your nickname: ")

    def start_client(self):
        self.client_socket.connect((self.host, self.port))
        self.client_socket.sendall(f"/register {self.nickname}".encode())
        
        threading.Thread(target=self.receive_messages).start()

        while True:
            message = input()
            self.client_socket.sendall(message.encode())

    def receive_messages(self):
        while True:
            message = self.client_socket.recv(1024).decode()
            if message:
                print(message)
            else:
                break

if __name__ == '__main__':
    client = ChatClient(host='127.0.0.1', port=12345)
    client.start_client()
