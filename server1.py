import socket
import select
import logging
import argparse
import json
import logging.handlers

class ChatServer:
    def __init__(self, host, port, max_users, log_level):
        self.host = host
        self.port = port
        self.max_users = max_users
        self.clients = {}
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Настройка логирования
        logging.basicConfig(level=log_level, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

        # Настройка syslog
        syslog_handler = logging.handlers.SysLogHandler(address='/dev/log')
        syslog_handler.setLevel(log_level)
        syslog_formatter = logging.Formatter('%(name)s: %(levelname)s %(message)s')
        syslog_handler.setFormatter(syslog_formatter)
        self.logger.addHandler(syslog_handler)

    def start_server(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(self.max_users)
        self.logger.info(f'Server started on {self.host}:{self.port}')
        
        inputs = [self.server_socket]
        outputs = []

        while True:
            readable, writable, exceptional = select.select(inputs, outputs, inputs)
            
            for s in readable:
                if s is self.server_socket:
                    client_socket, client_address = s.accept()
                    self.logger.info(f'New connection from {client_address}')
                    inputs.append(client_socket)
                    self.clients[client_socket] = {"address": client_address, "nickname": None}
                else:
                    try:
                        data = s.recv(1024)
                        if data:
                            self.handle_message(s, data.decode().strip())
                        else:
                            self.logger.info(f'Connection closed by {self.clients[s]["address"]}')
                            inputs.remove(s)
                            del self.clients[s]
                            s.close()
                    except ConnectionResetError:
                        self.logger.info(f'Connection reset by {self.clients[s]["address"]}')
                        inputs.remove(s)
                        del self.clients[s]
                        s.close()
                    except Exception as e:
                        self.logger.error(f'Error handling message from {self.clients[s]["address"]}: {e}')
                        inputs.remove(s)
                        del self.clients[s]
                        s.close()

    def handle_message(self, client_socket, message):
        if message.startswith('/'):
            self.handle_command(client_socket, message)
        else:
            self.handle_chat_message(client_socket, message)

    def handle_command(self, client_socket, message):
        parts = message.split(' ', 1)
        command = parts[0]
        
        if command == '/register':
            if len(parts) < 2:
                client_socket.sendall("Usage: /register <nickname>".encode())
            else:
                self.register_nickname(client_socket, parts[1])
        elif command == '/nick':
            if len(parts) < 2:
                client_socket.sendall("Usage: /nick <new_nickname>".encode())
            else:
                self.change_nickname(client_socket, parts[1])
        elif command == '/exit':
            self.logger.info(f'{self.clients[client_socket]["address"]} disconnected')
            client_socket.sendall("Disconnecting...".encode())
            client_socket.close()
            del self.clients[client_socket]
        else:
            client_socket.sendall(f"Unknown command: {command}".encode())

    def register_nickname(self, client_socket, nickname):
        if self.clients[client_socket]["nickname"] is None:
            for client, info in self.clients.items():
                if info["nickname"] == nickname:
                    client_socket.sendall(f"Nickname {nickname} is already taken".encode())
                    return
            self.clients[client_socket]["nickname"] = nickname
            client_socket.sendall(f"Nickname set to {nickname}".encode())
        else:
            client_socket.sendall("You are already registered".encode())

    def change_nickname(self, client_socket, new_nickname):
        old_nickname = self.clients[client_socket]["nickname"]
        if old_nickname is None:
            client_socket.sendall("You are not registered. Use /register <nickname>".encode())
            return

        for client, info in self.clients.items():
            if info["nickname"] == new_nickname:
                client_socket.sendall(f"Nickname {new_nickname} is already taken".encode())
                return

        self.clients[client_socket]["nickname"] = new_nickname
        client_socket.sendall(f"Nickname changed from {old_nickname} to {new_nickname}".encode())

    def handle_chat_message(self, client_socket, message):
        if self.clients[client_socket]["nickname"] is None:
            client_socket.sendall("You must register with /register <nickname> before sending messages".encode())
            return

        parts = message.split(' ', 1)
        if len(parts) < 2:
            client_socket.sendall("Invalid message format. Use '<nickname> <message>'".encode())
            return

        recipient_nickname, actual_message = parts
        sender_nickname = self.clients[client_socket]["nickname"]

        recipient_socket = None
        for client, info in self.clients.items():
            if info["nickname"] == recipient_nickname:
                recipient_socket = client
                break

        if recipient_socket:
            try:
                recipient_socket.sendall(f'{sender_nickname}: {actual_message}'.encode())
                client_socket.sendall("Message sent successfully".encode())
            except Exception as e:
                self.logger.error(f"Failed to send message: {e}")
                client_socket.sendall("Failed to send message".encode())
        else:
            client_socket.sendall(f'User {recipient_nickname} not found'.encode())

def main():
    parser = argparse.ArgumentParser(description="Start the chat server.")
    parser.add_argument('--config', required=True, help='Path to the config file')
    args = parser.parse_args()

    with open(args.config, 'r') as f:
        config = json.load(f)

    server = ChatServer(
        host=config['host'], 
        port=config['port'], 
        max_users=config['max_users'], 
        log_level=config['log_level']
    )
    server.start_server()

if __name__ == '__main__':
    main()
