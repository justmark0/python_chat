import asyncio
import socket
from .handle import handle_requests


class Server:

    def __init__(self, hostname, port):
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
            data = conn.recv(4096).decode('utf-8')
            if data == "":
                continue
            else:
                task1 = asyncio.create_task(handle_requests(data, address))
                await task1  # TODO make it real async or just call handler


# TODO систему поддержания соединений (если один отключился, то через время его спросить, если нет ответа отсоеденить)
# TODO Encryption
# TODO registration
# TODO decentralization
# TODO Add logging
