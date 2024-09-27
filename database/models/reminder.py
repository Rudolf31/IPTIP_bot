from peewee import Model, BigIntegerField, ForeignKeyField, AutoField
from .user import User
from .employee import Employee


class Reminder(Model):
    id = AutoField(primary_key=True) 
    user_id = ForeignKeyField(User, field='id', unique=True)
    employee_id = ForeignKeyField(Employee, field='id', unique=True)