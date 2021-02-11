from data.config import HOST, PORT
from data.send import *
from data.models import Chat


def client_start():
    Chat.get_or_create(name='1', chat_id='randomsymbols1', ip=HOST, port=PORT)

    while True:
        print('Main menu.\nWrite: "chat *name of chat*" to enter to the existing one. Or create new one by typing '
              '"#new *ip* *port*".To exit from chat type: "exit()". To send message without encryption write with '
              'message: "ne:*message*"\nList of available chats:')
        chats = Chat.select()
        for c in chats:
            print(f"Name:{c.name}; ip:{c.ip}; port:{c.port}; chat_id{c.chat_id};")

        #a = input()
        a = 'chat 1'  # for testing
        if a.split()[0] == "chat":
            chat = Chat.get_or_none(name=a.split()[1])
            if chat is not None:
                print(f'You entered chat "{a}".')
                while True:
                    a = input()
                    if a == "exit()":
                        break
                    if a.split(":")[0] == 'ne':  # Not encrypted message
                        send_mes(chat, a)
                    ssend(chat, a)
            else:
                print("Couldn't find this chat")
        elif a.split()[0] == 'new':
            pass  # TODO add chat creation
        # TODO add my name to new chat
        else:
            print("Couldn't understand your command")
