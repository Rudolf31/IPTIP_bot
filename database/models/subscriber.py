from peewee import Model, BigIntegerField, ForeignKeyField
from user import User

class Subscriber(Model):
    id = BigIntegerField(primary_key=True, autoincrement=True)
    user_id = ForeignKeyField(User, field='id', unique=True)