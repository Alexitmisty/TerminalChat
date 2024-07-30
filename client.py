import socket  # Импорт модуля для работы с сетевыми сокетами
import threading  # Импорт модуля для работы с потоками

class ChatClient:
    def __init__(self, host, port):
        self.host = host  # Адрес хоста сервера
        self.port = port  # Порт сервера
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Создание клиентского сокета
        self.nickname = input("Enter your nickname: ")  # Запрос у пользователя никнейм

    def start_client(self):
        self.client_socket.connect((self.host, self.port))  # Подключение к серверу
        self.client_socket.sendall(f"/register {self.nickname}".encode())  # Отправление команды регистрации с никнеймом
        
        threading.Thread(target=self.receive_messages).start()  # Запуск потока для получения сообщений от сервера

        while True:
            message = input()  # Ожидание ввода сообщения от пользователя
            self.client_socket.sendall(message.encode())  # Отправление сообщение на сервер

    def receive_messages(self):
        while True:
            message = self.client_socket.recv(1024).decode()  # Получение сообщения от сервера
            if message:
                print(message)  # Если сообщение получено, вывод его на экран
            else:
                break  # Если сообщение пустое, выход из цикла (соединение закрыто)

if __name__ == '__main__':
    client = ChatClient(host='127.0.0.1', port=12345)  # Создание экземпляра клиента с заданным хостом и портом
    client.start_client()  # Запуск клиента
