from data.message_encryption import *
import random
import re


def acc(a):
    if len(a.split()) != 5:
        print('Try again. Pattern is following: "#acc *name* *chat_id* *ip* *port*"')
        return
    ip = a.split()[3]
    if not re.fullmatch(r'^((25[0-5]|(2[0-4]|1[0-9]|[1-9]|)[0-9])(\.(?!$)|$)){4}$', ip):
        print("Wrong ip. Exapmles: 172.0.0.1 or 200.200.200.200")
        return
    port = a.split()[3]
    if port == 'y' or port == "":
        port = 4702
    if not re.fullmatch(r'[0-9]{1,5}', port):
        print("Wrong port. Exapmle: 4702")
        return
    chat = Chat.get_or_none(name=a.split()[1])
    if chat is None:
        print(f"No chat with chat_id {a.split()[2]}")
        return
    me = Member.get_or_none(chat_id=chat.chat_id, name=my_default_name, ip=HOST, port=PORT)
    if me is not None:
        if me.is_admin is False:
            print("I cannot accept users since I am not admin")
            return
    members = Member.select().where(Member.chat_id == a.split()[2])
    member_l = []
    for mem in members:
        if mem.approved is True:
            member_l.append({"ip": mem.ip, "port": mem.port, "name": mem.name, "is_admin": mem.is_admin})
    Smes(json.dumps(member_l), Chat(name=a.split()[1], chat_id=a.split()[2], ip=ip, port=port),
         type='join_acc').send_sjoin_acc_mes(chat_name=chat.name)
    new_mem = {"ip": ip, "port": port, "name": a.split()[1], "is_admin": False}
    Smes(json.dumps(new_mem), Chat(name='none', chat_id=a.split()[2], ip=ip, port=port),
         type='new_member').send_smes_to_all()


def chat_f(a):
    chat = Chat.get_or_none(name=a.split()[1])
    if chat is None:
        print("Couldn't find this chat")
        return
    print(f'You entered chat "{a}".')
    while True:
        a = input()
        if a == "exit()":
            break
        if a == "":
            continue
        if a.split(":")[0] == 'ne':  # Not encrypted message
            members = Member.select().where(Member.chat == chat)
            for mem in members:
                send_mes((str(mem.ip), str(mem.port)), a)
        Smes(a, chat).send_smes_to_all()


def new_f(a):
    name = input("Write name of the chat that you and members will see in the list of the chats\n")
    chat = Chat.get_or_none(name=name)
    if chat is not None:
        print('Pick another name. You have it already')
    if name == '#new' or name == '#join' or name == '#acc' or name == 'chat':
        print('Pick another name for chat')
        return

    chat_id = hex(random.randint(1, 10 ** 10))
    while True:  # If Chat id is already exist
        if Chat.get_or_none(chat_id=chat_id) is not None:
            chat_id = hex(random.randint(1, 10 ** 10))
        else:
            break

    chat_id_changeable = input("Will users be able to change user_id? y/n (default=n)\nThis means if users will get "
                               "collusion in chat_id they will notify all members that they are changing chat_id. On "
                               "other side some users can send too many of this notifications and flood, some users "
                               "even may lost last chat_id and could not connect to chat again\n")
    if chat_id_changeable == 'y' or chat_id_changeable == 'yes':
        chat_id_changeable = True
    elif chat_id_changeable == 'n' or chat_id_changeable == 'no' or chat_id_changeable == '':
        chat_id_changeable = False

    chat = Chat.create(name=name, chat_id=chat_id, ip=HOST, port=PORT, chat_id_changeable=chat_id_changeable)
    Member(chat=chat, ip=HOST, port=PORT, name=my_default_name, is_admin=True).save()
    print(f"You have created the chat. Other users can join by chat_id:{chat_id}")


def join_f(a):
    chat_id = input("Write chat_id\n")
    while True:
        ip = input("Write ip of server\n")
        if not re.fullmatch(r'^((25[0-5]|(2[0-4]|1[0-9]|[1-9]|)[0-9])(\.(?!$)|$)){4}$', ip):
            print("Wrong ip. Exapmles: 172.0.0.1 or 200.200.200.200")
            return
        port = input('Write port of server. (or "y" to use default)')
        if port == 'y' or port == "":
            port = 4702
        if not re.fullmatch(r'[0-9]{1,5}', port):
            print("Wrong port. Exapmle: 4702")
            return
        Smes(chat_id, Chat(name=my_default_name, chat_id=chat_id, ip=ip, port=port),
             type='sjoin').send_sdef_mes()


def add_admin_f():
    chat_name = input("Write chat name where to add admin\n")
    chat = Chat.get_or_none(name=chat_name)
    if chat is None:
        print('No chat with such name')
        return
    me = Member.get_or_none(chat=chat, ip=HOST)
    if me is None:
        print('You are not member of this chat')
        return
    members = Member.select().where(Member.chat == chat)
    print('List of available members to which you can assign admin role')
    list_of_members = []
    for mem in members:
        if mem.ip == HOST or mem.is_admin is True or mem.approved is False:
            continue
        list_of_members.append(mem)
        print(f'#{len(list_of_members)} {mem.name} {mem.ip} {mem.port}')
    num = input('Write number of user that you want to make admin. or "exit()" to cancel\n')
    if num == 'exit()':
        return
    if not num.isnumeric():
        print('You should write number')
        return
    if int(num) > 0 or int(num) <= len(list_of_members):
        memb = list_of_members[int(num) - 1]
        mes = {"ip": memb.ip, "port": memb.port, "name": memb.name}
        Smes(json.dumps(mes), Chat(name=chat.name, chat_id=chat.chat_id, ip=memb.ip, port=memb.port),
             type='add_admin').send_smes_to_all()


def client_start():
    Chat.get_or_create(name='1', chat_id='randomsymbols1', ip=HOST, port=PORT)  # for testing

    while True:
        print(
            'Main menu.\nWrite: "chat *name of chat*" to enter to the existing one. \n You can create new one by '
            'typing "#new". Or you can join by typing "#join"To exit from chat type: "exit()". To send message without '
            'encryption write with message: "ne:*message*"\nList of available chats:')
        chats = Chat.select()
        for c in chats:
            print(f"Name:{c.name}; ip:{c.ip}; port:{c.port}; chat_id:{c.chat_id};")

        a = input()
        if a == '':
            continue
        if a.split()[0] == "chat":
            chat_f(a)
        elif a.split()[0] == '#new':
            new_f(a)
            # TODO make invitations
        elif a.split()[0] == '#join':
            join_f(a)
        elif a.split()[0] == '#acc':
            acc(a)
        elif a.split()[0] == '#add_admin':
            add_admin_f()
        else:
            print("Couldn't understand your command")

# TODO ban *time*
# TODO get history
# TODO describe problem and solution for chat_is changes and history loses
