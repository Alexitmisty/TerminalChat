import socket
import select
import logging
import argparse
import json
import logging.handlers

class ChatServer:
    def __init__(self, host, port, max_users, log_level):
        # Инициализация переменных
        self.host = host
        self.port = port
        self.max_users = max_users
        self.clients = {}
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Настройка базового логирования
        logging.basicConfig(level=log_level, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

        # Настройка syslog
        syslog_handler = logging.handlers.SysLogHandler(address='/dev/log')  # Для отправки логов в syslog
        syslog_handler.setLevel(log_level)  # Установка уровня логирования для syslog
        syslog_formatter = logging.Formatter('%(name)s: %(levelname)s %(message)s')  # Форматирование сообщений
        syslog_handler.setFormatter(syslog_formatter)  # Применение формата к обработчику
        self.logger.addHandler(syslog_handler)  # Добавление обработчика к логгеру

    def start_server(self):
        self.server_socket.bind((self.host, self.port))  # Привязка сервера к хосту и порту
        self.server_socket.listen(self.max_users)  # Установка максимального количества подключений
        self.logger.info(f'Server started on {self.host}:{self.port}')  # Логирование старта сервера
        
        inputs = [self.server_socket]  # Список сокетов для чтения
        outputs = []  # Список сокетов для записи

        while True:
            readable, writable, exceptional = select.select(inputs, outputs, inputs)  # Ожидание активности сокетов
            
            for s in readable:
                if s is self.server_socket:  # Новое подключение
                    client_socket, client_address = s.accept()  # Принятие нового подключения
                    self.logger.info(f'New connection from {client_address}')  # Логирование нового подключения
                    inputs.append(client_socket)  # Добавление нового клиента в список сокетов
                    self.clients[client_socket] = {"address": client_address, "nickname": None}  # Сохранение информации о клиенте
                else:
                    try:
                        data = s.recv(1024)  # Получение данных от клиента
                        if data:
                            self.handle_message(s, data.decode().strip())  # Обработка сообщения от клиента
                        else:
                            self.logger.info(f'Connection closed by {self.clients[s]["address"]}')  # Логирование закрытия подключения
                            inputs.remove(s)  # Удаление сокета из списка
                            del self.clients[s]  # Удаление клиента из списка
                            s.close()  # Закрытие сокета
                    except ConnectionResetError:
                        self.logger.info(f'Connection reset by {self.clients[s]["address"]}')  # Логирование сброса подключения
                        inputs.remove(s)  # Удаление сокета из списка
                        del self.clients[s]  # Удаление клиента из списка
                        s.close()  # Закрытие сокета
                    except Exception as e:
                        self.logger.error(f'Error handling message from {self.clients[s]["address"]}: {e}')  # Логирование ошибки
                        inputs.remove(s)  # Удаление сокета из списка
                        del self.clients[s]  # Удаление клиента из списка
                        s.close()  # Закрытие сокета

    def handle_message(self, client_socket, message):
        if message.startswith('/'):  # Проверка, является ли сообщение командой
            self.handle_command(client_socket, message)  # Обработка команды
        else:
            self.handle_chat_message(client_socket, message)  # Обработка сообщения

    def handle_command(self, client_socket, message):
        parts = message.split(' ', 1)  # Разделение команды и аргументов
        command = parts[0]  # Команда
        
        if command == '/register':
            if len(parts) < 2:
                client_socket.sendall("Usage: /register <nickname>".encode())  # Отправка инструкции по использованию команды
            else:
                self.register_nickname(client_socket, parts[1])  # Регистрация никнейма
        elif command == '/nick':
            if len(parts) < 2:
                client_socket.sendall("Usage: /nick <new_nickname>".encode())  # Отправка инструкции по использованию команды
            else:
                self.change_nickname(client_socket, parts[1])  # Смена никнейма
        elif command == '/exit':
            # Игнорируем команду /exit от клиента
            pass
        else:
            client_socket.sendall(f"Unknown command: {command}".encode())  # Отправка сообщения о неизвестной команде

    def register_nickname(self, client_socket, nickname):
        if self.clients[client_socket]["nickname"] is None:  # Проверка, зарегистрирован ли клиент
            for client, info in self.clients.items():
                if info["nickname"] == nickname:
                    client_socket.sendall(f"Nickname {nickname} is already taken".encode())  # Отправка сообщения о занятом никнейме
                    return
            self.clients[client_socket]["nickname"] = nickname  # Регистрация никнейма
            client_socket.sendall(f"Nickname set to {nickname}".encode())  # Отправка подтверждения регистрации
        else:
            client_socket.sendall("You are already registered".encode())  # Отправка сообщения о повторной регистрации

    def change_nickname(self, client_socket, new_nickname):
        old_nickname = self.clients[client_socket]["nickname"]
        if old_nickname is None:
            client_socket.sendall("You are not registered. Use /register <nickname>".encode())  # Отправка инструкции по регистрации
            return

        for client, info in self.clients.items():
            if info["nickname"] == new_nickname:
                client_socket.sendall(f"Nickname {new_nickname} is already taken".encode())  # Отправка сообщения о занятом никнейме
                return

        self.clients[client_socket]["nickname"] = new_nickname  # Смена никнейма
        client_socket.sendall(f"Nickname changed from {old_nickname} to {new_nickname}".encode())  # Подтверждение смены никнейма

    def handle_chat_message(self, client_socket, message):
        if self.clients[client_socket]["nickname"] is None:  # Проверка, зарегистрирован ли клиент
            client_socket.sendall("You must register with /register <nickname> before sending messages".encode())  # Отправка инструкции по регистрации
            return

        parts = message.split(' ', 1)  # Разделение сообщения на никнейм и сообщение
        if len(parts) < 2:
            client_socket.sendall("Invalid message format. Use '<nickname> <message>'".encode())  # Отправка инструкции по формату сообщения
            return

        recipient_nickname, actual_message = parts
        sender_nickname = self.clients[client_socket]["nickname"]

        recipient_socket = None
        for client, info in self.clients.items():
            if info["nickname"] == recipient_nickname:
                recipient_socket = client  # Поиск сокета получателя
                break

        if recipient_socket:
            try:
                recipient_socket.sendall(f'{sender_nickname}: {actual_message}'.encode())  # Отправка сообщения получателю
                client_socket.sendall("Message sent successfully".encode())  # Подтверждение отправки сообщения
            except Exception as e:
                self.logger.error(f"Failed to send message: {e}")  # Логирование ошибки отправки
                client_socket.sendall("Failed to send message".encode())  # Уведомление об ошибке отправки
        else:
            client_socket.sendall(f'User {recipient_nickname} not found'.encode())  # Уведомление о ненайденном пользователе

def main():
    parser = argparse.ArgumentParser(description="Start the chat server.")  # Парсер аргументов командной строки
    parser.add_argument('--config', required=True, help='Path to the config file')  # Добавление аргумента для пути к конфигурационному файлу
    args = parser.parse_args()  # Разбор аргументов

    with open(args.config, 'r') as f:
        config = json.load(f)  # Чтение конфигурационного файла

    server = ChatServer(
        host=config['host'], 
        port=config['port'], 
        max_users=config['max_users'], 
        log_level=config['log_level']
    )  # Создание экземпляра сервера с параметрами из конфигурационного файла
    server.start_server()  # Запуск сервера

if __name__ == '__main__':
    main()  # Запуск главной функции
