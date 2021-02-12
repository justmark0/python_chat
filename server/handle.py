from data.message_encryption import *
from data.models import *
import random
import rsa


def true_if_fields_not_in_data(fields: list, data: dict, addr):
    for field in fields:
        if field not in data.keys():
            send_error(addr, f'Error: fields: {fields} is obligatory')
            return True
    return False


def get_content_of_smes(data):
    '''
    :param data: dict
    :return: message:str, is_verified: bool
    '''
    mess = ""
    my = get_rsa_priv_from_str(get_my_rsa().priv_key)
    my_pub = get_rsa_pub_from_str(get_my_rsa().pub_key)
    for ms in data['data']:
        mess += rsa.decrypt(bytes.fromhex(ms), my).decode('utf-8')
    return mess, rsa.verify(mess.encode('utf-8'), bytes.fromhex(data['sign']), my_pub)


def add_message_to_db(data, mess, addr):
    ip, port = addr
    chat = Chat.get_or_none(chat_id=data['chat_id'])
    if chat is None:
        send_error(addr, f"Error: couldn't find this chat. Chat_id {data['chat_id']}. "
                         f"You can send me invitation")
        return
    mem = Member.get_or_none(ip=str(ip), port=str(port), name=data['name'])
    if mem is None:
        send_error(addr, f"Error: {data['name']} is not member of {data['chat_id']}")
        return
    Message(chat=chat, member=mem, content=mess).save()


def is_member(addr, data):
    ip, port = addr
    a = Member.get_or_none(ip=ip, port=port, name=data['name'])
    if a is None:
        return False
    if a.chat.chat_id == data['chat_id']:
        return True
    return False


async def handle_requests(message, addr):
    try:
        data = json.loads(message)
    except json.decoder.JSONDecodeError:
        send(addr, "Error: could't parse json")
        print(f"[date] Error: could't parse json from {addr}. ")  # TODO logging
        return
    if data["type"] == 'mes':
        print(f"You received message in chat {data['chat_id']} from {data['name']}. Content is: {data['data']}")

    elif data["type"] == 'get_pub_key':
        mes = {"type": "pub_key", "data": str(get_my_rsa().pub_key)}
        send(addr, json.dumps(mes))

    elif data["type"] == 'pub_key':
        mes: dict = json.loads(message)
        if 'data' not in mes.keys():
            return
        ip, port = addr
        Key(ip=ip, port=port, pub_key=mes["data"]).save()

    elif data['type'] == 'smes':
        if true_if_fields_not_in_data(['name', 'chat_id', 'data', 'sign'], data, addr):
            return
        mess, is_verified = get_content_of_smes(data)
        if is_verified and is_member(addr, data):
            add_message_to_db(data, mess, addr)
            print(f"[encrypted] You received message in chat {data['chat_id']} from {data['name']}. Content is: {mess}")
        else:
            print(f"[date] Error: received message with wrong sign. from: {addr}; name:{data['name']}")  # TODO logging

    elif data['error']:
        if 'data' in data.keys():
            print(data['data'])

    elif data['sjoin']:
        if true_if_fields_not_in_data(['name', 'chat_id', 'data', 'sign'], data, addr):
            return
        mess, is_verified = get_content_of_smes(data)
        if is_verified:
            ip, port = addr
            chat = Chat.get_or_none(chat_id=data['chat_id'])
            if chat is None:
                send_error(addr, f"Error: couldn't find this chat. Chat_id {data['chat_id']}. "
                                 f"You can send me invitation")
                return
            if Member.get_or_none(ip=ip, port=port, name=data['name'], chat_id=chat) is not None:
                return
            mem = Member.create(ip=ip, port=port, name=data['name'], chat_id=chat)
            print(f'{data["name"]} {addr} wants to join in chat {chat.name}. Type "#acc {data["name"]} {chat.chat_id} '
                  f'{ip} {port}" to accept join request')

    elif data['join_acc']:
        if true_if_fields_not_in_data(['name', 'chat_id', 'data', 'sign', 'chat_name'], data, addr):
            return
        mess, is_verified = get_content_of_smes(data)
        if is_verified:
            chat = Chat.get_or_none(chat_id=data['chat_id'])
            chat_id = data['chat_id']
            suggest_new_name = False
            if chat is not None:
                chat_id = hex(random.randint(1, 10 ** 10))
                suggest_new_name = True
            mem_list = data['data']
            chat = Chat.create(chat_id=chat_id, chat_name=data['chat_name'])
            for member in mem_list:
                Member(name=member['name'], ip=member['ip'], port=member['port'], chat_id=chat,
                       is_admin=member['is_admin'], approved=True).save()
            if suggest_new_name is True:
                pass  # TODO suggest new name

# TODO send message to all members
