from peewee import Model, CharField, DateTimeField, BigIntegerField
from User import id

class Subscriber(Model):
    id = BigIntegerField(primary_key=True, autoincrement=True)
    
