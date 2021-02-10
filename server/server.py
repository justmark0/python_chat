import asyncio
import socket
from .handle import handle_requests


class Server(object):

    def __init__(self, hostname, port):
        self.event_loop = asyncio.get_event_loop()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.hostname = hostname
        self.port = port

    def start(self):
        asyncio.run(self.astart())

    async def astart(self):
        self.socket.bind((self.hostname, self.port))
        self.socket.listen(10)

        while True:
            conn, address = self.socket.accept()
            data = conn.recv(1024).decode('utf-8')
            if data == "":
                continue
            else:
                task1 = asyncio.create_task(handle_requests(data))


# TODO систему поддержания соединений (если один отключился, то через время его спросить, если нет ответа отсоеденить)
# TODO Encryption
# TODO registration
# TODO decentralization
