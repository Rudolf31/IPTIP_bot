from peewee import Model, CharField, DateTimeField, BigIntegerField

class employee(Model):
    id = BigIntegerField(primary_key=True)
    full_name = CharField(null=False)
    birthday = DateTimeField(null=False)
    tg_id = BigIntegerField(unique=True)
