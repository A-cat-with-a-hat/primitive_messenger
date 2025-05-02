import socket
import threading
import json
from datetime import datetime

cur_id = 0

user_by_id = {}
prime_for_hash = 102409
mod_for_hash = 10 ** 9 + 7

def get_hash(s):
    cur_hash = 0
    for i in range(len(s)):
        cur_hash *= prime_for_hash
        cur_hash += ord(s[i])
        cur_hash %= mod_for_hash
    return cur_hash

class Database():
    def __init__(self):
        self.hash_password = {}
        self.stored_messages = {}
        self.conn_by_id = {}

    def send_stored_messages(self, user_id):
        for message in self.stored_messages[user_by_id]:
            self.conn_by_id[user_by_id].sendall(message.encode())

database = Database()

def decode_message(message):
    if type(message) == bytes:
        message = message.decode()
    return message

def get_dict(message):
    return json.loads(message)

def turn_into_json(message):
    message['timestamp'] = int(datetime.now().timestamp())
    message = json.dumps(message)
    return message

# {"from": id1, "to": id2, "type": "text"/"invite"/..., "timestamp": ..., "text": ...}

def handler(conn, addr):
    global cur_id
    print(f"Connected with {addr}")
    data = '1'
    cur_id += 1
    cur_message = {}
    correct_authoriztion = False
    cur_message['from'] = 0
    cur_message['type'] = "authorisation"
    cur_message['text'] = "Введите свой id и пароль на через enter, если id ещё не существует, то создастся новый аккаунт с введёнными даннми"
    conn.sendall(turn_into_json(cur_message).encode())
    while not correct_authoriztion:
        data = decode_message(conn.recv(1024))
        data = get_dict(data)
        user_id, password = data['text']
        password = get_hash(password)
        if user_id not in database.hash_password.keys() or database.hash_password[user_id] == password:
            correct_authoriztion = True
            cur_message['to'] = user_id

            if user_id not in database.hash_password.keys():
                cur_message['text'] = "Новый аккаунт создан"
                conn.sendall(turn_into_json(cur_message).encode())
            else:
                cur_message['text'] = "Корректная авторизация"
                conn.sendall(turn_into_json(cur_message).encode())
        else:
            cur_message['text'] = 'Некорректный пароль'
            conn.sendall(turn_into_json(cur_message).encode())
    user_by_id[cur_user_id] = conn
    print(f"ID = {cur_user_id}")
    while data: # while data is being sent
        data = decode_message(conn.recv(1024)) # read sent data
        if not data:
            print("Connection closed")
            break
        else:
            print(f'Evaluating "{data}"...')
            data = get_dict(data)
            print(f'{data}')
            reciever_id = data['to']
            if False and reciever_id not in user_by_id:
                conn.sendall("User_does_not_exist".encode())
                continue
            if False and reciever_id == cur_user_id:
#                print("You_cant_send_mail_to_yourself")
                conn.sendall("You_cant_send_mail_to_yourself".encode())
                continue
            str_res = data
            data['type'] = 'user_message'
            str_res = turn_into_json(data)
            user_by_id[reciever_id].sendall(str_res.encode())

# ip_server = "192.168.236.1"
ip_server = "127.0.0.1"

server_socket = socket.socket() # init socket
server_socket.bind((ip_server, 12345)) # bind socket using set ip adress

server_socket.listen() # listen for socket connection

print("Server_is_up")

while True:
    conn, addr = server_socket.accept() # connect with client socket
    print("New_user")
    client_handler = threading.Thread(target=handler, args=(conn, addr))
    client_handler.start()