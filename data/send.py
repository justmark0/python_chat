from .config import RSA_KEY_LENGTH, my_default_name, PORT
from .models import Key, Chat
import socket
import json
import time
import rsa
'''addr is a tuple with format: (*ip*, *port*)'''


def send(addr, mess: str):
    try_times = 4
    for i in range(try_times):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            ip, port = addr
            sock.connect((ip, int(port)))
            sock.sendall(mess.encode('utf-8'))
            sock.close()
            return
        except ConnectionRefusedError:
            if i == try_times - 1:
                print("Couldn't connect to host :(")
                return
            time.sleep(0.05)
            continue


def ssend(chat: Chat, mes: str):  # Secure send. In other words message with encryption
    addr = (chat.ip, chat.port)
    host_key = get_rsa_key(addr)
    n = int(host_key.pub_key.split(",")[0].split("(")[1])
    e = int(host_key.pub_key.split()[1][:-1:])
    message = {"type": "smes", "name": chat.my_name or my_default_name, "chat_id": chat.chat_id,
               "data": (rsa.encrypt(mes.encode('utf-8'), rsa.PublicKey(n, e))).hex()}
    print(message)
    # message = {"type": "smes", "name": chat.my_name or my_default_name, "chat_id": chat.chat_id,
    #            "data": rsa.encrypt(mes.encode('utf-8'), rsa.PublicKey(n, e))}
    # print(f'enc message:{message}')
    send(addr, json.dumps(message))


def send_mes(chat: Chat, mes: str):  # Not encrypted message
    addr = (chat.ip, chat.port)
    message = {"type": "mes", "name": chat.my_name or my_default_name, "chat_id": chat.chat_id, "data": mes}
    send(addr, json.dumps(message))


def get_my_rsa():
    if Key.get_or_none(ip='0.0.0.0') is None:
        my_pub, my_priv = rsa.newkeys(RSA_KEY_LENGTH)
        my = Key.create(ip='0.0.0.0', port=PORT, pub_key=my_pub, priv_key=my_priv)
        return my
    else:
        return Key.get(ip='0.0.0.0')


def get_rsa_key(addr):
    ip, port = addr
    db_key = Key.get_or_none(ip=ip, port=port)
    if db_key is not None:
        return db_key
    for a in range(3):
        send(addr, '{"type": "get_pub_key"}')
        for i in range(4):
            time.sleep(0.05)
            db_key = Key.get_or_none(ip=ip, port=port)
            if db_key is not None:
                return db_key
    raise Exception("Couldn't get rsa pub_key. Probably served isn't responding")
