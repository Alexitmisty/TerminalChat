import socket  # Импортируем модуль для работы с сетевыми сокетами
import select  # Импортируем модуль для мультиплексирования ввода-вывода
import logging  # Импортируем модуль для логирования
import argparse  # Импортируем модуль для обработки аргументов командной строки
import json  # Импортируем модуль для работы с JSON
import sys  # Импортируем модуль для доступа к системным параметрам и функциям
import logging.handlers  # Импортируем модуль для работы с обработчиками логирования

class ChatServer:
    def __init__(self, host, port, max_users, log_level):
        self.host = host  # Адрес хоста
        self.port = port  # Порт для соединения
        self.max_users = max_users  # Максимальное количество пользователей
        self.clients = {}  # Словарь для хранения подключенных клиентов
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Создание сокета сервера
        
        # Настройка логирования в syslog
        handler = logging.handlers.SysLogHandler(address='/dev/log')  # Создание обработчика для syslog
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')  # Задание формата логов
        handler.setFormatter(formatter)  # Применение формата к обработчику
        self.logger = logging.getLogger(__name__)  # Создание логгера
        self.logger.addHandler(handler)  # Добавление обработчика к логгеру
        self.logger.setLevel(log_level)  # Установка уровня логирования

    def start_server(self):
        self.server_socket.bind((self.host, self.port))  # Привязка сокета к хосту и порту
        self.server_socket.listen(self.max_users)  # Настройка сокета на прослушивание
        self.logger.info(f'Server started on {self.host}:{self.port}')  # Лог информации о старте сервера
        
        inputs = [self.server_socket]  # Список сокетов для чтения
        outputs = []  # Список сокетов для записи

        while True:
            # Основной цикл сервера для обработки соединений и сообщений
            readable, writable, exceptional = select.select(inputs, outputs, inputs)  # Ожидание события на сокетах
            
            for s in readable:  # Обработка сокетов, готовых для чтения
                if s is self.server_socket:  # Если это серверный сокет, значит новое входящее соединение
                    client_socket, client_address = s.accept()  #  Принятие оединение
                    self.logger.info(f'New connection from {client_address}')  # Лог нового соединения
                    inputs.append(client_socket)  # Добавление клиентского сокета в список для чтения
                    self.clients[client_socket] = {"address": client_address, "nickname": None}  # Сохранение информации о клиенте
                else:
                    try:
                        data = s.recv(1024)  # Получение данных от клиента
                        if data:  # Если данные получены
                            self.handle_message(s, data.decode().strip(), inputs)  # Обработка сообщения
                        else:  # Если данные не получены, клиент закрыл соединение
                            self.logger.info(f'Connection closed by {self.clients[s]["address"]}')  # Лог закрытия соединения
                            inputs.remove(s)  # Удаление сокета из списка для чтения
                            del self.clients[s]  # Удаление информации о клиенте
                            s.close()  # Закрытие сокета
                    except ConnectionResetError:  # Обработка принудительного разрыва соединения
                        self.logger.info(f'Connection reset by {self.clients[s]["address"]}')  # Лог разрыва соединения
                        inputs.remove(s)  #  Удаление сокета из списка для чтения
                        del self.clients[s]  # Удаление информации о клиенте
                        s.close()  # Закрытие сокета
                    except Exception as e:  # Обработка других исключений
                        self.logger.error(f'Error handling message from {self.clients[s]["address"]}: {e}')  # Логируем ошибку
                        inputs.remove(s)  # Закрытие сокета из списка для чтения
                        del self.clients[s]  # Удаление информации о клиенте
                        s.close()  # Закрытие сокета

    def handle_message(self, client_socket, message, inputs):
        # Обработка входящего сообщения
        if message.startswith('/'):  # Если сообщение является командой
            self.handle_command(client_socket, message, inputs)  # Обработка команды
        else:  # Если сообщение является чатом
            self.handle_chat_message(client_socket, message)  # Обрабобтка чат-сообщения

    def handle_command(self, client_socket, message, inputs):
        # ОБработка команды от клиента
        parts = message.split(' ', 1)  # Разделяение команды и аргумента
        command = parts[0]  # Получение команды
        
        if command == '/register':  # Если команда для регистрации
            if len(parts) < 2:  # Если аргумент отсутствует
                client_socket.sendall("Usage: /register <nickname>".encode())  # Отправление сообщения о неправильном использовании команды
            else:  # Если аргумент присутствует
                self.register_nickname(client_socket, parts[1])  # Регистрация никнейма
        elif command == '/nick':  # Если команда для смены никнейма
            if len(parts) < 2:  # Если аргумент отсутствует
                client_socket.sendall("Usage: /nick <new_nickname>".encode())  # Отправление сообщения о неправильном использовании команды
            else:  # Если аргумент присутствует
                self.change_nickname(client_socket, parts[1])  # Смена никнейма
        elif command == '/remove':  # Если команда для удаления себя
            self.remove_self(client_socket, inputs)  # Удаление клиента
        else:  # Если команда неизвестна
            client_socket.sendall(f"Unknown command: {command}".encode())  # Отправление сообщения о неизвестной команде

    def register_nickname(self, client_socket, nickname):
        # Регистрация никнейма клиента
        if self.clients[client_socket]["nickname"] is None:  # Если никнейм еще не зарегистрирован
            for client, info in self.clients.items():  # Проверка, занят ли никнейм
                if info["nickname"] == nickname:
                    client_socket.sendall(f"Nickname {nickname} is already taken".encode())  # Отправление сообщения о занятом никнейме
                    return
            self.clients[client_socket]["nickname"] = nickname  # Установление никнейм
            client_socket.sendall(f"Nickname set to {nickname}".encode())  # Отправление сообщения об успешной регистрации
        else:
            client_socket.sendall("You are already registered".encode())  # Отправление сообщения о том, что клиент уже зарегистрирован

    def change_nickname(self, client_socket, new_nickname):
        # Смена никнейма клиента
        old_nickname = self.clients[client_socket]["nickname"]  # Получение старого никнейма
        if old_nickname is None:  # Если клиент не зарегистрирован
            client_socket.sendall("You are not registered. Use /register <nickname>".encode())  # Отправление сообщения о необходимости регистрации
            return

        for client, info in self.clients.items():  # Проверяем, занят ли новый никнейм
            if info["nickname"] == new_nickname:
                client_socket.sendall(f"Nickname {new_nickname} is already taken".encode())  # Отправление сообщения о занятом никнейме
                return

        self.clients[client_socket]["nickname"] = new_nickname  # Установление нового никнейма
        client_socket.sendall(f"Nickname changed from {old_nickname} to {new_nickname}".encode())  # Отправление сообщения об успешной смене никнейма

    def remove_self(self, client_socket, inputs):
        # Удаление клиента
        nickname = self.clients[client_socket]["nickname"]  # Получение никнейма клиента
        if nickname is None:  # Если клиент не зарегистрирован
            client_socket.sendall("You are not registered.".encode())  # Отправление сообщения о необходимости регистрации
        else:
            client_socket.sendall("You have been removed from the server.".encode())  # Отправление сообщения об удалении
            self.logger.info(f'User {nickname} removed themselves')  # Лог удаления клиента
            inputs.remove(client_socket)  # Удаление сокета из списка для чтения
            del self.clients[client_socket]  # Удаление информации о клиенте
            client_socket.close()  # Закрытие сокета

    def handle_chat_message(self, client_socket, message):
        # Обработка сообщения чата
        if self.clients[client_socket]["nickname"] is None:  # Если клиент не зарегистрирован
            client_socket.sendall("You must register with /register <nickname> before sending messages".encode())  # Отправление сообщения о необходимости регистрации
            return

        parts = message.split(' ', 1)  # Разделение сообщения на никнейм получателя и текст сообщения
        if len(parts) < 2:  # Если сообщение в неправильном формате
            client_socket.sendall("Invalid message format. Use '<nickname> <message>'".encode())  # Отправление сообщения о неправильном формате
            return

        recipient_nickname, actual_message = parts  # Получение никнейма получателя и текст сообщения
        sender_nickname = self.clients[client_socket]["nickname"]  # Получение никнейма отправителя

        recipient_socket = None  # Инициализация сокета получателя
        for client, info in self.clients.items():  # Поиск сокета получателя по никнейму
            if info["nickname"] == recipient_nickname:
                recipient_socket = client
                break

        if recipient_socket:  # Если получатель найден
            try:
                recipient_socket.sendall(f'{sender_nickname}: {actual_message}'.encode())  # Отправление сообщения получателю
                client_socket.sendall("Message sent successfully".encode())  # Отправление сообщения об успешной отправке
            except Exception as e:  # Обрабатка ошибки отправки
                self.logger.error(f"Failed to send message: {e}")  # Лог ошибки
                client_socket.sendall("Failed to send message".encode())  # Отправление сообщения о неудачной отправке
        else:  # Если получатель не найден
            client_socket.sendall(f'User {recipient_nickname} not found'.encode())  # Отправление сообщения о ненайденном получателе

def main():
    # Основная функция для запуска сервера
    parser = argparse.ArgumentParser(description="Start the chat server.")  # Создание парсера аргументов командной строки
    parser.add_argument('--config', required=True, help='Path to the config file')  # Добавление аргумента для пути к файлу конфигурации
    args = parser.parse_args()  # Парсим аргументы

    with open(args.config, 'r') as f:  # Открытие файла конфигурации
        config = json.load(f)  # Загрузка конфигурации из файла

    server = ChatServer(
        host=config['host'], 
        port=config['port'], 
        max_users=config['max_users'], 
        log_level=config['log_level']
    )  # Создание экземпляра сервера с параметрами из конфигурации
    server.start_server()  # Запуск сервера

if __name__ == '__main__':
    main()  # Запуск основной функции, если скрипт выполняется напрямую
