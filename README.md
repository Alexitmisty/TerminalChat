# Приложение консольного чата

## Обзор
Это простая реализация чат-сервера и клиента с использованием Python. Сервер обрабатывает несколько клиентов, ведет логи и управление пользователями (регистрация, смена псевдонимов и т. д.). Клиенты могут общаться друг с другом, указав никнейм получателя.

## Features
- User registration with nicknames.
- Send and receive messages.
- Server logs actions using syslog.
- Server configuration via a config file.

## Предварительные условия
Python 3.x установлен в вашей системе.

## Файлы
server.py: реализация сервера чата.
client.py: реализация клиента чата.
config.json: файл конфигурации сервера.
client.sh: скрипт для запуска клиента.

## Конфигурация
Файл config.json содержит конфигурацию сервера:
```json
{
    "host": "127.0.0.1",
    "port": 12345,
    "max_users": 10,
    "log_level": 6
}
```

### Server
1. Install dependencies:
    ```sh
    sudo apt-get install python3.10
    ```
2. Create a `config.json` file with the following content:
    ```json
    {
        "host": "127.0.0.1",
        "port": 12345,
        "max_users": 10,
        "log_level": 6
    }
    ```
3. Run the server:
    ```sh
    python3 server.py --config config.json
    ```

### Client
1. Run the client:
    ```sh
    python3 client.py
    ```

## Usage
1. Start the server as described above.
2. Start multiple client instances to simulate multiple users.
3. Follow the prompts to register with a nickname and send messages.

## Note
- This is a basic implementation for educational purposes. Production code should include more robust error handling and security features.
