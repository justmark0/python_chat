from data.send import send, get_my_rsa, get_rsa_priv_from_str
from data.models import Key
import json
import rsa


async def handle_requests(message, addr):
    try:
        data = json.loads(message)
    except json.decoder.JSONDecodeError:
        send(addr, "Error: could't parse json")
        print(f"[date] Error: could't parse json from {addr}. ")  # TODO logging
        return
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
        mess = ""
        my = get_rsa_priv_from_str(get_my_rsa().priv_key)
        for ms in data['data']:
            mess += rsa.decrypt(bytes.fromhex(ms), my).decode('utf-8')
        print(f"[encrypted] You received message in chat {data['chat_id']} from {data['name']}. Content is: {mess}")
