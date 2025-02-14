# Приложение консольного чата

## Обзор
Это простая реализация чат-сервера и клиента с использованием Python. Сервер обрабатывает несколько клиентов, ведет логи и управление пользователями (регистрация, смена псевдонимов и т. д.). Клиенты могут общаться друг с другом, указав никнейм получателя.

## Features
- Регистрация пользователей по никам.
- Отправлять и получать сообщения.
- Сервер регистрирует действия с помощью системного журнала.
- Конфигурация сервера через файл конфигурации.

## Предварительные условия
Python 3.x установлен в вашей системе.

## Файлы
- server.py: реализация сервера чата.
- client.py: реализация клиента чата.
- config.json: файл конфигурации сервера.
- client.sh: скрипт для запуска клиента

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
- host: IP-адрес, к которому будет привязан сервер
- port: номер порта, который будет прослушивать сервер
- max_users: Максимальное количество одновременных пользователей
- log_level: уровень ведения журнала (например, 6 для INFO)

## Настройка и развертывание

### Сервер
1. Клонируйте репозиторий или загрузите файлы на свой локальный компьютер
2. Перейдите в каталог, в котором находятся файлы
3. Запустите сервер через терминал командой
    ```sh
    sh server.sh
    ```

### Клиент
1. Убедитесь, что сервер запущен
2. Перейдите в каталог, в котором находятся файлы
3. Запустите клиент через терминал командой
    ```sh
    sh client.sh
    ```
## Применение
### Сервер
- Когда сервер запускается, он будет прослушивать клиентские соединения
- Журналы будут записываться в syslog

### Клиент
1. Подключение
   - Когда клиент подключится к серверу, ему будет предложено ввести никнейм
   - Пример: `Enter your nickname: Алексей`
2. Ввод занятого имени
   - При введении занятого имени клиенту присылается сообщение 'Nickname {nickname} is already taken' после чего клиент, должен зарегистрироваться под другим именем
   - Пример: `/register Макс`
3. Смена ника
   - Используйте команду `/nick <никнейм>`
   - Пример `/nick Андрей`
4. Отправка сообщения
   - Для отправки сообщения используйте следующий формат: `<никнейм> <сообщение>`
   - После отправки другому клиенту появляется сообщение `Message sent successfully`
   - Пример: `Андрей Привет, как дела?`
5. Приём сообщения
   - Сообщение будет отражаться у клиента в формате:  `<никнейм>: <сообщение>`
   - Пример: `Макс: Привет, как дела?`
6. Удаление пользователя
   - Для удаление данных клиента на сервере необходимо ввести команду `/remove`

## Пример работы
1. Запуск сервера:
   ```sh
    sh server.sh
   ```
2. Запуск клиентов
   ```sh
    sh client.sh
   ```
3. Общение клиентов:
   ```sh
   Enter your nickname: Алексей
   Макс Привет!
   Макс: И тебе привет
   /nick Леша
   Макс Теперь мой новый ник Леша.
   Макс: Буду знать
   ```
