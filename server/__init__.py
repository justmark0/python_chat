from .server import Server

HOST = "0.0.0.0"
PORT = 4702


def server_start():
    serv = Server(HOST, PORT)
    print('start')
    serv.start()