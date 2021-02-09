import socket


def client_start():
    a = input("1 - open connection (exit() - exit)\n")
    if a == '1':
        sock = socket.socket()
        sock.connect(('localhost', 4702))
        print("Connection established. Type messages:")
        while True:
            mes = input()
            sock.send(mes.encode('utf-8'))
            if mes == "exit()":
                break

        sock.close()

