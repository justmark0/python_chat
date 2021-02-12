from .config import *
from .models import *
from data import *
'''addr is a tuple with format: (*ip*, *port*)'''


def send_error(addr, message):
    message = {"type": "error", "data": message}
    send(addr, json.dumps(message))


def send_mes(chat: Chat, mes: str):  # Not encrypted message
    message = {"type": "mes", "name": my_default_name, "chat_id": chat.chat_id, "data": mes}
    send((chat.ip, chat.port), json.dumps(message))


# def send_join_request(addr, name, chat_id):
#     message = {"type": }
