from .config import *
from .models import Key, Chat
import socket
import json
import time
import rsa
'''addr is a tuple with format: (*ip*, *port*)'''


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


def get_rsa_pub_from_str(pub):
    n = int(pub.split(",")[0].split("(")[1])
    e = int(pub.split()[1][:-1:])
    return rsa.PublicKey(n, e)


def get_rsa_priv_from_str(pub):
    n = int(pub.split(",")[0].split("(")[1])
    e = int(pub.split()[1][:-1:])
    d = int(pub.split()[2][:-1:])
    p = int(pub.split()[3][:-1:])
    q = int(pub.split()[4][:-1:])
    return rsa.PrivateKey(n, e, d, p, q)


def send(addr, mess: str):
    try_times = 3
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
            time.sleep(0.1)
            continue


def ssend_done_message(chat: Chat, mes: str):
    addr = (chat.ip, chat.port)
    send(addr, mes)


def divide_str_by_len(mes, length):
    if len(mes) > length:
        chunks = []
        while mes != "":
            a = mes[:length:]
            chunks.append(a)
            mes = mes[length::]
        return chunks
    return [mes]


def make_json_ssend(chat: Chat, mes: str):
    host_key = get_rsa_key((chat.ip, chat.port))
    host_key_pub = get_rsa_pub_from_str(host_key.pub_key)
    message = {"type": "smes", "name": chat.my_name or my_default_name, "chat_id": chat.chat_id}
    chunks = divide_str_by_len(mes, rsa_max_length[str(RSA_KEY_LENGTH)])
    data_lst = []
    for i in range(len(chunks)):
        data_lst.append((rsa.encrypt(chunks[i].encode('utf-8'), host_key_pub)).hex())
    message['data'] = data_lst
    return json.dumps(message)


def ssend(chat: Chat, mes: str):  # Secure send. In other words message with encryption
    messages = divide_str_by_len(mes, max_symbols_in_message)
    print(messages)
    for dmes in messages:
        print(make_json_ssend(chat, dmes))
        ssend_done_message(chat, make_json_ssend(chat, dmes))


def send_mes(chat: Chat, mes: str):  # Not encrypted message
    addr = (chat.ip, chat.port)
    message = {"type": "mes", "name": chat.my_name or my_default_name, "chat_id": chat.chat_id, "data": mes}
    send(addr, json.dumps(message))

