from .server import Server
from data.config import *
import logging
import datetime


def server_start():
    serv = Server(HOST, PORT)
    logging.info(f'[{datetime.datetime.now()}]Server started')
    serv.start()
