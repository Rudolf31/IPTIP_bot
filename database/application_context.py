from peewee import SqliteDatabase, SQL
from peewee import Model, CharField, DateTimeField, BigIntegerField
from peewee import AutoField, ForeignKeyField, BooleanField

from config import DATABASE


sqlite_db = SqliteDatabase(DATABASE)


class BaseModel(Model):
    """
    BaseModel responsible for metadata
    """
    class Meta:
        database = sqlite_db


class User(BaseModel):
    """
    User table, representing registered users on Telegram
    """
    id = AutoField(primary_key=True)
    tg_id = BigIntegerField(unique=True, null=False)
    admin = BooleanField(default=False)


class Employee(BaseModel):
    """
    Employee table, representing employees working at the department.
    Mainly serves for retaining birthday data.
    """
    id = AutoField(primary_key=True)
    full_name = CharField(null=False)
    birthday = DateTimeField(null=False)
    tg_id = BigIntegerField(unique=True, null=True)  # Telegram id when available
    scheduled_reminder = DateTimeField(null=True)  # Time of next reminder


class Reminder(BaseModel):
    """
    Reminder table, representing extra birthday reminders that a subscriber
    can request for the birthday of a particular employee.
    """
    id = AutoField(primary_key=True)
    user = ForeignKeyField(User, field='id', backref='user')
    employee = ForeignKeyField(Employee, field='id', backref='employee')

    class Meta:
        constraints = [SQL('UNIQUE (user, employee)')]


class Subscriber(BaseModel):
    """
    Subscriber table, representing users who agreed to receive birthday
    reminders.
    """
    id = AutoField(primary_key=True)
    user = ForeignKeyField(User, field='id', unique=True, backref='user')


class AppContext:
    """
    AppContext is a context manager that provides access to the database.
    Initializes database and safely creates required tables on connection.

    Returns the database object via the context manager protocol.
    """

    _db = None

    def __init__(self):

        self._db = SqliteDatabase(DATABASE)

    async def __aenter__(self) -> SqliteDatabase:
        self._db.connect()
        with self._db.atomic():
            self._db.create_tables([User, Employee, Reminder, Subscriber], safe=True)
        return self._db

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self._db.close()
