import socket
import json

HOST = "localhost"
PORT = 4702


def send(addr, mess):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(addr)
    sock.sendall(mess.encode('utf-8'))
    sock.close()


def client_start():
    chats = {'chat 1': "randomsymbols1"}  # TODO move to db

    chat_info = {"randomsymbols1": [('localhost', 4702), "mark"]}  # TODO move to db

    # a = input('type which chat you want to enter by typing "chat *number*", or create new with "#new *ip* *port*"')
    # TODO add chat creation

    # a = 'chat 1'  # for testing

    if a in chats.keys():
        chat_id = chats[a]
        while True:
            a = input()
            if a == "exit()":
                break
            message = {"type": "mes", "name": chat_info[chat_id][1], "data": a}
            send(chat_info[chat_id][0], json.dumps(message))
