# Console Chat Application

## Overview
This is a simple console-based chat application implemented in Python. It includes both server and client components.

## Features
- User registration with nicknames.
- Send and receive messages.
- Server logs actions using syslog.
- Server configuration via a config file.

## Requirements
- Python 3.10+
- Ubuntu 20.04

## Setup

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
