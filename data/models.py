from peewee import Model, CharField, SqliteDatabase, ForeignKeyField, BooleanField, DateTimeField
from .config import max_symbols_in_message
import datetime
db = SqliteDatabase("db.sqlite3")


class Key(Model):
    ip = CharField(max_length=15)
    port = CharField(max_length=5)
    priv_key = CharField(null=True, max_length=1024)
    pub_key = CharField(max_length=1024)

    class Meta:
        database = db


class Chat(Model):
    name = CharField(max_length=100, unique=True)
    chat_id = CharField(max_length=512)
    ip = CharField(max_length=15)
    port = CharField(max_length=5)
    chat_id_changeable = BooleanField(default=False)

    class Meta:
        database = db


class Member(Model):
    chat = ForeignKeyField(Chat, backref='members')
    ip = CharField(max_length=15)
    port = CharField(max_length=5)
    name = CharField(max_length=50)
    is_admin = BooleanField(default=False)
    approved = BooleanField(default=False)

    class Meta:
        database = db


class Message(Model):
    chat = ForeignKeyField(Chat, backref='messages')
    member = ForeignKeyField(Member, backref='messages')
    content = CharField(max_length=max_symbols_in_message)
    date = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = db


class Blocked(Model):
    member = ForeignKeyField(Member, backref='')
    date = DateTimeField()

    class Meta:
        database = db
