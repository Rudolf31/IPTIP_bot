from peewee import Model, BooleanField, BigIntegerField

class Reminder(Model):
    id = BigIntegerField(primary_key=True, autoincrement=True) 
    user_id = ForeignKeyField(User, field='id', unique=True)
    employee_id = ForeignKeyField(Empoloyee, field='id', unique=True)