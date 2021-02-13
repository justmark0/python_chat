from .rsa_functions import *
from .models import *
from .config import *
import json


def divide_into_chunks(mes, length):
    m_cpy = mes[::]
    if len(m_cpy) > length:
        chunks = []
        while m_cpy != "":
            a = m_cpy[:length:]
            chunks.append(a)
            m_cpy = m_cpy[length::]
        return chunks
    return [m_cpy]


def chunk_mes_and_enc(mes_l, host_key_pub):
    chunks = divide_into_chunks(mes_l, rsa_max_length[str(RSA_KEY_LENGTH)])
    data_lst = []
    for i in range(len(chunks)):
        data_lst.append((rsa.encrypt(chunks[i].encode('utf-8'), host_key_pub)).hex())
        return data_lst


class Smes:  # Secure message

    def __init__(self, message: str, chat: Chat, type='smes'):
        self.mes = message
        self.chat = chat
        self.type = type
        self.addr = (chat.ip, chat.port)

    def verification_and_hostpub(self):
        host_key = get_rsa_key(self.addr)
        host_key_pub = get_rsa_pub_from_str(host_key.pub_key)
        my_priv = get_rsa_priv_from_str(host_key.priv_key)
        hash_local = rsa.compute_hash(self.mes.encode('utf-8'), 'SHA-1')
        signature = rsa.sign_hash(hash_local, my_priv, 'SHA-1').hex()
        return signature, host_key_pub

    def base_info(self, mes_l):
        signature, host_key_pub = self.verification_and_hostpub()
        data = {"type": self.type, 'sign': signature, 'data': chunk_mes_and_enc(mes_l, host_key_pub),
                'name': my_default_name}
        return data

    def send_smes(self):
        messages = divide_into_chunks(self.mes, max_symbols_in_message)
        for dmes in messages:
            data = self.base_info(dmes)
            data['chat_id'] = self.chat.chat_id
            send(self.addr, json.dumps(data))

    def send_smes_to_all(self):
        members = Member.select().where(Member.chat == Chat.get(chat_id=self.chat.chat_id))
        for mem in members:
            # if mem.ip == '0.0.0.0':  # TODO uncomment it
            #     continue
            Smes(self.mes, Chat(name=self.chat.name, chat_id=self.chat.chat_id, ip=mem.ip, port=mem.port,
                                chat_id_changeable=self.chat.chat_id_changeable), type=self.type).send_smes()

    def send_sdef_mes(self):
        data = self.base_info(self.mes)
        send(self.addr, json.dumps(data))

    def send_sjoin_acc_mes(self, chat_name):
        data = self.base_info(self.mes)
        data['chat_name'] = chat_name
        data['chat_id_changeable'] = self.chat.chat_id_changeable
        send(self.addr, json.dumps(data))
