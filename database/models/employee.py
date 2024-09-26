from peewee import Model, CharField, DateTimeField, BigIntegerField

class Employee(Model):
    id = BigIntegerField(primary_key=True, autoincrement=True)
    full_name = CharField(null=False)
    birthday = DateTimeField(null=False)
    tg_id = BigIntegerField(unique=True)
