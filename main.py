from multiprocessing import Process
import client
import server
import time

proc = Process(target=server.server_start)
proc.start()
time.sleep(0.1)
client.client_start()
