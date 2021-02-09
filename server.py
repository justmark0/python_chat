import socket


def server_start(port=4702):
    sock = socket.socket()
    sock.bind(('', port))
    sock.listen(1)  # queue length
    print("Server is started")
    conn, addr = sock.accept()

    while True:
        data = conn.recv(1024)
        if not data:
            break
        print(f"Server received data:{data.decode('utf-8')}")
        if data == b"exit()":
            conn.close()
            break

        conn.send(data.upper())

# TODO систему поддержания соединений (если один отключился, то через время его спросить, если нет ответа отсоеденить)
# TODO Encryption
# TODO registration
# TODO decentralization
