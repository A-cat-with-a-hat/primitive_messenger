import socket
import threading
import json
from datetime import datetime

ip_server = "127.0.0.1"

def turn_into_json(message):
    message['timestamp'] = int(datetime.now().timestamp())
    message = json.dumps(message)
    return message

def turn_into_message(message):
    return (turn_into_json(message)).encode()

def create_message_string(from_user_id, to_user_id, message_type, timestamp, message_text):
    return json.dumps({"from": from_user_id, "to": to_user_id, "type": message_type, "time": timestamp, "text": message_text})


def unpack_message_string(text):
    return json.loads(text)


def recieve_messages(client_socket, user_id):
    while True:
        data = unpack_message_string(client_socket.recv(1024).decode())
        if data['to'] != user_id:
            continue
        if data['type'] == "user_message":
            print(f"Message from {data['from']}: {data['text']}")
        elif data['type'] == "system_message":
            print(f"System message: {data['text']}")


def send_messages(client_socket, user_id):
    while True:
        cur_message = {}
        cur_message['from'] = user_id
        cur_message['to'] = input("Id_to: ")
        cur_message['type'] = 'user_message'
        cur_message['text'] = input("Message_text: ")
        client_socket.sendall(turn_into_message(cur_message))


def start_client():
    print("Attempting to connect")
    client_socket = socket.socket()
    client_socket.connect((ip_server, 12345))

    print("Connected")
    id_data = unpack_message_string(client_socket.recv(1024).decode())
    while id_data["type"] == "authorisation":
        print(id_data['text'])
        if (id_data['is_correct']):
            break
        user_id = input('Введите ваш id:')
        user_password = input('Введите ваш пароль: ')
        cur_message = {}
        cur_message['text'] = [user_id, user_password]
        client_socket.sendall(turn_into_message(cur_message))
        id_data = unpack_message_string(client_socket.recv(1024).decode())
    user_id = id_data["to"]

    print(f"Ваш id: {user_id}")
    reciever = threading.Thread(target=recieve_messages, args=(client_socket, user_id))
    sender = threading.Thread(target=send_messages, args=(client_socket, user_id))
    reciever.start()
    sender.start()


start_client()