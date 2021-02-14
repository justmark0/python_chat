import socket
import time
from .config import *
import json


def send(addr, mess: str):
    try_times = 5
    for i in range(try_times):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            ip, port = addr
            sock.connect((ip, PORT))
            sock.sendall(mess.encode('utf-8'))
            sock.close()
            time.sleep(0.05)
            return
        except ConnectionRefusedError:
            if i == try_times - 1:
                print("Couldn't connect to host :(")
                return
            time.sleep(0.1)
            continue
