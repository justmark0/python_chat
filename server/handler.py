from data.message_encryption import *
from data.models import *
import random
import rsa


def verify_fields(fields: list, data: dict, addr):  # returns true if everything okay
    for field in fields:
        if field not in data.keys():
            send_error(addr, f'Error: fields: {fields} is obligatory')
            return False
    return True


def get_content_of_smes(data: dict):
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
        return 'err'
    mem = Member.get_or_none(ip=str(ip), port=str(port), name=data['name'])
    if mem is None:
        send_error(addr, f"Error: {data['name']} is not member of {data['chat_id']}")
        return 'err'
    Message(chat=chat, member=mem, content=mess).save()
    return 'ok'


def is_member(addr, data):
    print(addr)
    print(data)
    ip, port = addr
    chat = Chat.get_or_none(chat_id=data['chat_id'])
    if chat is None:
        return False
    a = Member.get_or_none(ip=ip, name=data['name'], chat_id=chat)
    if a is None:
        return False
    return True


def check_chat_id_IETS(chat_id):  # Check chat_id if exists then suggest (new one)
    suggest_new_name = False
    new_chat_id = chat_id
    while True:  # If Chat id is already exist
        if Chat.get_or_none(chat_id=new_chat_id) is not None:
            new_chat_id = hex(random.randint(1, 10 ** 10))
            suggest_new_name = True
        else:
            break
    if suggest_new_name is True:
        send_new_name_suggestion(chat_id, new_chat_id)
    if chat_id != new_chat_id:
        return new_chat_id
    return None


async def handle_requests(message, addr):
    print(f"DEBUG: {message}")
    try:
        data = json.loads(message)
        mess, is_verified = get_content_of_smes(data)
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
        if not verify_fields(['name', 'chat_id', 'data', 'sign'], data, addr):
            return
        mess, is_verified = get_content_of_smes(data)
        if not is_member(addr, data):
            print(f"Error. You received message from {data['name']} who is not member of chat_id {data['chat_id']} ")
            return
        if is_verified:
            if add_message_to_db(data, mess, addr) == 'err':
                return
            chat = Chat.get(chat_id=data['chat_id'])
            print(f"[encrypted] You received message in chat {chat.name} from {data['name']}. Content is: {mess}")
        else:
            print(f"[date] Error: received message with wrong sign. from: {addr}; name:{data['name']}")  # TODO logging

    elif data['type'] == 'error':
        if 'data' in data.keys():
            print(data['data'])

    elif data['type'] == 'sjoin':
        if not verify_fields(['name', 'chat_id', 'data', 'sign'], data, addr):
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

    elif data['type'] == 'join_acc':
        if not verify_fields(['name', 'chat_id', 'data', 'sign', 'chat_name', 'chat_id_changeable'], data, addr):
            return
        mess, is_verified = get_content_of_smes(data)
        if is_verified:
            if data['chat_id_changeable'] == 'True':
                new_chat_id = check_chat_id_IETS(data['chat_id'])
                if new_chat_id is not None:
                    data['chat_id'] = new_chat_id
            else:
                chat_local = Chat.get_or_none(data['chat_id'])
                if chat_local is not None:
                    print(f'Error. You cannot join new chat since you have such chat id. You can delete chat '
                          f'{chat_local.name} and try to join again')
                    return

            chat_name = data['chat_name']  # If client has such chat name
            while True:
                if Chat.get_or_none(name=chat_name) is not None:
                    chat_name = chat_name + str(hex(random.randint(1, 10 ** 7)))
                else:
                    break

            mem_list = json.loads(mess)
            chat = Chat.create(chat_id=data['chat_id'], chat_name=data['chat_name'])
            for member in mem_list:
                if member['ip'] == '0.0.0.0':
                    ip, port = addr
                    member['ip'] = ip
                    member['port'] = port
                Member(name=member['name'], ip=member['ip'], port=member['port'], chat_id=chat,
                       is_admin=member['is_admin'], approved=True).save()

    elif data['type'] == 'new_chat_id':
        if not verify_fields(['old', 'new'], data, addr):
            return
        chat = Chat.get_or_none(chat_id=data['old'])
        if chat is None:
            send_error(addr, "Error. new_chat_id request. I am not member of chat")
            return
        if chat.chat_id_changeable is False:
            send_error(addr, "Error. Chat_id is not changeable")
        chat_id = data['new']
        nchat = check_chat_id_IETS(chat_id)
        if nchat == data['new']:
            chat.chat_id = data['new']  # User accepted new chat id
        else:
            chat.chat_id = nchat  # User had collision and made new chat id

    elif data['type'] == 'add_admin':
        print(data)
        if not verify_fields(['data', 'chat_id', 'sign', 'name'], data, addr):
            return
        if not is_member(addr, data):
            print(f"Error. You received message from {data['name']} who is not member of chat_id {data['chat_id']} ")
            return
        chat = Chat.get_or_none(chat_id=data['old'])
        if chat is None:
            send_error(addr, "Error. new_chat_id request. I am not member of chat")
            return
        mes = json.loads(mess)
        mem = Member.get_or_none(ip=mes['ip'], port=mes['port'], name=mes['name'])
        if mem is None:
            send_error(addr, f"Error. requested member not is not member of this chat")
            return
        mem.is_admin = True
        mem.save()

# TODO if rsa key changed request new one
