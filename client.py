import socket
import threading
import json
from datetime import datetime

ip_server = "127.0.0.1"

def create_message_string(from_user_id, to_user_id, message_type, timestamp, message_text):
    return json.dumps({"from": from_user_id, "to": to_user_id, "type": message_type, "time": timestamp, "text": message_text})


def unpack_message_string(text):
    return json.loads(text)


def recieve_messages(client_socket, user_id):
    while True:
        data = unpack_message_string(client_socket.recv(1024).decode())
        print(data, user_id, type(data['to']), type(user_id))
        if data['to'] != user_id:
            continue
        if data['type'] == "user_message":
            print(f"Message from {data['from']}: {data['text']}")
        elif data['type'] == "system_message":
            print(f"NEW SYSTEM MESSAGE (TIME: {data['time']}): {data['text']}")


def send_messages(client_socket, user_id):
    while True:
        message_id_string = input("Id_to: ")
        if not message_id_string.isdigit():
            continue
        message_id = message_id_string
        message_time = int(datetime.now().timestamp())
        client_socket.sendall(create_message_string(user_id, message_id, "user_message", message_time, message_text).encode())


def start_client():
    print("Attempting to connect")
    client_socket = socket.socket()
    client_socket.connect((ip_server, 12345))

    print("Connected")
    id_data = unpack_message_string(client_socket.recv(1024).decode())
    while id_data["type"] != "new_id":
        print("HuH")
        id_data = unpack_message_string(client_socket.recv(1024).decode())
    user_id = id_data["to"]

    print(f"Id_given: {user_id}")
    reciever = threading.Thread(target=recieve_messages, args=(client_socket, user_id))
    sender = threading.Thread(target=send_messages, args=(client_socket, user_id))
    reciever.start()
    sender.start()


start_client()