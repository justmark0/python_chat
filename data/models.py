from peewee import Model, CharField, SqliteDatabase

db = SqliteDatabase("db.sqlite3")


class Key(Model):
    ip = CharField(max_length=15)
    port = CharField(max_length=5)
    priv_key = CharField(null=True, max_length=1024)
    pub_key = CharField(max_length=1024)

    class Meta:
        database = db


class Chat(Model):
    name = CharField(max_length=100)
    my_name = CharField(max_length=100, null=True)
    chat_id = CharField(max_length=512)
    ip = CharField(max_length=15)
    port = CharField(max_length=5)

    class Meta:
        database = db


# class Account(Model):
#     pass
#
#
# class Message(Model):
#     pass
