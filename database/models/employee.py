from peewee import Model, CharField, DateTimeField, BigIntegerField, AutoField

class Employee(Model):
    id = AutoField(primary_key=True) 
    full_name = CharField(null=False)
    birthday = DateTimeField(null=False)
    tg_id = BigIntegerField(unique=True)
