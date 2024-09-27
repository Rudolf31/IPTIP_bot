from peewee import Model, BigIntegerField, ForeignKeyField, AutoField
from .user import User

class Subscriber(Model):
    id = AutoField(primary_key=True) 
    user_id = ForeignKeyField(User, field='id', unique=True)