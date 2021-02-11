from peewee import SqliteDatabase
from data.config import DB_URI
from data.models import *

db = SqliteDatabase(DB_URI)
db.create_tables([Key, Chat])
