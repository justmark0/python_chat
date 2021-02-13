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


def send_new_name_suggestion(old_chat_id, new_chat_id):
    chat = Chat.get(chat_id=new_chat_id)
    members = Member.select().where(Member.chat == chat)
    message = {'type': 'new_chat_id', 'old': old_chat_id, 'new': new_chat_id}
    for mem in members:
        send((mem.ip, mem.port), json.dumps(message))
