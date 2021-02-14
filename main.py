from multiprocessing import Process
import logging
import client
import server
import time

if __name__ == '__main__':
    try:
        logging.basicConfig(filename='chat.log', encoding='utf-8', level=logging.DEBUG)
    except ValueError:
        logging.basicConfig(filename='chat.log', level=logging.DEBUG)
    proc = Process(target=server.server_start)
    proc.start()
    time.sleep(0.1)
    client.client_start()
