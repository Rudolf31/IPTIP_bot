from peewee import Model, BigIntegerField, ForeignKeyField
from user import User
from employee import Employee


class Reminder(Model):
    id = BigIntegerField(primary_key=True, autoincrement=True) 
    user_id = ForeignKeyField(User, field='id', unique=True)
    employee_id = ForeignKeyField(Employee, field='id', unique=True)