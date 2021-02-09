import server
import client
from multiprocessing import Process

proc = Process(target=server.server_start)
proc.start()
client.client_start()
