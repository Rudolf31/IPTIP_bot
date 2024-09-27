from peewee import Model, BooleanField, BigIntegerField, AutoField

class User(Model):
    id = AutoField(primary_key=True) 
    tg_id = BigIntegerField(unique=True, null=False)
    admin = BooleanField(default=False)