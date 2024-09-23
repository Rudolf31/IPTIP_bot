from peewee import Model, BooleanField, BigIntegerField

class User(Model):
    id = BigIntegerField(primary_key=True) 
    tg_id = BigIntegerField(unique=True, null=False)
    admin = BooleanField(default=False)