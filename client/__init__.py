from server.handler import add_message_to_db, is_blocked
from data.message_encryption import *
import logging
import random
import re


def acc(a):
    if len(a.split()) != 4:
        print('Try again. Pattern is following: "#acc *name* *chat_id* *ip*"')
        return
    ip = a.split()[3]
    if not re.fullmatch(r'^((25[0-5]|(2[0-4]|1[0-9]|[1-9]|)[0-9])(\.(?!$)|$)){4}$', ip):
        print("Wrong ip. Exapmles: 172.0.0.1 or 200.200.200.200")
        return
    chat = Chat.get_or_none(chat_id=a.split()[2])
    if chat is None:
        print(f"No chat with chat_id {a.split()[2]}")
        return
    me = Member.get_or_none(chat_id=chat.chat_id, name=my_default_name, ip=HOST, port=PORT)
    if me is not None:
        if me.is_admin is False:
            print("I cannot accept users since I am not admin")
            return
    members = Member.select().where(Member.chat_id == chat)
    member_l = []
    for mem in members:
        if mem.ip == a.split()[3]:
            continue
        if mem.approved is True:
            member_l.append({"ip": mem.ip, "port": mem.port, "name": mem.name, "is_admin": mem.is_admin})
    Smes(json.dumps(member_l), Chat(name=a.split()[1], chat_id=a.split()[2], ip=ip, port=PORT),
         type='join_acc').send_sjoin_acc_mes(chat_name=chat.name)
    new_mem = {"ip": ip, "port": PORT, "name": a.split()[1], "is_admin": False}
    new, _ = Member.get_or_create(chat=chat, ip=ip, name=a.split()[1])
    new.approved = True
    new.is_admin = False
    new.save()
    members = Member.select().where(Member.chat == Chat.get(chat_id=chat.chat_id))
    for mem in members:
        if mem.ip == '0.0.0.0' or mem.ip == ip:  # comment if want to DEBUG
            continue
        Smes(json.dumps(new_mem), Chat(name='none', chat_id=a.split()[2], ip=mem.ip, port=PORT),
             type='new_member').send_smes()


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
        if is_blocked(('0.0.0.0', PORT), {'chat_id': chat.chat_id, "name": my_default_name}) is True:
            print('I cannot send messages to this chat. You can see #my_blocks')
            return
        if a.split(":")[0] == 'ne':  # Not encrypted message
            members = Member.select().where(Member.chat == chat)
            for mem in members:
                send_mes((str(mem.ip), str(mem.port)), a)
        Smes(a, chat).send_smes_to_all()
        add_message_to_db({"chat_id": chat.chat_id, 'name': my_default_name}, a, ('0.0.0.0', PORT))


def new_f(a):
    name = input("Write name of the chat that you and members will see in the list of the chats\n")
    chat = Chat.get_or_none(name=name)
    if chat is not None:
        print('Pick another name. You have it already')
        return
    if name in ['#new', '#join', '#acc', 'chat', '#my_blocks', '#add_admin', '#block']:
        print('Pick another name for chat')
        return
    if len(name) > 100:
        print('Choose name less that 100 symbols')
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
    Member(chat=chat, ip=HOST, port=PORT, name=my_default_name, is_admin=True, approved=True).save()
    print(f"You have created the chat. Other users can join by chat_id:{chat_id}")


def join_f(a):
    chat_id = input("Write chat_id\n")
    while True:
        ip = input("Write ip of server\n")
        if not re.fullmatch(r'^((25[0-5]|(2[0-4]|1[0-9]|[1-9]|)[0-9])(\.(?!$)|$)){4}$', ip):
            print("Wrong ip. Exapmles: 172.0.0.1 or 200.200.200.200")
            continue
        break
    Smes(chat_id, Chat(name=my_default_name, chat_id=chat_id, ip=ip, port=PORT),
         type='sjoin').send_sdef_mes()


def select_chat_and_member(for_everyone, to_person):
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
    while True:
        num = input('Write number of user that you want to make admin. or "exit()" to cancel\n')
        if num == 'exit()':
            return
        elif not num.isnumeric():
            print('You should write number')
        else:
            break
    if int(num) > 0 or int(num) <= len(list_of_members):
        try:
            memb = list_of_members[int(num) - 1]
        except IndexError:
            print('Write correct data please')
            return
        mes = {"ip": memb.ip, "port": memb.port, "name": memb.name, 'data': 'is required'}
        mmm = 'data is required'
        if for_everyone == 'block':
            while True:
                date = input('Enter till when you want to block user. or "forever" to block. Format %Y-%m-%d %H:%M:%S'
                             'Example: 2021-02-15 00:00:01\n')
                if date == 'exit()':
                    return
                if date == 'forever':
                    date = datetime.datetime(3000, 10, 10, 23, 40, 10)
                try:
                    date = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
                    break
                except ValueError:
                    try:
                        date = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S.%f')
                        break
                    except ValueError:
                        print('Error. Wrong date. format: %Y-%m-%d %H:%M:%S. Try again or use exit()')
                        continue
            mmm = str(date)
            mes['data'] = str(date)
            blk = Blocked.get_or_none(member=memb)
            if blk is None:
                Blocked(member=memb, date=date).save()
                return
            blk.date = date
            blk.save()
        if for_everyone == 'add_admin':
            memb.is_admin = True
            memb.save()
        Smes(json.dumps(mes), Chat(name=chat.name, chat_id=chat.chat_id, ip=memb.ip, port=memb.port),
             type=for_everyone).send_smes_to_all()
        Smes(mmm, Chat(name=chat.name, chat_id=chat.chat_id, ip=memb.ip, port=PORT),
             type=to_person).send_smes()


def client_start():
    while True:
        print('Main menu.\nAvailable commands:\nchat *name_of_chat* - enter the chat and start messaging\n'
              '"#new" - creation a new chat\n"#join" - join existing chat\n"#add_admin" - allows to add admin'
              'to the chat\n"#block" - allows to block user in the chat\n"#my_blocks" - list of chats in which ypu '
              'are blocked\nList of available chats:')
        chats = Chat.select()
        for c in chats:
            print(f"Name:{c.name}; ip:{c.ip}; chat_id:{c.chat_id};")

        if my_default_name is None:
            print('Please setup .env file. Default parameters:\nDB_URI=db.sqlite3\nUSERNAME=user')

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
            select_chat_and_member('add_admin', 'you_is_admin')
        elif a.split()[0] == '#block':
            select_chat_and_member('block', 'you_blocked')
        elif a.split()[0] == '#my_blocks':
            ans = ''
            my_chats = Member.select().where(Member.ip == '0.0.0.0')
            for chat in my_chats:
                mem = Member.select().where(Member.ip == "0.0.0.0", Member.chat_id == chat.chat_id)
                block = Blocked.get_or_none(member=mem)
                if block is not None:
                    ans += f"Chat{chat.name}. Till {block.date}\n"
            print(ans)
        else:
            print("Couldn't understand your command")

# TODO get history
# TODO describe problem and solution for chat_is changes and history loses
