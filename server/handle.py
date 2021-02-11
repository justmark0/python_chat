from data.send import send, get_my_rsa
from data.models import Key
import json
import rsa


async def handle_requests(message, addr):
    data = json.loads(message)
    print(data)
    if data["type"] == 'mes':
        print(f"You received message in chat {data['chat_id']} from {data['name']}. Content is: {data['data']}")

    elif data["type"] == 'get_pub_key':
        mes = {"type": "pub_key", "data": str(get_my_rsa().pub_key)}
        send(addr, json.dumps(mes))

    elif data["type"] == 'pub_key':
        mes: dict = json.loads(message)
        if 'data' not in mes.keys():
            return
        ip, port = addr
        Key(ip=ip, port=port, pub_key=mes["data"]).save()

    elif data['type'] == 'smes':
        my = get_my_rsa()
        n = int(my.priv_key.split(",")[0].split("(")[1])
        e = int(my.priv_key.split()[1][:-1:])
        d = int(my.priv_key.split()[2][:-1:])
        p = int(my.priv_key.split()[3][:-1:])
        q = int(my.priv_key.split()[4][:-1:])
        mess = rsa.decrypt(bytes.fromhex(data['data']), rsa.PrivateKey(n, e, d, p, q)).decode('utf-8')
        print(f"[encrypted] You received message in chat {data['chat_id']} from {data['name']}. Content is: {mess}")
