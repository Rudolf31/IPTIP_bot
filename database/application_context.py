from peewee import SqliteDatabase
from config import DATABASE
from database.models.user import User
from database.models.employee import Employee
from database.models.reminder import Reminder
from database.models.subscriber import Subscriber


class AppContext:
    def __init__(self):
        self.database = SqliteDatabase(DATABASE)

    async def __aenter__(self):
        
        self.database.connect()
        
        await self.database.create_tables([User,   Subscriber], safe=True)
        return self.database

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        
        self.database.close()