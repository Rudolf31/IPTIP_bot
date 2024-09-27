from peewee import SqliteDatabase
from peewee import Model, CharField, DateTimeField, BigIntegerField
from peewee import AutoField, ForeignKeyField, BooleanField

from config import DATABASE


sqlite_db = SqliteDatabase(DATABASE)


class BaseModel(Model):
    class Meta:
        database = sqlite_db


class User(BaseModel):
    id = AutoField(primary_key=True)
    tg_id = BigIntegerField(unique=True, null=False)
    admin = BooleanField(default=False)


class Employee(BaseModel):
    id = AutoField(primary_key=True)
    full_name = CharField(null=False)
    birthday = DateTimeField(null=False)
    tg_id = BigIntegerField(unique=True)


class Reminder(BaseModel):
    id = AutoField(primary_key=True)
    user = ForeignKeyField(User, field='id', backref='user')
    employee = ForeignKeyField(Employee, field='id', backref='employee')

    # TODO: make pair unique constraint for user and employee


class Subscriber(BaseModel):
    id = AutoField(primary_key=True)
    user = ForeignKeyField(User, field='id', unique=True, backref='user')


class DbContext:
    def __init__(self):
        sqlite_db.connect()
        sqlite_db.create_tables([User, Employee, Reminder, Subscriber])

    def __del__(self):
        sqlite_db.close()
